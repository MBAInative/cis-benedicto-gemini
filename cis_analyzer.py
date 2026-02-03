import pandas as pd
import sys
import os
import re

try:
    from cis_pdf_processor import extract_official_data_from_pdf
except ImportError:
    extract_official_data_from_pdf = None

def detect_ambito_y_ficha(xl):
    """Analiza las hojas RV y la ficha técnica para determinar el ámbito real."""
    meta = {
        "ambito": "NACIONAL", "region": None, "n": "N/A", "campo": "N/A",
        "referencia": "Generales 2023", "rv_sheet": None
    }
    
    # Detectar ámbito por hojas RV disponibles
    rv_sheets = [s for s in xl.sheet_names if s.startswith('RV')]
    if 'RV EA23' in rv_sheets:  # Elecciones Autonómicas
        meta["ambito"] = "AUTONÓMICO"
        meta["rv_sheet"] = "RV EA23"
        meta["referencia"] = "Autonómicas 2023"
    elif 'RV EG23' in rv_sheets:  # Elecciones Generales
        meta["rv_sheet"] = "RV EG23"
    elif rv_sheets:
        meta["rv_sheet"] = rv_sheets[0]
    
    # Extraer región de ficha técnica
    ficha_name = next((s for s in xl.sheet_names if 'FICHA' in s.upper()), None)
    if ficha_name:
        df_f = pd.read_excel(xl, sheet_name=ficha_name).fillna("")
        for i in range(len(df_f)):
            row_str = " ".join([str(x).upper() for x in df_f.iloc[i]]).strip()
            
            if "ÁMBITO" in row_str:
                 for val in df_f.iloc[i]:
                      val_s = str(val).upper()
                      if "ARAGÓN" in val_s or "ARAGON" in val_s:
                           meta["region"] = "ARAGÓN"
                           meta["ambito"] = "AUTONÓMICO"
                           meta["referencia"] = "Autonómicas Aragón 2023"
                      elif "COMUNIDAD" in val_s or "AUTONÓMICA" in val_s:
                           meta["ambito"] = "AUTONÓMICO"
                           region = val_s.replace("COMUNIDAD AUTÓNOMA DE", "").split("(")[0].strip()
                           meta["region"] = region
                           meta["referencia"] = f"Autonómicas {region} 2023"
            elif "TAMAÑO" in row_str or "PRODUCTO" in row_str:
                 for val in df_f.iloc[i]:
                      if any(c.isdigit() for c in str(val)): meta["n"] = str(val); break
            elif "CAMPO" in row_str or "FECHA" in row_str:
                 for val in df_f.iloc[i]:
                      if "/" in str(val) or "-" in str(val): meta["campo"] = str(val); break

    return meta

def extract_baseline_from_rv(xl, rv_sheet_name):
    """Extrae el baseline real de la hoja de Recuerdo de Voto.
    
    Busca la fila (N) que contiene los totales y extrae los porcentajes
    de cada partido desde esa fila.
    """
    if not rv_sheet_name or rv_sheet_name not in xl.sheet_names:
        return {}
    
    df_rv = pd.read_excel(xl, sheet_name=rv_sheet_name)
    baseline = {}
    
    # Buscar fila (N) con totales
    n_rows = df_rv[df_rv.iloc[:, 0].astype(str).str.contains(r"\(N\)", na=False, regex=True)].index
    if n_rows.empty:
        return {}
    
    n_idx = n_rows[0]
    
    # Buscar fila con nombres de partidos (suele estar antes de (N))
    for r in range(max(0, n_idx-15), n_idx):
        row_vals = [str(x).upper().strip() for x in df_rv.iloc[r].values]
        # Buscar si hay partidos conocidos en esta fila
        if any(p in " ".join(row_vals) for p in ['PP', 'PSOE', 'VOX']):
            for col_idx, name in enumerate(row_vals):
                p_key = normalize_name(name)
                if p_key and len(p_key) > 1:
                    # Extraer valor de la fila (N) para esta columna
                    val = try_float(df_rv.iloc[n_idx, col_idx])
                    if val and 0.1 < val < 100:
                        baseline[p_key] = val
            break
    
    return baseline

