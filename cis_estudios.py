"""
Clases para análisis de estudios del CIS.
Arquitectura modular para diferentes tipos de estudios electorales.
"""

import pandas as pd
import os
import re
from abc import ABC, abstractmethod


class EstudioCIS(ABC):
    """Clase base abstracta para todos los estudios del CIS."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.excel_file = pd.ExcelFile(file_path)
        self.sheet_names = self.excel_file.sheet_names
        self._cache = {}
        self._inferred_data = None

    def _infer_context(self) -> dict:
        """Infiere métricas clave del estudio a partir de los cruces de datos."""
        if self._inferred_data:
            return self._inferred_data
            
        metrics = {
            'ruralidad': self._extraer_metricas_rurales(),
            'polarizacion': self._extraer_metricas_ideologicas(),
            'transvases_potenciales': self._extraer_segunda_opcion(),
            'sesgo_recuerdo': self._extraer_bias_recuerdo()
        }
        self._inferred_data = metrics
        return metrics

    # Referencias históricas fijas para detección de sesgos (Memory Baseline)
    VOTO_HISTORICO_2023 = {
        'NACIONAL': {'PP': 33.1, 'PSOE': 31.7, 'VOX': 12.4, 'SUMAR': 12.3, 'PODEMOS': 3.3},
        'ARAGON': {'PP': 35.6, 'PSOE': 27.3, 'VOX': 11.2, 'CHA': 5.8, 'PODEMOS': 2.1},
        'EXTREMADURA': {'PP': 38.8, 'PSOE': 39.9, 'VOX': 8.1, 'PODEMOS': 6.0}
    }

    def _extraer_bias_recuerdo(self) -> dict:
        """Compara el recuerdo con el histórico real del año del recuerdo (2023)."""
        recuerdo = self.extraer_recuerdo_voto()
        # Determinar territorio para el histórico
        territorio = 'NACIONAL'
        if hasattr(self, 'comunidad'): territorio = self.comunidad
        
        hist_ref = self.VOTO_HISTORICO_2023.get(territorio, self.VOTO_HISTORICO_2023['NACIONAL'])
        
        sum_rec = sum(recuerdo.values())
        if sum_rec == 0: return {}
        
        biases = {}
        for p, ref_val in hist_ref.items():
            rec_val = (recuerdo.get(p, 0) / sum_rec) * 100
            if rec_val > 0 and ref_val > 0:
                # Ratio > 1: Sobre-representación (Sesgo de deseabilidad)
                biases[p] = round(rec_val / ref_val, 2)
        return biases

    def get_context_biases(self) -> dict:
        """
        Define sesgos fidelidad, transvases y justificación experta.
        Genera los coeficientes dinámicamente según la sociología del estudio.
        """
        ctx = self._infer_context()
        rur = ctx['ruralidad']
        pol = ctx['polarizacion']
        rec_bias = ctx.get('sesgo_recuerdo', {})
        
        # 1. Coeficientes de fidelidad dinámicos (Expert Rules + Sensed Data)
        # El PSOE resiste mejor en zonas rurales (rur > 0.45)
        fid_psoe = 0.90 + (min(0.08, (rur - 0.4) * 0.4) if rur > 0.4 else -0.05)
        
        # 2. Corrección por Sesgo de Recuerdo (Recall Bias) - Aldabón-Gemini 2.4
        # Si el PSOE está muy inflado en el recuerdo, bajamos su fidelidad
        psoe_bias = rec_bias.get('PSOE', 1.0)
        psoe_correction = 0
        if psoe_bias > 1.15: # Solo si el sesgo es evidente (>15%)
            psoe_correction = min(0.15, (psoe_bias - 1.15) * 0.3)
            fid_psoe -= psoe_correction
        
        # El bloque de derecha se moviliza en climas polarizados (pol > 0.5)
        clima_mov = (pol - 0.5) * 0.3
        
        # Bonus moderado por "Voto Vergonzante"
        vox_bias = rec_bias.get('VOX', 1.0)
        vox_bonus = max(0, (1.0 - vox_bias) * 0.3) if vox_bias < 0.9 else 0

        fid_pp = 1.05 + max(0.0, clima_mov * 0.5)
        fid_vox = 1.10 + max(0.0, clima_mov * 0.7) + vox_bonus
        
        biases = {
            'fidelidad': {
                'PSOE': round(fid_psoe, 2),
                'PP': round(fid_pp, 2),
                'VOX': round(fid_vox, 2),
                'SUMAR': 0.85, 
                'PODEMOS': round(1.10 + max(0.0, clima_mov * 0.2), 2),
                'SALF': 1.10,
                'En Blanco': 1.0, 'Voto Nulo': 1.0
            },
            'transvases': {
                'PSOE': {'PODEMOS': 0.08, 'SUMAR': 0.10, 'En Blanco': 0.05},
                'PP': {'VOX': 0.05},
                'VOX': {'PP': 0.10}
            },
            'justificacion': {
                'Diagnóstico Sociológico': f"Clima: {'Rural' if rur > 0.45 else 'Urbano/Moderado'}. Polarización: {'Alta' if pol > 0.6 else 'Baja'}.",
                'Sesgo de Muestra': f"Recall PSOE: {'Normal' if psoe_bias < 1.15 else f'Inflado (x{psoe_bias:.2f})'}. " + 
                                   (f"Voto oculto VOX detectado (+{vox_bonus:.2f})." if vox_bonus > 0 else "Representatividad correcta de la derecha.")
            }
        }
        
        # 2. Integrar segundas opciones detectadas como voto refugio (opcional)
        segundas = ctx['transvases_potenciales'].get('GLOBAL', {})
        if segundas:
             for p_orig in ['PSOE', 'PP', 'VOX', 'SUMAR', 'PODEMOS']:
                if p_orig not in biases['transvases']: biases['transvases'][p_orig] = {}
                for p_dest, peso in segundas.items():
                    if p_dest != p_orig:
                        biases['transvases'][p_orig][p_dest] = biases['transvases'][p_orig].get(p_dest, 0) + (peso * 0.15)
                
        return biases
    
    @abstractmethod
    def get_partidos_referencia(self) -> dict:
        """Retorna diccionario de partidos con sus resultados reales de referencia."""
        pass
    
    @abstractmethod
    def get_hoja_rv(self) -> str:
        """Retorna el nombre de la hoja de Recuerdo de Voto a usar."""
        pass
    
    def _extraer_metricas_rurales(self) -> float:
        """Calcula el peso de municipios pequeños (<10k hab) usando el total del estudio."""
        sheet = self._encontrar_hoja('TAMAÑO DE MUNICIPIO')
        if not sheet: return 0.3
        try:
            df = pd.read_excel(self.file_path, sheet_name=sheet, header=None)
            for i in range(min(100, len(df))):
                cell_val = str(df.iloc[i, 0]).upper()
                if '(N)' in cell_val:
                    row = df.iloc[i]
                    total = self._try_float(row.iloc[1])
                    if total > 500:
                        rural = self._try_float(row.iloc[2]) + self._try_float(row.iloc[3])
                        return rural / total if total > 0 else 0.3
        except: pass
        return 0.3

    def _extraer_metricas_ideologicas(self) -> float:
        """Infiere polarización (peso de extremos 1-2 y 9-10) en la escala 1-10."""
        sheet = self._encontrar_hoja('IDEOLOGÍA')
        if not sheet: return 0.5
        try:
            df = pd.read_excel(self.file_path, sheet_name=sheet, header=None)
            for i in range(min(100, len(df))):
                row_str = [str(x) for x in df.iloc[i].tolist()]
                if any('1 Izquierda' in x for x in row_str):
                    for k in range(i + 1, i + 20):
                        if k >= len(df): break
                        if '(N)' in str(df.iloc[k, 0]):
                            n_row = df.iloc[k]
                            total = self._try_float(n_row.iloc[1])
                            if total > 500:
                                # Extremos: 1-2 (cols 2,3) y 9-10 (cols 10,11)
                                extremos = sum(self._try_float(n_row.iloc[c]) for c in [2, 3, 10, 11])
                                return extremos / total if total > 0 else 0.5
        except: pass
        return 0.5

    def _extraer_segunda_opcion(self) -> dict:
        """Extrae transvases potenciales de la pregunta de segunda opción (P12)."""
        sheet = self._encontrar_hoja('RESULTADOS') or self._encontrar_hoja('VOTO DIRECTO')
        if not sheet: return {}
        try:
            df = pd.read_excel(self.file_path, sheet_name=sheet, header=None)
            found_p12 = False
            transvases = {}
            for i in range(len(df)):
                cell_val = str(df.iloc[i, 0]).upper()
                if 'SEGUNDA OPCION' in cell_val or 'P12' in cell_val or 'PREGUNTA 12' in cell_val:
                    found_p12 = True
                    continue
                if found_p12:
                    if '(N)' in cell_val or 'PREGUNTA' in cell_val: 
                        if transvases: break
                        continue
                    p_key = self._normalizar_partido(df.iloc[i, 0])
                    val = self._try_float(df.iloc[i, 1])
                    if p_key and val > 0:
                        transvases[p_key] = val / 100.0
            return {'GLOBAL': transvases} if transvases else {}
        except: pass
        return {}

    def _encontrar_hoja(self, keyword: str) -> str:
        """Busca una hoja por palabra clave usando normalización difusa."""
        norm_key = self._fuzzy_normalize(keyword)
        for s in self.sheet_names:
            if norm_key in self._fuzzy_normalize(s):
                return s
        return None

    def _try_float(self, val) -> float:
        """Conversión robusta a float para formatos de texto CIS."""
        try:
            if pd.isna(val) or val == 'nan' or val == '': return 0.0
            if isinstance(val, (int, float)): return float(val)
            s = str(val).strip()
            # Manejo de formatos España: 3.312,99 -> 3312.99
            if '.' in s and ',' in s: s = s.replace('.', '').replace(',', '.')
            elif ',' in s: s = s.replace(',', '.')
            s = re.sub(r'[^0-9.]', '', s)
            return float(s) if s else 0.0
        except: return 0.0

    def _fuzzy_normalize(self, text: str) -> str:
        """Normaliza texto eliminando acentos, caracteres raros y espacios."""
        if not text or not isinstance(text, str): return ""
        t = text.upper()
        t = t.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
        t = t.replace('Ñ', 'N').replace('±', 'N').replace('Ï', 'I').replace('¾', 'O').replace('Ë', 'O').replace('Ý', 'I').replace('═', 'O')
        t = re.sub(r'[^A-Z0-9]', '', t)
        return t

    def extraer_ficha_tecnica(self) -> dict:
        """Extrae las características técnicas del sondeo desde la hoja Ficha técnica."""
        import re
        
        ficha = {
            'referencia': 'N/A',
            'n': 'N/A',
            'campo': 'N/A',
            'ambito': 'N/A',
            'tipo': type(self).__name__
        }
        
        # Buscar hoja de ficha técnica
        hoja_ficha = None
        for sheet in self.sheet_names:
            if 'ficha' in sheet.lower():
                hoja_ficha = sheet
                break
        
        if not hoja_ficha:
            return ficha
        
        try:
            df = pd.read_excel(self.excel_file, sheet_name=hoja_ficha, header=None)
            
            # Buscar en todas las celdas
            for i in range(min(20, len(df))):
                for j in range(min(4, len(df.columns))):
                    cell = str(df.iloc[i, j]) if pd.notna(df.iloc[i, j]) else ""
                    cell_upper = cell.upper()
                    
                    # Buscar número de estudio (formato XXXX/X o solo XXXX)
                    if ficha['referencia'] == 'N/A':
                        match = re.search(r'\b(35\d{2}/?\d?)\b', cell)
                        if match:
                            ficha['referencia'] = match.group(1)
                    
                    # Buscar número de entrevistas/muestra
                    if ficha['n'] == 'N/A':
                        match = re.search(r'(\d+[\.,]?\d*)\s*entrevistas', cell, re.IGNORECASE)
                        if match:
                            ficha['n'] = match.group(1).replace('.', '') + ' entrevistas'
                    
                    # Buscar fechas de trabajo de campo
                    if ficha['campo'] == 'N/A':
                        # Formato: "Del 21 al 25 de noviembre de 2025" o "Del 2 al 6 de junio"
                        match = re.search(r'(?:del\s+)?(\d{1,2}(?:\s+al\s+\d{1,2})?\s+(?:de\s+)?\w+\s+(?:de\s+)?20\d{2})', cell, re.IGNORECASE)
                        if match:
                            ficha['campo'] = match.group(1).strip()
                        else:
                            # Buscar en filas adyacentes si parece que está cortado
                            if 'FECHA' in cell_upper or 'REALIZACIÓN' in cell_upper:
                                for offset in range(1, 4):
                                    if i + offset < len(df):
                                        next_val = str(df.iloc[i + offset, j])
                                        if 'DEL' in next_val.upper() or any(m in next_val.lower() for m in ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']):
                                            ficha['campo'] = next_val.strip()
                                            break
                    
                    # Buscar ámbito
                    if ficha['ambito'] == 'N/A':
                        if 'ÁMBITO' in cell_upper or 'AMBITO' in cell_upper:
                            # Buscar en la siguiente columna o en el mismo texto
                            if j + 1 < len(df.columns):
                                next_cell = str(df.iloc[i, j+1]) if pd.notna(df.iloc[i, j+1]) else ""
                                if next_cell and len(next_cell) > 2:
                                    ficha['ambito'] = next_cell.strip()
                        elif 'ARAGÓN' in cell_upper or 'ARAGON' in cell_upper:
                            ficha['ambito'] = 'Aragón'
                        elif 'NACIONAL' in cell_upper or 'ESPAÑA' in cell_upper:
                            ficha['ambito'] = 'Nacional'
                            
        except Exception as e:
            print(f"Error leyendo ficha técnica: {e}")
        
        return ficha


    
    def extraer_voto_directo(self) -> dict:
        """Extrae el Voto Directo. Busca en hoja Estimación o Resultados."""
        hoja_estim = self._encontrar_hoja_estimacion()
        if not hoja_estim:
            return {}
            
        # Si la hoja es 'Resultados', usar lógica de búsqueda por preguntas
        if 'RESULTADOS' in hoja_estim.upper():
            return self._extraer_voto_directo_desde_resultados(hoja_estim, normalizar=False)
            
        return self._extraer_columna_estimacion(col_idx=1, normalizar=False)
    
    def _extraer_estimacion_cis_pdf(self) -> dict:
        """Intenta extraer la estimación oficial desde un PDF si existe."""
        # Intentar varias combinaciones de nombres de archivo
        base = self.file_path.rsplit('.', 1)[0]
        pdf_variants = [
            base.replace('_multi_A', '').replace('-multi_A', '').replace('_multi', '').replace('-multi', '') + '_Estimacion.pdf',
            base + '_Estimacion.pdf',
            self.file_path.replace('_multi_A.xlsx', '_Estimacion.pdf').replace('-multi.xlsx', '_Estimacion.pdf').replace('_multi.xlsx', '_Estimacion.pdf')
        ]
        
        pdf_path = None
        for v in pdf_variants:
            if os.path.exists(v):
                pdf_path = v
                break
                
        if not pdf_path:
            return {}
            
        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Limpiar texto
            full_text_upper = text.upper()
            
            # Localizar el inicio de la tabla de estimación
            # El CIS suele poner "ESTIMACIÓN DE VOTO" en la página de cocina
            start_idx = full_text_upper.find("ESTIMACIÓN DE VOTO")
            if start_idx == -1:
                start_idx = full_text_upper.find("ESTIMACIÓN")
            
            search_text = text[start_idx:] if start_idx != -1 else text
            
            matches = re.findall(r'([A-ZÁÉÍÓÚÑa-záéíóúñ\s\.\-\/]{2,35})\s+(\d+(?:,\d+)?)(?:\s+[\±\▒]\s*\d+(?:,\d+)?)?\s+(\d+(?:,\d+)?)?', search_text)
            
            pdf_data = {}
            for match in matches:
                p_name = match[0].strip()
                v1 = match[1] # Voto Directo
                v2 = match[2] # Estimación (si existe)
                
                # Evitar capturar títulos
                if any(x in p_name.upper() for x in ['ESTIMACIÓN', 'CUADRO', 'FUENTE', 'CIS', 'TOTAL', 'BADAJOZ', 'CÁCERES']):
                    continue
                    
                p_key = self._normalizar_partido(p_name)
                # Permitir Blanco y Nulo en la estimación del PDF
                if not p_key or p_key in ['No Sabe', 'No Contesta', 'Abstención', 'No Votaría']:
                    continue
                
                # Si tenemos v2, esa es la estimación. Si no, v1
                p_val = v2 if v2 else v1
                val = float(p_val.replace(',', '.'))
                
                if 0.1 <= val <= 75:
                    # Nos quedamos con la PRIMERA aparición de cada partido (que es el TOTAL)
                    if p_key not in pdf_data:
                        pdf_data[p_key] = val
            
            # Si el bloque capturado es de marginales (voto muy bajo), intentar buscar más adelante
            if pdf_data.get('PSOE', 0) < 5 and 'ESTIMACIÓN DE VOTO' in search_text:
                # Reintentar saltando la primera ocurrencia si es necesario
                pass
            
            return pdf_data
        except Exception as e:
            # Silenciar errores de PDF corruptos o streams terminados si tenemos fallback
            return {}

    def _extraer_voto_directo_desde_resultados(self, hoja: str, normalizar: bool = False) -> dict:
        """Extrae Voto Directo buscando la tabla de intención de voto puramente."""
        df = pd.read_excel(self.excel_file, sheet_name=hoja, header=None)
        resultados = {}
        
        # 1. Localizar bloque de intención de voto principal
        start_row = -1
        
        # Primero buscamos patrones muy específicos de intención de voto espontánea
        for i in range(len(df)):
            cell = str(df.iloc[i, 0]).upper()
            
            # Buscamos la pregunta clásica de intención de voto
            # EXCLUIR agresivamente si menciona simpatía o suma de voto+simpatía
            # PERO permitir RECODIFICADA si no hay otra opción, ya que es el estándar moderno
            if 'VOTARÍA' in cell and ('PRÓXIMAS' in cell or 'ELECCIONES' in cell):
                if any(x in cell for x in ['SIMPATÍA', 'VOTO+', 'VOTO +']):
                    continue
                
                # Validación adicional: Que las primeras 12 filas no sean la tabla de simpatía
                is_valid = True
                for offset in range(1, 15):
                    if i + offset < len(df):
                        next_cell = str(df.iloc[i + offset, 0]).upper()
                        if any(x in next_cell for x in ['SIMPATÍA', 'VOTO+']):
                            is_valid = False
                            break
                
                if is_valid and any(self._normalizar_partido(str(df.iloc[j, 0])) for j in range(i+1, min(i+15, len(df)))):
                    start_row = i
                    break
        
        # Fallback si no se encontró la tabla pura (ej. estudios antiguos o raros)
        if start_row == -1:
            for i in range(len(df)):
                cell = str(df.iloc[i, 0]).upper()
                if 'VOTARÍA' in cell and 'PRÓXIMAS' in cell and not any(x in cell for x in ['SIMPATÍA', 'VOTO+']):
                    start_row = i
                    break
                    
        if start_row == -1: return {}
        
        # 2. Extraer hasta encontrar el final de la tabla (N)
        empty_streak = 0
        for i in range(start_row + 1, min(start_row + 60, len(df))):
            row = df.iloc[i]
            partido_raw = str(row.iloc[0]).strip()
            
            # Skip empty rows but don't break immediately
            if not partido_raw:
                empty_streak += 1
                if empty_streak > 3: break # Limitar a 3 filas vacías consecutivas
                continue
            
            empty_streak = 0
            
            # Fin de la tabla (N) o próxima pregunta
            if '(N)' in partido_raw.upper() or (len(partido_raw) > 50 and partido_raw.isupper()):
                break
            
            # Obtener clave (normalizada o categoría especial)
            p_key = self._normalizar_partido(partido_raw)
            if not p_key:
                p_up = partido_raw.upper()
                if 'SABE' in p_up or 'N.S.' in p_up: p_key = 'No Sabe'
                elif 'CONTESTA' in p_up or 'N.C.' in p_up: p_key = 'No Contesta'
                elif 'ABSTENCI' in p_up or 'NO VOTAR' in p_up: p_key = 'Abstención'
                elif 'BLANCO' in p_up: p_key = 'En Blanco'
                elif 'NULO' in p_up: p_key = 'Voto Nulo'
                elif 'OTRO' in p_up: p_key = 'OTROS'
                else: continue
            
            # Extraer y ACUMULAR (especialmente para OTROS)
            val = self._try_float(row.iloc[1])
            if val is not None and 0.05 <= val <= 99:
                resultados[p_key] = resultados.get(p_key, 0.0) + val
        
        return resultados
    
    def extraer_estimacion_cis(self) -> dict:
        """Extrae la Estimación del CIS. 
        Intenta PDF primero, luego diferentes hojas de Excel."""
        
        # 1. Intentar PDF primero (siempre es lo más fiable)
        pdf_data = self._extraer_estimacion_cis_pdf()
        if pdf_data:
            return pdf_data
            
        # 2. Intentar Excel
        hoja_estim = self._encontrar_hoja_estimacion()
        if not hoja_estim:
            return {}
            
        # Si estamos en una hoja de Resultados (común en autonómicas), 
        # la estimación suele estar en la columna 3 del mismo bloque
        if 'RESULTADOS' in hoja_estim.upper():
             return self._extraer_columna_estimacion_desde_resultados(hoja_estim, col_idx=3)
             
        return self._extraer_columna_estimacion(col_idx=3)

    def _extraer_columna_estimacion_desde_resultados(self, hoja: str, col_idx: int) -> dict:
        """Extrae estimación cuando está en una columna de la tabla de resultados."""
        df = pd.read_excel(self.excel_file, sheet_name=hoja, header=None)
        
        # Buscar el bloque de RECODIFICADA o SIMPATÍA o VOTO+SIMPATÍA
        start_row = -1
        for i in range(len(df)):
            cell = str(df.iloc[i, 0]).upper()
            if 'ESTIMACIÓN' in cell or 'RECODIFICADA' in cell or 'SIMPATÍA' in cell or 'VOTO+SIMPATÍA' in cell:
                # Verificar si tiene datos numéricos en las filas siguientes
                val = self._try_float(df.iloc[i+1, col_idx])
                if val is None: val = self._try_float(df.iloc[i+2, col_idx])
                if val is not None:
                    start_row = i
                    break
        
        if start_row == -1: return {}
        
        resultados = {}
        for i in range(start_row + 1, min(start_row + 50, len(df))):
            row = df.iloc[i]
            partido_raw = str(row.iloc[0]).strip()
            if '(N)' in partido_raw.upper() or not partido_raw: break
            
            partido_key = self._normalizar_partido(partido_raw)
            if partido_key:
                valor = self._try_float(row.iloc[col_idx])
                if valor: resultados[partido_key] = valor
        return resultados
    
    def _extraer_columna_estimacion(self, col_idx: int, normalizar: bool = True) -> dict:
        """Extrae datos de una columna específica de la hoja Estimación.
        
        Args:
            col_idx: Índice de columna a extraer (1=Voto Directo, 3=Estimación CIS)
            normalizar: Si True, normaliza los resultados para que sumen 100%
        """
        hoja_estim = self._encontrar_hoja_estimacion()
        if not hoja_estim:
            return {}
        
        df = pd.read_excel(self.excel_file, sheet_name=hoja_estim, header=None)
        resultados = {}
        
        # Categorías técnicas a ignorar (no son opciones de voto)
        ignorar = ['NAN', 'REFERENCIA', 'FICHA', 'METODO', 'TRABAJO', 'MUESTRA', 'AMBITO', '(N)', 'ESCAÑOS', 'INTERVALO', 'MARGEN']
        
        # Diccionario de categorías especiales para normalización rápida
        cat_map = {
            'BLANCO': 'En Blanco',
            'NULO': 'Voto Nulo',
            'SABE': 'No Sabe',
            'CONTESTA': 'No Contesta',
            'ABSTENCI': 'Abstención',
            'OTROS': 'OTROS'
        }
        
        # Buscar en más filas (hasta 65) para no perder el final de la tabla
        for i in range(min(65, len(df))):
            row = df.iloc[i]
            
            if len(row) <= col_idx or not pd.notna(row.iloc[0]):
                continue
                
            partido_raw = str(row.iloc[0]).strip()
            partido_upper = partido_raw.upper()
            
            if not partido_raw or len(partido_raw) < 2:
                continue
            
            # Solo ignorar si no es una categoría de voto
            if any(ig in partido_upper for ig in ignorar):
                # Pero si es Blanco/Nulo, NO ignorar aunque diga "Voto"
                if not any(cat in partido_upper for cat in ['BLANCO', 'NULO']):
                    continue
            
            valor = self._try_float(row.iloc[col_idx])
            if valor is None:
                continue
            
            # Intentar normalizar como partido
            partido_key = self._normalizar_partido(partido_raw)
            
            # Si no es partido, intentar como categoría especial
            if not partido_key:
                for pat, key in cat_map.items():
                    if pat in partido_upper:
                        partido_key = key
                        break
            
            if not partido_key:
                continue
            
            # Solo guardar si el valor es razonable (0-100)
            if 0 <= valor <= 100:
                # Evitar duplicados, preferir valores de zona principal (filas 8-25)
                if partido_key not in resultados or (8 <= i <= 25):
                    resultados[partido_key] = valor
        
        # Normalizar a 100% si se solicita
        if normalizar and resultados:
            total = sum(resultados.values())
            if total > 0 and abs(total - 100) > 1:  # Solo normalizar si difiere de 100
                resultados = {p: round(v * 100 / total, 1) for p, v in resultados.items()}
        
        return resultados


    
    def _fuzzy_normalize(self, text: str) -> str:
        """Normaliza texto eliminando acentos, caracteres raros y espacios."""
        if not text: return ""
        t = text.upper()
        # Eliminar caracteres raros de codificación (común en Excel del CIS)
        t = re.sub(r'[Ë¾Ý═]', 'O', t) # ¾ y Ë suelen ser Ó, Ý es Í, etc.
        # Eliminar acentos estándar
        t = t.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U').replace('Ñ', 'N')
        # Eliminar todo lo que no sea A-Z
        t = re.sub(r'[^A-Z]', '', t)
        return t

    def _encontrar_hoja_estimacion(self) -> str:
        """Encuentra la hoja de Estimación usando lógica difusa para evitar fallos de codificación."""
        sheets = self.sheet_names
        
        # 1. Prioridad: 'ESTIMACION DE VOTO' (Fuzzy)
        for s in sheets:
            if 'ESTIMACIONDEVOTO' in self._fuzzy_normalize(s):
                return s
                
        # 2. Prioridad: 'ESTIMACION' (Fuzzy exacto o casi)
        for s in sheets:
            norm = self._fuzzy_normalize(s)
            if norm == 'ESTIMACION':
                return s
        
        # 3. Prioridad: Resultados [Comunidad] (Fuzzy)
        if hasattr(self, 'comunidad'):
            com_norm = self._fuzzy_normalize(self.comunidad)
            for s in sheets:
                s_norm = self._fuzzy_normalize(s)
                if 'RESULTADOS' in s_norm and com_norm in s_norm:
                    return s
        
        # 4. Fallback: Cualquier cosa que diga RESULTADOS
        for s in sheets:
            if 'RESULTADOS' in self._fuzzy_normalize(s):
                return s
                
        # 5. Last resort: Cualquier cosa que diga ESTIMACION
        for s in sheets:
            if 'ESTIMACION' in self._fuzzy_normalize(s):
                return s
                
        return None
    
    def _normalizar_partido(self, nombre: str) -> str:
        """Normaliza el nombre de un partido para usarlo como clave."""
        if not nombre or not isinstance(nombre, str):
            return ""
        
        nombre_orig = nombre
        nombre = nombre.upper().strip()
        
        # Eliminar prefijos comunes en Barómetros como números de código
        nombre = re.sub(r'^\d+\s+', '', nombre)
        
        # Mapeo de variantes a nombres canónicos
        mapeo = {
            'PSOE': 'PSOE', 'PARTIDO SOCIALISTA': 'PSOE',
            'PP': 'PP', 'PARTIDO POPULAR': 'PP',
            'VOX': 'VOX',
            'SUMAR': 'SUMAR', 'MOVIMIENTO SUMAR': 'SUMAR',
            'PODEMOS': 'PODEMOS', 'UNIDAS PODEMOS': 'PODEMOS',
            'SALF': 'SALF', 'SE ACABÓ LA FIESTA': 'SALF',
            'ERC': 'ERC', 'ESQUERRA REPUBLICANA': 'ERC',
            'JUNTS': 'JUNTS',
            'BILDU': 'BILDU', 'EH BILDU': 'BILDU',
            'PNV': 'PNV', 'EAJ-PNV': 'PNV',
            'BNG': 'BNG', 'BLOQUE NACIONALISTA': 'BNG',
            'CHA': 'CHA', 'CHUNTA': 'CHA',
            'PAR': 'PAR', 'PARTIDO ARAGONÉS': 'PAR',
            'TERUEL EXISTE': 'TERUEL EXISTE',
            'UPN': 'UPN', 'UNIÓN DEL PUEBLO NAVARRO': 'UPN',
            'CCA': 'CCA', 'COALICIÓN CANARIA': 'CCA',
            'PACMA': 'PACMA',
            'CUP': 'CUP',
            'FRENTE OBRERO': 'FRENTE OBRERO',
            'ALIANÇA CATALANA': 'ALIANÇA CATALANA',
            'EXTREMADURA UNIDA': 'EXTREMADURA UNIDA',
            'UNIDAS POR EXTREMADURA': 'PODEMOS',
            'PODEMOS-IU-AV': 'PODEMOS',
            'PODEMOS-AV': 'PODEMOS',
            'IU-MÁS MADRID': 'SUMAR',
            'JUNTOS-LEVANTA': 'JUNTOS-LEVANTA',
            'OTROS': 'OTROS', 'OTROS PARTIDOS': 'OTROS', 'OTRO PARTIDO': 'OTROS',
            'EN BLANCO': 'En Blanco', 'BLANCO': 'En Blanco', 'VOTO EN BLANCO': 'En Blanco',
            'VOTO BLANCO': 'En Blanco',
            'VOTO NULO': 'Voto Nulo', 'NULO': 'Voto Nulo'
        }
        
        # Limpieza de puntos para siglas (P.P. -> PP)
        nombre_clean = nombre.replace('.', '')
        
        for variante, canonico in mapeo.items():
            # Intentar match con nombre original o sin puntos
            if re.search(rf'\b{re.escape(variante)}\b', nombre) or \
               re.search(rf'\b{re.escape(variante)}\b', nombre_clean):
                return canonico
        
        return ""
        
        return ""
    
    def _get_partidos_extra(self) -> list:
        """Partidos adicionales a buscar que no están en referencia."""
        return ['OTROS', 'EN BLANCO', 'NULO']
    
    def _try_float(self, val) -> float:
        """Intenta convertir un valor a float."""
        try:
            if isinstance(val, str):
                val = val.replace('%', '').replace(',', '.').strip()
                if '±' in val or '–' in val or '-' in val:
                    return None
            v = float(val)
            return v if not pd.isna(v) else None
        except:
            return None
    
    def extraer_recuerdo_voto(self) -> dict:
        """Extrae los datos de Recuerdo de Voto de la hoja RV correspondiente."""
        hoja_rv = self.get_hoja_rv()
        if hoja_rv not in self.sheet_names:
            return {}
        
        df = pd.read_excel(self.excel_file, sheet_name=hoja_rv, header=None)
        
        # Buscar fila con nombres de partidos
        party_row = -1
        for i in range(min(50, len(df))):
            row_str = ' '.join([str(x).upper() for x in df.iloc[i].values])
            if 'PP' in row_str and 'PSOE' in row_str:
                party_row = i
                break
        
        if party_row < 0:
            return {}
        
        # Buscar fila (N) con totales
        n_rows = df[df.iloc[:, 0].astype(str).str.contains(r"\(N\)", na=False, regex=True)].index
        if len(n_rows) == 0:
            return {}
        
        n_idx = n_rows[0]
        
        # Mapear columnas a partidos y calcular porcentajes
        recuerdo = {}
        total = 0
        valores_raw = {}
        
        for col_idx, val in enumerate(df.iloc[party_row].values):
            p_raw = str(val).strip().upper()
            p_key = self._normalizar_partido(str(val))
            
            # Capturar partidos de referencia Y categorías de no-partido (Blanco/Nulo)
            if p_key and (p_key in self.get_partidos_referencia() or p_key in ['En Blanco', 'Voto Nulo']):
                v = self._try_float(df.iloc[n_idx, col_idx])
                if v and v > 0:
                    valores_raw[p_key] = v
                    total += v
            # Fallback manual para Blanco/Nulo si el normalizador falló
            elif 'BLANCO' in p_raw:
                v = self._try_float(df.iloc[n_idx, col_idx])
                if v: valores_raw['En Blanco'] = valores_raw.get('En Blanco', 0) + v; total += v
            elif 'NULO' in p_raw:
                v = self._try_float(df.iloc[n_idx, col_idx])
                if v: valores_raw['Voto Nulo'] = valores_raw.get('Voto Nulo', 0) + v; total += v
        
        if total > 0:
            for p_key, v in valores_raw.items():
                recuerdo[p_key] = (v / total) * 100
        
        return recuerdo
    
    def calcular_aldabon_gemini(self) -> dict:
        """
        Calcula la estimación usando el método Aldabón-Gemini.
        
        Fórmula: Estimación = Voto_Directo × K × Ajuste_Fidelidad
        Donde K = Voto_Real_Referencia / Recuerdo_Encuesta
        """
        voto_directo = self.extraer_voto_directo()
        recuerdo = self.extraer_recuerdo_voto()
        partidos_ref = self.get_partidos_referencia()
        
        if not voto_directo or not recuerdo:
            return {}
        
        # Calcular factores K
        sum_rec = sum(recuerdo.values())
        k_factors = {}
        for p, voto_real in partidos_ref.items():
            rec = recuerdo.get(p, 0)
            if rec > 0 and sum_rec > 0:
                rec_pct = (rec / sum_rec) * 100
                k = voto_real / rec_pct
                # Amortiguación del factor K (Aldabón-Gemini 2.6: Mayor peso al Voto Directo)
                # Bajamos el factor de 0.75 a 0.40 para evitar que el sesgo de memoria 
                # destruya la intención de voto declarada.
                k_factors[p] = 1.0 + (k - 1.0) * 0.40
            else:
                k_factors[p] = 1.0
        
        # Obtener configuración contextual (Gurú 2.1)
        config = self.get_context_biases()
        fidelidad_map = config['fidelidad']
        transvases_map = config['transvases']
        
        # 1. Aplicar fórmula base (Voto Directo * K * Fidelidad) y calcular masa "perdida"
        estimacion_raw = {}
        masa_perdida = {} # Para redistribución de "voto refugio"
        
        for p, vd in voto_directo.items():
            if p in ['No Sabe', 'No Contesta', 'Abstención']:
                continue
                
            # Intentar obtener K-factor. Si es categoría técnica, buscarla en partidos_ref o usar 1.
            k = k_factors.get(p, 1.0)
            if p in ['En Blanco', 'Voto Nulo'] and p not in k_factors:
                rec_val = recuerdo.get(p, 0)
                ref_val = partidos_ref.get(p, 0)
                if rec_val > 0:
                    k = 1.0 + ((ref_val / rec_val) - 1.0) * 0.75 # K amortiguado
                else:
                    k = 1.0

            fid = fidelidad_map.get(p, 1.0)
            
            # Valor base cocinado amortiguado
            base_val = vd * k
            # Protección Suelo: El cocinado no debería bajar mucho del Voto Directo
            # a menos que haya una fidelidad bajísima detectada.
            estimacion_raw[p] = max(vd * 0.9, base_val * fid)
            
            # La masa que no se queda en el partido puede ir a otros (transvase)
            masa_perdida[p] = base_val * (1 - fid) if (base_val * fid) < base_val else 0
            
        # 2. Aplicar "Voto Refugio" (Transvases ideológicos)
        # Redistribuir la masa perdida entre los partidos del mismo bloque
        for origen, masa in masa_perdida.items():
            if masa > 0 and origen in transvases_map:
                destinos = transvases_map[origen]
                for destino, porcentaje in destinos.items():
                    if destino in estimacion_raw or destino == 'En Blanco':
                        refugio_val = masa * porcentaje
                        estimacion_raw[destino] = estimacion_raw.get(destino, 0.0) + refugio_val
        
        # Normalizar a 100% incluyendo categorías de voto (Blanco/Nulo)
        estimacion = {}
        total = sum(estimacion_raw.values())
        if total > 0:
            # Normalizar y redondear
            estimacion = {p: round(v * 100 / total, 1) for p, v in estimacion_raw.items()}
            # Ajustar para que sume exactamente 100%
            suma_actual = sum(estimacion.values())
            if abs(suma_actual - 100) > 0.01 and estimacion:
                # Ajustar el valor más grande para compensar diferencia
                partido_mayor = max(estimacion, key=estimacion.get)
                estimacion[partido_mayor] = round(estimacion[partido_mayor] + (100 - suma_actual), 1)
        
        return estimacion
    
    def calcular_aldabon_claude(self) -> dict:
        """
        Calcula la estimación usando el método Aldabón-Claude.
        
        Enfoque: Aplicar SOLO el Factor K de corrección por recuerdo de voto,
        SIN los ajustes de fidelidad adicionales que usa Aldabón-Gemini.
        
        Esto es más conservador que Gemini (que aplica ajustes de fidelidad)
        pero diferente del CIS (que usa lógica difusa e inercia).
        
        Fórmula: Estimación = Voto_Directo × K
        Donde K = Voto_Real_Referencia / Recuerdo_Encuesta
        """
        voto_directo = self.extraer_voto_directo()
        recuerdo = self.extraer_recuerdo_voto()
        partidos_ref = self.get_partidos_referencia()
        
        if not voto_directo:
            return {}
        
        # Si no hay recuerdo, devolver Voto Directo normalizado
        if not recuerdo:
            total = sum(voto_directo.values())
            if total > 0:
                return {p: round(v * 100 / total, 1) for p, v in voto_directo.items()}
            return {}
        
        # Calcular factores K (sin ajustes de fidelidad)
        sum_rec = sum(recuerdo.values())
        k_factors = {}
        for p, voto_real in partidos_ref.items():
            rec = recuerdo.get(p, 0)
            if rec > 0 and sum_rec > 0:
                rec_pct = (rec / sum_rec) * 100
                # Factor K puro, sin modificaciones
                k_factors[p] = voto_real / rec_pct
            else:
                k_factors[p] = 1.0
        
        # Aplicar fórmula simple usando la fidelidad base sin transvases (modelo conservador)
        fid_map = self.get_context_biases()['fidelidad']
        estimacion_raw = {}
        for p, vd in voto_directo.items():
            # Solo cocinar partidos y categorías de voto (excluir NS/NC/Abstención)
            if p in ['No Sabe', 'No Contesta', 'Abstención']:
                continue
                
            # K-factor amortiguado para todas las categorías incluyendo Blanco/Nulo
            k = k_factors.get(p, 1.0)
            if p in ['En Blanco', 'Voto Nulo'] and p not in k_factors:
                rec_val = recuerdo.get(p, 0)
                ref_val = partidos_ref.get(p, 0)
                if rec_val > 0:
                    k = 1.0 + ((ref_val / (rec_val/sum_rec*100) if sum_rec>0 else 1) - 1.0) * 0.75
                else:
                    k = 1.0

            fid = fid_map.get(p, 1.0)
            # Limitar factor K para evitar distorsiones extremas
            k = max(0.5, min(2.0, k))
            estimacion_raw[p] = vd * k * fid
        
        # Normalizar a 100% solo los partidos
        estimacion = {}
        total = sum(estimacion_raw.values())
        if total > 0:
            estimacion = {p: round(v * 100 / total, 1) for p, v in estimacion_raw.items()}
            # Ajustar para que sume exactamente 100%
            suma_actual = sum(estimacion.values())
            if abs(suma_actual - 100) > 0.01 and estimacion:
                partido_mayor = max(estimacion, key=estimacion.get)
                estimacion[partido_mayor] = round(estimacion[partido_mayor] + (100 - suma_actual), 1)
        
        return estimacion


class AvanceGenerales(EstudioCIS):

    """Clase para Avances de Elecciones Generales."""
    
    # Resultados reales de las Elecciones Generales 2023
    VOTO_REAL_2023 = {
        'PP': 33.1, 'PSOE': 31.7, 'VOX': 12.4, 'SUMAR': 12.3,
        'ERC': 1.9, 'JUNTS': 1.6, 'BILDU': 1.4, 'PNV': 1.1,
        'BNG': 0.8, 'CCA': 0.5, 'UPN': 0.2, 'PODEMOS': 3.3,
        'En Blanco': 0.8, 'Voto Nulo': 1.1
    }
    
    def get_partidos_referencia(self) -> dict:
        return self.VOTO_REAL_2023
    
    def get_hoja_rv(self) -> str:
        return 'RV EG23'


class AvanceAutonomicas(EstudioCIS):
    """Clase para Avances de Elecciones Autonómicas."""
    
    # Diccionario de resultados por comunidad autónoma
    VOTO_REAL_AUTONOMICAS = {
        'ARAGON': {
            'PP': 35.6, 'PSOE': 27.3, 'VOX': 11.2, 'CHA': 5.8,
            'PAR': 3.2, 'SUMAR': 4.5, 'PODEMOS': 2.1, 'TERUEL EXISTE': 2.5,
            'En Blanco': 1.7, 'Voto Nulo': 1.1
        },
        'EXTREMADURA': {
            'PP': 38.8, 'PSOE': 39.9, 'VOX': 8.1, 'PODEMOS': 6.0, # Volver a 2023 para calibración de 3538
            'SUMAR': 1.0, 'En Blanco': 1.2, 'Voto Nulo': 1.3, 'OTROS': 3.7
        }
    }
    
    def __init__(self, file_path: str, comunidad: str = 'ARAGON'):
        super().__init__(file_path)
        self.comunidad = comunidad.upper()
    
    def get_partidos_referencia(self) -> dict:
        return self.VOTO_REAL_AUTONOMICAS.get(self.comunidad, {})
    
    def get_hoja_rv(self) -> str:
        return 'RV EA23'
    
    def _normalizar_partido(self, nombre: str) -> str:
        """Normaliza partidos con variantes autonómicas."""
        # 1. Intentar normalización base
        norm = super()._normalizar_partido(nombre)
        if norm: return norm
        
        # 2. Si no normalizó, aplicar lógica regional específica
        nombre_up = str(nombre).upper().strip()
        
        if self.comunidad == 'ARAGON':
            mapeo_aragon = {
                'PODEMOS-AV': 'PODEMOS', 'PODEMOS ARAGÓN': 'PODEMOS',
                'IU-MOVIMIENTO SUMAR': 'SUMAR', 'IU-ARAGÓN': 'SUMAR',
                'CHUNTA': 'CHA', 'PAR': 'PAR', 'TERUEL EXISTE': 'TERUEL EXISTE'
            }
            for v, c in mapeo_aragon.items():
                if v in nombre_up: return c
                
        elif self.comunidad == 'EXTREMADURA':
            mapeo_ext = {
                'PODEMOS-IU-AV': 'PODEMOS', 'UNIDAS POR EXTREMADURA': 'PODEMOS',
                'JUNTOS LEVANTA': 'JUNTOS-LEVANTA', 'LEVANTA': 'JUNTOS-LEVANTA',
                'NEX': 'OTROS', 'EXTREMADURA UNIDA': 'EXTREMADURA UNIDA'
            }
            for v, c in mapeo_ext.items():
                if v in nombre_up: return c
        
        return norm # Retornará "" si nada funcionó

    def get_context_biases(self) -> dict:
        """Ajustes automáticos basados en la sociología detectada."""
        return super().get_context_biases()


class BarometroNacional(EstudioCIS):
    """Clase para Barómetros Nacionales."""
    
    # Mismos resultados que Generales
    VOTO_REAL_2023 = AvanceGenerales.VOTO_REAL_2023.copy()
    VOTO_REAL_2023['SALF'] = 0.0  # Partido nuevo, sin referencia
    
    def get_partidos_referencia(self) -> dict:
        return self.VOTO_REAL_2023
    
    def get_hoja_rv(self) -> str:
        return 'RV EG23'


# --- Factory para crear el tipo correcto de estudio ---

def crear_estudio(file_path: str) -> EstudioCIS:
    """
    Factory que crea el tipo correcto de estudio basándose en el archivo.
    """
    xl = pd.ExcelFile(file_path)
    sheets = xl.sheet_names
    
    # Detectar tipo por hojas disponibles
    tiene_rv_ea = any('RV EA' in s for s in sheets)
    tiene_rv_eg = any('RV EG' in s for s in sheets)
    tiene_estimacion = any('estimaci' in s.lower() for s in sheets)
    
    # Detección robusta de autonómicas (por nombre de hoja de resultados)
    comunidades = ['EXTREMADURA', 'ARAGÓN', 'ARAGON', 'MADRID', 'VALENCIA', 'CATALUNYA', 'PAÍS VASCO', 'GALICIA']
    es_autonomico = tiene_rv_ea or any('RESULTADOS' in s.upper() and any(c in s.upper() for c in comunidades) for s in sheets)
    
    # Buscar PDF asociado
    base_id = re.split(r'[_-]', os.path.basename(file_path))[0]
    dir_path = os.path.dirname(file_path)
    tiene_pdf = any(
        os.path.exists(os.path.join(dir_path, f"{base_id}{suf}"))
        for suf in ['_Estimacion.pdf', '-Estimacion.pdf']
    )
    
    # Determinar tipo
    if es_autonomico:
        # Detectar comunidad autónoma analizando la Ficha técnica o el nombre del archivo
        comunidad = 'ARAGON'
        try:
            # Primero intentar por nombre de hoja
            for s in sheets:
                s_up = s.upper()
                if 'RESULTADOS' in s_up:
                    for c in comunidades:
                        if c in s_up:
                            comunidad = c
                            if comunidad == 'ARAGÓN': comunidad = 'ARAGON'
                            break
            
            # Si no, buscar en ficha técnica
            if comunidad == 'ARAGON' and 'Ficha técnica' in sheets:
                ficha_df = pd.read_excel(file_path, sheet_name='Ficha técnica', header=None)
                ficha_text = ficha_df.to_string().upper()
                if 'EXTREMADURA' in ficha_text:
                    comunidad = 'EXTREMADURA'
                elif 'ARAGÓN' in ficha_text or 'ARAGON' in ficha_text:
                    comunidad = 'ARAGON'
        except:
            pass
        return AvanceAutonomicas(file_path, comunidad)
    elif tiene_pdf or (not tiene_estimacion and tiene_rv_eg):
        return BarometroNacional(file_path)
    else:
        return AvanceGenerales(file_path)


if __name__ == "__main__":
    # Prueba básica
    import os
    
    test_files = [
        ("data/cis_studies/3543-multi_A.xlsx", "Avance Autonómicas Aragón"),
        ("data/cis_studies/3524_multi_A.xlsx", "Avance Generales"),
        ("data/cis_studies/3536-multi.xlsx", "Barómetro Nacional"),
    ]
    
    for path, desc in test_files:
        if os.path.exists(path):
            print(f"\n=== {desc} ({path}) ===")
            estudio = crear_estudio(path)
            print(f"Tipo: {type(estudio).__name__}")
            print(f"Hoja RV: {estudio.get_hoja_rv()}")
            print(f"Partidos referencia: {list(estudio.get_partidos_referencia().keys())[:5]}...")