def get_baseline_results(ambito, region=None):
    """Retorna los resultados OFICIALES de referencia según el ámbito.
    
    Fuente: Ministerio del Interior - Resultados Electorales
    - Generales 23J: https://resultados.elecciones.interior.gob.es/
    - Autonómicas Aragón 2023: https://resultados2023.aragon.es/
    """
    # Generales 23J (Nacional) - Datos Oficiales Ministerio del Interior
    if ambito == "NACIONAL":
        return {
            'PP': 33.1, 'PSOE': 31.7, 'VOX': 12.4, 'SUMAR': 12.3,
            'ERC': 1.9, 'JUNTS': 1.6, 'EH BILDU': 1.4, 'EAJ-PNV': 1.1,
            'BNG': 0.6, 'CC': 0.5, 'UPN': 0.2, 'PACMA': 0.7
        }
    # Autonómicas Aragón 2023 - Datos Oficiales Gobierno de Aragón
    if region == "ARAGÓN" and ambito == "AUTONÓMICO":
        return {
            'PP': 35.5, 'PSOE': 29.5, 'VOX': 11.3, 'CHA': 5.1,
            'TERUEL EXISTE': 5.0, 'SUMAR': 4.2, 'PAR': 2.1, 'PODEMOS': 4.0
        }
    return {}

def find_rv_sheet(xl):
    """Localiza la hoja de Recuerdo de Voto por contenido."""
    # Prioridad 1: Nombres directos
    known = ['RV EG23', 'RV AU23', 'RECUERDO VOTO', 'RV 23-J', 'RECUERDO_VOTO', 'VOTO']
    for k in known:
        if k in xl.sheet_names and k != 'Estimación de Voto': return k
    
    # Prioridad 2: Heurística por contenido
    for s in xl.sheet_names:
        if 'ESTIMAC' in s.upper(): continue
        try:
             df_head = pd.read_excel(xl, sheet_name=s, nrows=40).astype(str)
             content = " ".join(df_head.values.flatten()).upper()
             if "(N)" in content and 'PP' in content and 'PSOE' in content:
                  return s
        except: continue
    return None

def normalize_name(val):
    """Normalización de élite: robusta a ruido, mayúsculas y sufijos."""
    if pd.isna(val): return ""
    p = str(val).replace('*','').upper().strip()
    
    # Mapeo universal de keywords a claves de baseline
    mappings = {
        "PSOE": ["SOCIALISTA", "PSOE", "SÁNCHEZ", "PARTIDO SOCIALISTA"],
        "PP": ["POPULAR", "PP", "FEIJOO", "FEIJÓO", "PARTIDO POPULAR"],
        "VOX": ["VOX", "ABASCAL"],
        "SUMAR": ["SUMAR", "MOVIMIENTO SUMAR", "YOLANDA", "IU", "IZQUIERDA UNIDA"],
        "PODEMOS": ["PODEMOS", "BELARRA", "MONTERO"],
        "SALF": ["FIESTA", "SALF", "ALVISE"],
        "ERC": ["ERC", "ESQUERRA"],
        "JUNTS": ["JUNTS", "PUIGDEMONT"],
        "EH BILDU": ["BILDU", "OTEGI"],
        "EAJ-PNV": ["PNV", "EAJ"],
        "BNG": ["BNG", "GALEGO"],
        "CC": ["CC", "CANARIA", "CCA"],
        "UPN": ["UPN", "NAVARRA"],
        "PACMA": ["PACMA"],
        "CHA": ["CHA", "ARAGONESISTA"],
        "TERUEL EXISTE": ["EXISTE", "TERUEL"],
        "PAR": ["PAR", "ARAGONÉS"]
    }
    
    for key, tokens in mappings.items():
        if any(token in p for token in tokens): return key
        
    # Filtros de exclusión
    exclude = ['TOTAL', 'SABE', 'CONTESTA', 'BLANCO', 'NULO', 'OTROS', 'MARGEN', 'INTERVALO', 'ESCAÑO', 'RESIDENTE']
    if any(x in p for x in exclude) or len(p) < 2: return ""
    
    return p.split()[0]

def analyze_cis_professional(file_path, study_type=None):
    print(f"--- ANALISIS PROFESIONAL: {os.path.basename(file_path)} ---", flush=True)
    
    try:
        xl = pd.ExcelFile(file_path)
        meta = detect_ambito_y_ficha(xl)
        
        # Usar baselines OFICIALES verificados (Ministerio del Interior / Gobierno de Aragón)
        voto_real_ref = get_baseline_results(meta["ambito"], meta.get("region"))
        
        # Localizar hoja de Recuerdo de Voto
        rv_sheet = meta.get("rv_sheet") or find_rv_sheet(xl)
        
        print(f"  Ámbito: {meta['ambito']}, Región: {meta.get('region')}, RV: {rv_sheet}", flush=True)
        print(f"  Baseline oficial: {list(voto_real_ref.keys())[:5]}...", flush=True)
        
        # Cargar hoja RV para uso posterior
        df_rv = pd.read_excel(xl, sheet_name=rv_sheet) if rv_sheet else None

        df_estim_official = None
        df_raw_source = None
        
        # Búsqueda de Estimación Oficial
        estim_sheet = next((s for s in xl.sheet_names if any(x in s.upper() for x in ['ESTIMACI', 'AVANCE', 'VOTO_EST'])), None)
        if estim_sheet:
            df_estim_official = pd.read_excel(xl, sheet_name=estim_sheet)
            # Ampliar a 50 filas para archivos con notas metodológicas extensas
            content = " ".join(df_estim_official.iloc[:50].astype(str).values.flatten()).upper()
            if "VOTO DIRECTO" in content or "VOTO + SIMPATÍA" in content: 
                df_raw_source = df_estim_official

        # Si es Barómetro, PRIORIDAD ABSOLUTA al PDF para Oficial
        if study_type == "BAROMETRO" and extract_official_data_from_pdf:
            study_id = re.split(r'[_ -]', os.path.basename(file_path))[0]
            # Buscar PDF en el mismo directorio
            pdf_path = os.path.join(os.path.dirname(file_path), f"{study_id}_Estimacion.pdf")
            # A. Extraer Estimación CIS (Niveles de Prioridad v6.0)
        
        # --- 2. EXTRACCIÓN DE DATOS CRUDA ---
        cis_oficial = {}
        voto_simp = {}
        
        # A. Extraer Estimación CIS (Niveles de Prioridad v6.2)
        base_id = re.split(r'[_ -]', os.path.basename(file_path))[0]
        pdf_variants = [f"{base_id}_Estimacion.pdf", f"{base_id}-Estimacion.pdf"]
        
        for pv in pdf_variants:
             pdf_path = os.path.join(os.path.dirname(file_path), pv)
             if os.path.exists(pdf_path) and extract_official_data_from_pdf:
                  df_pdf = extract_official_data_from_pdf(pdf_path)
                  if df_pdf is not None and len(df_pdf) > 0:
                       # El PDF retorna DataFrame con ['Partido', 'Estimación']
                       # Convertir directamente a diccionario (NO usar extract_from_dataframe)
                       for _, row in df_pdf.iterrows():
                            p_name = str(row.get('Partido', '')).upper().strip()
                            p_key = normalize_name(p_name)
                            val = try_float(row.get('Estimación', 0))
                            if p_key and val:
                                 cis_oficial[p_key] = val
                       if cis_oficial:
                            print(f"  PDF Official extraído: {list(cis_oficial.keys())[:5]}...", flush=True)
                       break

        # Si no hay datos del PDF, intentar extraer del Excel
        voto_directo_excel = {}
        if not cis_oficial and df_estim_official is not None:
             # Extraer AMBAS columnas: Voto Directo (col 1) y Estimación CIS (col 3)
             extracted = extract_from_dataframe(df_estim_official, voto_real_ref)
             if extracted:
                  voto_directo_excel = extracted.get('voto_directo', {})
                  cis_oficial = extracted.get('estimacion_cis', {})
                  print(f"  Excel Voto Directo: {list(voto_directo_excel.keys())[:4]}...", flush=True)
                  print(f"  Excel Estimación CIS: {list(cis_oficial.keys())[:4]}...", flush=True)
             
             # Fallback: Escanear todas las hojas si falla
             if not cis_oficial:
                  for sheet in xl.sheet_names:
                       if sheet == estim_sheet: continue
                       df_alt = pd.read_excel(xl, sheet_name=sheet)
                       extracted = extract_from_dataframe(df_alt, voto_real_ref)
                       if extracted.get('estimacion_cis'):
                            voto_directo_excel = extracted.get('voto_directo', {})
                            cis_oficial = extracted.get('estimacion_cis', {})
                            break

        # B. Extraer Intención de Voto desde hoja RV (Fuente unificada para Barómetros y Avances)
        # La tabla RV tiene: fila con nombres de partidos (PP, PSOE...) y fila (N) con totales ABSOLUTOS
        # Debemos convertir a PORCENTAJES dividiendo entre el total
        if df_rv is not None and voto_simp == {}:
             # Buscar fila con nombres de partidos
             party_row = -1
             for i in range(min(50, len(df_rv))):
                  row_str = ' '.join([str(x).upper() for x in df_rv.iloc[i].values])
                  if 'PP' in row_str and 'PSOE' in row_str and 'VOX' in row_str:
                       party_row = i
                       break
             
             if party_row >= 0:
                  # Mapear columnas a partidos
                  party_cols = {}
                  for col_idx, val in enumerate(df_rv.iloc[party_row].values):
                       p_key = normalize_name(val)
                       if p_key and len(p_key) > 1:
                            party_cols[col_idx] = p_key
                  
                  # Buscar fila (N) con totales
                  n_rows = df_rv[df_rv.iloc[:, 0].astype(str).str.contains(r"\(N\)", na=False, regex=True)].index
                  if len(n_rows) > 0:
                       n_idx = n_rows[0]
                       
                       # Paso 1: Calcular TOTAL sumando todos los partidos relevantes
                       total_abs = 0
                       raw_values = {}
                       for col_idx, p_key in party_cols.items():
                            val = try_float(df_rv.iloc[n_idx, col_idx])
                            if val and val > 0:
                                 raw_values[p_key] = val
                                 if p_key in voto_real_ref or p_key in ['SALF', 'PODEMOS']:
                                      total_abs += val
                       
                       # Paso 2: Convertir a PORCENTAJES
                       if total_abs > 0:
                            for p_key, val in raw_values.items():
                                 if p_key in voto_real_ref or p_key in ['SALF', 'PODEMOS']:
                                      voto_simp[p_key] = (val / total_abs) * 100

        # 4. Extracción de Recuerdo de Voto (porcentajes, no absolutos)
        recuerdo_enc = {}
        if df_rv is not None:
             # Buscar fila con nombres de partidos
             party_row = -1
             for i in range(min(50, len(df_rv))):
                  row_str = ' '.join([str(x).upper() for x in df_rv.iloc[i].values])
                  if 'PP' in row_str and 'PSOE' in row_str:
                       party_row = i
                       break
             
             if party_row >= 0:
                  # Buscar fila de porcentajes (suele estar justo después de (N))
                  n_rows = df_rv[df_rv.iloc[:, 0].astype(str).str.contains(r"\(N\)", na=False, regex=True)].index
                  if len(n_rows) > 0:
                       n_idx = n_rows[0]
                       # Los porcentajes están en la fila (N) como proporción del total
                       total = 0
                       for col_idx, val in enumerate(df_rv.iloc[party_row].values):
                            p_key = normalize_name(val)
                            if p_key in voto_real_ref:
                                 v = try_float(df_rv.iloc[n_idx, col_idx])
                                 if v: total += v
                       
                       if total > 0:
                            for col_idx, val in enumerate(df_rv.iloc[party_row].values):
                                 p_key = normalize_name(val)
                                 if p_key in voto_real_ref:
                                      v = try_float(df_rv.iloc[n_idx, col_idx])
                                      if v: recuerdo_enc[p_key] = (v / total) * 100

        # 5. Metodología Aldabón-Gemini (Solo si hay Recuerdo de Voto)
        final = {}
        if df_rv is not None:
             sum_rec = sum([recuerdo_enc.get(p, 0) for p in voto_real_ref])
             k_factors = {p: (voto_real_ref[p] / (recuerdo_enc.get(p, 0) / sum_rec * 100) if (sum_rec > 0 and recuerdo_enc.get(p, 0) > 0) else 1.0) for p in voto_real_ref}

             ajustes = {'PSOE': 0.94, 'PP': 0.93, 'VOX': 0.85, 'SUMAR': 0.88, 'PODEMOS': 0.82, 'SALF': 1.10}
             estim_aj = {}
             for p in voto_simp:
                  k = k_factors.get(p, 1.0)
                  if p == 'PODEMOS' and 'SUMAR' in k_factors: k = k_factors['SUMAR']
                  estim_aj[p] = voto_simp[p] * k * ajustes.get(p, 1.0)

             total = sum(estim_aj.values())
             final = {p: round(v * 100 / total, 1) for p, v in estim_aj.items()} if total > 0 else {}

        # Usar voto_directo_excel si está disponible, sino usar voto_simp
        raw_to_use = voto_directo_excel if voto_directo_excel else {p: round(voto_simp.get(p,0), 1) for p in (final if final else cis_oficial)}
        
        return {
            'benedicto': final, 
            'official': cis_oficial,  # Estimación CIS (col 3) = Alamino-Tezanos
            'raw': raw_to_use,        # Voto Directo (col 1) = Voto Directo en encuesta
            'meta': meta
        }
    except Exception as e:
        print(f"Error Crítico: {e}"); return None

def extract_from_dataframe(df, voto_real_ref):
    """Extrae Voto Directo (col 1) y Estimación CIS (col 3) de la hoja de Estimación."""
    try:
        voto_directo = {}
        estimacion_cis = {}
        
        # Lista de partidos a buscar
        search_list = list(voto_real_ref.keys()) + ['SALF', 'PODEMOS', 'SE ACABÓ', 'TERUEL EXISTE', 'IU-MOVIMIENTO SUMAR', 'PODEMOS-AV']
        
        for i in range(min(100, len(df))):
            row = df.iloc[i]
            p_name = str(row.iloc[0]).upper().strip() if pd.notna(row.iloc[0]) else ""
            p_key = normalize_name(p_name)
            
            if p_key and (p_key in search_list or any(s in p_name for s in ['PP', 'PSOE', 'VOX', 'CHA', 'SUMAR', 'PODEMOS', 'TERUEL', 'PAR'])):
                # Normalizar nombre de partido
                if 'SUMAR' in p_name: p_key = 'SUMAR'
                elif 'PODEMOS' in p_name: p_key = 'PODEMOS'
                elif 'TERUEL' in p_name: p_key = 'TERUEL EXISTE'
                elif 'PP' == p_name: p_key = 'PP'
                elif 'PSOE' == p_name: p_key = 'PSOE'
                elif 'VOX' == p_name: p_key = 'VOX'
                elif 'CHA' == p_name: p_key = 'CHA'
                elif 'PAR' == p_name: p_key = 'PAR'
                
                # Col 1 = Voto Directo en la encuesta
                val_vd = try_float(row.iloc[1]) if len(row) > 1 else None
                
                # REFUERZO 3543: Si no hay valor en col 1, mirar la siguiente fila (algunos Avances tienen saltos)
                if val_vd is None and i + 1 < len(df):
                    next_row = df.iloc[i+1]
                    # Solo tomar si col 0 está vacía en la siguiente fila (indica continuación)
                    if pd.isna(next_row.iloc[0]) or str(next_row.iloc[0]).strip() == "":
                        val_vd = try_float(next_row.iloc[1]) if len(next_row) > 1 else None

                if val_vd and 0.1 <= val_vd <= 65:
                    if p_key not in voto_directo:
                        voto_directo[p_key] = val_vd
                
                # Col 3 = Estimación CIS (Alamino-Tezanos)
                val_est = try_float(row.iloc[3]) if len(row) > 3 else None
                
                # REFUERZO 3543: Mirar también la siguiente fila para la estimación si es necesario
                if val_est is None and i + 1 < len(df):
                    next_row = df.iloc[i+1]
                    if pd.isna(next_row.iloc[0]) or str(next_row.iloc[0]).strip() == "":
                        val_est = try_float(next_row.iloc[3]) if len(next_row) > 3 else None

                if val_est and 0.1 <= val_est <= 65:
                    if p_key not in estimacion_cis:
                        estimacion_cis[p_key] = val_est
            
            # REFUERZO 3543: Si ya tenemos los principales y llegamos a una zona de corte (como el inicio de otra provincia)
            # detectada por una celda que contiene 'N=' o similar, podríamos parar.
            # Pero más simple: no sobreescribir si ya tenemos un valor para ese partido.
            # Así la primera tabla (el total de la comunidad) manda.

        # Retornar ambos en formato compatible (estimacion_cis como default para compatibilidad)
        return {'voto_directo': voto_directo, 'estimacion_cis': estimacion_cis, **estimacion_cis}
    except Exception as e:
        print(f"Error extracción: {e}", flush=True)
        return {}

def try_float(val):
    try:
        if isinstance(val, str): 
             val = val.replace('%', '').replace(',', '.').strip()
             if '±' in val or '-' in val or '–' in val: return None
        v_f = float(val)
        return v_f if not pd.isna(v_f) else None
    except: return None

if __name__ == "__main__":
    pass
