import streamlit as st
import pandas as pd
import altair as alt
import os
import tempfile

# Import new class-based module
try:
    from cis_estudios import crear_estudio, AvanceGenerales, AvanceAutonomicas, BarometroNacional
except Exception as e:
    st.error(f"Error importing cis_estudios: {e}")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="CIS Monitor: Comparativa de Métodos",
    page_icon="⚖️",
    layout="wide"
)

# Título y Descripción
st.title("⚖️ CIS Monitor: Comparativa de Métodos de Cocina Electoral")
st.markdown("""
- **Voto Directo**: Intención de voto espontánea (incluye indecisos y abstención cruda)
- **Estimación CIS**: Método Alamino-Tezanos (oficial del CIS sobre voto válido)
- **Aldabón-Gemini 3.0**: Factor K × Φ (Fidelidad) × Λ (Momentum)
""")

# --- SIDEBAR: SELECTOR Y SUBIDA ---
st.sidebar.header("🗄️ Estudios Disponibles")

# Listar estudios existentes (filtrar archivos temporales ~$)
DATA_DIR = "data/cis_studies"
if os.path.exists(DATA_DIR):
    existing_files = [f for f in os.listdir(DATA_DIR) 
                      if f.endswith('.xlsx') and not f.startswith('~$')]
else:
    existing_files = []

# Selector de estudio existente
if existing_files:
    selected_file = st.sidebar.selectbox("Seleccionar Estudio:", sorted(existing_files, reverse=True))
    file_path = os.path.join(DATA_DIR, selected_file)
else:
    st.sidebar.warning("No hay estudios disponibles")
    file_path = None

    file_path = None

st.sidebar.markdown("---")

# Subida de nuevo estudio
st.sidebar.header("📤 Subir Nuevo Estudio")
uploaded_file = st.sidebar.file_uploader("Subir Excel del CIS:", type=['xlsx'])
uploaded_pdf = st.sidebar.file_uploader("Subir PDF de Estimación (opcional):", type=['pdf'])

if uploaded_file:
    # Guardar archivo subido temporalmente
    os.makedirs(DATA_DIR, exist_ok=True)
    new_file_path = os.path.join(DATA_DIR, uploaded_file.name)
    with open(new_file_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    
    if uploaded_pdf:
        pdf_path = os.path.join(DATA_DIR, uploaded_pdf.name)
        with open(pdf_path, 'wb') as f:
            f.write(uploaded_pdf.getbuffer())
    
    st.sidebar.success(f"✅ Archivo guardado: {uploaded_file.name}")
    file_path = new_file_path

st.sidebar.markdown("---")

# --- ANÁLISIS Y VISUALIZACIÓN ---
if file_path and os.path.exists(file_path):
    try:
        estudio = crear_estudio(file_path)
        
        # Mostrar ficha técnica
        ficha = estudio.extraer_ficha_tecnica()
        st.sidebar.subheader("📋 Ficha Técnica")
        st.sidebar.write(f"**Tipo:** {ficha.get('tipo', 'N/A')}")
        st.sidebar.write(f"**Referencia:** {ficha.get('referencia', 'N/A')}")
        st.sidebar.write(f"**Muestra (N):** {ficha.get('n', 'N/A')}")
        st.sidebar.write(f"**Trabajo de campo:** {ficha.get('campo', 'N/A')}")
        st.sidebar.write(f"**Ámbito:** {ficha.get('ambito', 'N/A')}")

        st.sidebar.write(f"**Hoja RV:** {estudio.get_hoja_rv()}")
        
        # --- DEBUG CONFIG ---
        with st.sidebar.expander("⚙️ Configuración del Modelo", expanded=True):
            if st.button("🧹 Limpiar Caché y Recargar"):
                st.cache_data.clear()
                st.rerun()
            
            try:
                config = estudio.get_context_biases()
                st.markdown("**Fidelidad Actual (Φ):**")
                st.code(f"PP:   {config['fidelidad']['PP']}\nPSOE: {config['fidelidad']['PSOE']}")
            except:
                pass
        
        # Obtener valores por defecto de momentum
        default_momentum = estudio.get_context_biases()['momentum']
        
        # Extraer datos base
        voto_directo = estudio.extraer_voto_directo()
        recuerdo = estudio.extraer_recuerdo_voto()
        estimacion_cis = estudio.extraer_estimacion_cis()
        # Calcular primero con valores por defecto para determinar partidos
        aldabon_gemini_default = estudio.calcular_aldabon_gemini()
        
        # Determinar partidos a mostrar
        all_parties = set()
        for d in [voto_directo, estimacion_cis, aldabon_gemini_default]:
            all_parties.update(d.keys())
        
        # Filtrar partidos con valores > 0.5%
        # Partidos principales (excluyendo categorías técnicas para el orden base)
        main_parties = sorted([p for p in all_parties 
                         if any(d.get(p, 0) > 0.5 for d in [voto_directo, estimacion_cis, aldabon_gemini_default])
                         and p not in ['No Sabe', 'No Contesta', 'Abstención', 'En Blanco', 'Voto Nulo']],
                        key=lambda x: -voto_directo.get(x, 0))
        
        # Categorías de voto técnico que SÍ queremos estimar
        voto_tecnico = ['En Blanco', 'Voto Nulo']
        
        # Categorías de no-voto (para Voto Directo crudo)
        non_vote_cats = ['No Sabe', 'No Contesta', 'Abstención'] + voto_tecnico
        parties = main_parties + [c for c in non_vote_cats if voto_directo.get(c, 0) > 0]
        
        # Categorías a mostrar en columnas de estimación (Partidos + Blanco/Nulo)
        cats_estimacion = main_parties + voto_tecnico
        
        if parties:
            # --- PANEL DE AJUSTE DE MOMENTUM ---
            st.subheader("🎚️ Ajuste de Momentum (Λ)")
            st.caption("Modifica el factor de coyuntura para cada partido. Valores < 1.0 = Desgaste | > 1.0 = Impulso")
            
            # Determinar los 6 primeros partidos por voto directo (dinámico)
            top_momentum_parties = main_parties[:6]
            
            # Crear sliders dinámicamente (2 filas de 3 columnas)
            momentum_values = {}
            row1_parties = top_momentum_parties[:3]
            row2_parties = top_momentum_parties[3:6]
            
            cols_row1 = st.columns(len(row1_parties)) if row1_parties else []
            for i, party in enumerate(row1_parties):
                with cols_row1[i]:
                    momentum_values[party] = st.number_input(
                        party, min_value=0.50, max_value=1.50,
                        value=default_momentum.get(party, 1.0), step=0.01, format="%.2f",
                        key=f"lam_{party}"
                    )
            
            if row2_parties:
                cols_row2 = st.columns(len(row2_parties))
                for i, party in enumerate(row2_parties):
                    with cols_row2[i]:
                        momentum_values[party] = st.number_input(
                            party, min_value=0.50, max_value=1.50,
                            value=default_momentum.get(party, 1.0), step=0.01, format="%.2f",
                            key=f"lam_{party}"
                        )
            
            # Calcular Aldabón-Gemini con momentum ajustado
            custom_momentum = momentum_values
            aldabon_gemini = estudio.calcular_aldabon_gemini(custom_momentum=custom_momentum)
            
            # Mostrar valores de momentum aplicados
            lam_display = " | ".join([f"{p}={v:.2f}" for p, v in momentum_values.items()])
            st.info(f"**Λ aplicados:** {lam_display}")
            
            st.markdown("---")
            
            # --- TABLA COMPARATIVA ---
            st.subheader("📊 Tabla Comparativa de Métodos")
            
            table_data = {
                'Categoría': parties,
                'Voto Directo (Crudo)': [voto_directo.get(p, 0) for p in parties],
                'Estimación CIS': [estimacion_cis.get(p, 0) if p in cats_estimacion else 0 for p in parties],
                'Aldabón-Gemini': [aldabon_gemini.get(p, 0) if p in cats_estimacion else 0 for p in parties],
            }
            
            df = pd.DataFrame(table_data)
            # Diferencia real: (Aldabón-Gemini - Estimación CIS)
            # Solo si la Estimación CIS es > 0, sino mostrar Aldabón-Gemini
            df['Diff (Gemini - CIS)'] = df.apply(
                lambda row: row['Aldabón-Gemini'] - row['Estimación CIS'] if row['Estimación CIS'] > 0 else 0, 
                axis=1
            )
            
            # Formatear tabla
            st.dataframe(
                df.style.format({
                    'Voto Directo (Crudo)': '{:.1f}%',
                    'Estimación CIS': '{:.1f}%',
                    'Aldabón-Gemini': '{:.1f}%',
                    'Diff (Gemini - CIS)': '{:+.1f}%'
                }).applymap(
                    lambda v: 'color: green' if v > 0 else 'color: red' if v < 0 else '',
                    subset=['Diff (Gemini - CIS)']
                ),
                use_container_width=True
            )
            
            # --- GRÁFICO DE BARRAS ---
            st.subheader("📈 Comparativa Visual")
            
            # Preparar datos para gráfico (usa aldabon_gemini ya calculado con momentum ajustado)
            chart_data = []
            for p in parties[:10]:  # Top 10 partidos
                chart_data.append({'Partido': p, 'Método': 'Voto Directo', 'Valor': voto_directo.get(p, 0)})
                chart_data.append({'Partido': p, 'Método': 'Estimación CIS', 'Valor': estimacion_cis.get(p, 0)})
                chart_data.append({'Partido': p, 'Método': 'Aldabón-Gemini', 'Valor': aldabon_gemini.get(p, 0)})
            
            chart_df = pd.DataFrame(chart_data)
            
            chart = alt.Chart(chart_df).mark_bar().encode(
                x=alt.X('Partido:N', sort=parties[:10]),
                y=alt.Y('Valor:Q', title='Estimación (%)'),
                color=alt.Color('Método:N', legend=alt.Legend(orient='top')),
                xOffset='Método:N',
                tooltip=['Partido', 'Método', alt.Tooltip('Valor:Q', format='.1f')]
            ).properties(height=400)
            
            st.altair_chart(chart, use_container_width=True)
            
            # --- EXPLICACIÓN DE MÉTODOS ---
            with st.expander("🎓 Explicación de los Métodos", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    ### Método Alamino-Tezanos (CIS)
                    - Usa **Lógica Difusa**: Asigna indecisos según simpatía o cercanía.
                    - **Efecto Inercia**: El recuerdo histórico pesa mucho más que la intención directa.
                    - Suele favorecer ligeramente a los partidos de la coalición de gobierno.
                    """)
                    
                    st.markdown("""
                    ### Voto Directo (Crudo)
                    - Es la intención de voto declarada por el ciudadano en la encuesta.
                    - Representa el **"suelo de realidad"** del que parte el modelo.
                    - No incluye corrección técnica por mentira o falta de recuerdo.
                    """)
                
                with col2:
                    st.markdown("""
                    ### Método Aldabón-Gemini 3.0
                    - **Fórmula**: $E_p = S_p \\times K_p \\times \\Phi_p \\times \\Lambda_p$
                    - **K (Factor de Corrección)**: Corrige el sesgo de recuerdo de voto.
                    - **Φ (Fidelidad)**: Tasa de retención estructural histórica.
                    - **Λ (Momentum)**: Parámetro SUBJETIVO ajustable por el usuario.
                    - **Protección de Suelo**: Nunca estima por debajo del **100% del VD**.
                    """)
            
            # --- GUÍA DIDÁCTICA: FÓRMULAS ---
            with st.expander("📐 Explicación Técnica de las Fórmulas (Aldabón-Gemini 3.0)", expanded=False):
                st.markdown("""
                ## 1. Definición de Variables Base
                
                | Variable | Nombre | Descripción |
                |:--|:--|:--|
                | $V_p$ | **Voto Real 23J** | Porcentaje real obtenido por el partido $p$ en las Elecciones Generales de Julio 2023 sobre el censo de voto válido. |
                | $R_{raw}$ | **Recuerdo Bruto** | Porcentaje de encuestados en el CIS actual que declaran haber votado a $p$ en 2023. |
                | $S_p$ | **Voto+Simpatía** | Intención directa declarada o simpatía explícita hacia el partido $p$ en la encuesta actual. |
                
                ---
                
                ## 2. Algoritmo de Rectificación Aldabón-Gemini
                
                El modelo aplica una función de transformación lineal sobre la intención directa, calibrada por tres factores.
                
                ### A. Normalización del Recuerdo ($R_{norm}$)
                Primero normalizamos el recuerdo bruto eliminando No contesta / No sabe para operar sobre Voto Válido Equivalente:
                
                $$R_{norm,p} = \\frac{R_{raw,p}}{\\sum_{i \\in Partidos} R_{raw,i}} \\times 100$$
                
                ### B. Cálculo del Factor de Corrección ($K_p$)
                Este coeficiente mide la sobredimensionamiento (autocomplacencia) o infra-representación (voto oculto) de cada electorado en la muestra.
                
                $$K_p = \\frac{V_p}{R_{norm,p}}$$
                
                - Si $K_p > 1$: Detectamos **Voto Oculto** (ej. PP/VOX suelen tener $K \\approx 1.3 - 1.6$).
                - Si $K_p < 1$: Detectamos **Sobrerrepresentación** (ej. PSOE suele tener $K \\approx 0.8 - 0.9$).
                
                **Nota:** El factor K se aplica al 100% (sin amortiguación).
                
                ### C. Matriz de Ajuste Fino ($\\Phi_p$ y $\\Lambda_p$)
                Aplicamos correcciones basadas en fidelidad histórica y momentum actual.
                
                | Factor | Descripción | Valores por Defecto |
                |:--|:--|:--|
                | **Φ (Fidelidad)** | Tasa de retención estructural. | $\\Phi = 1.0$ (neutro) |
                | **Λ (Momentum)** | Factor de coyuntura (ajustable por usuario). | $\\Lambda = 1.0$ (neutro) |
                
                ---
                
                ## 3. Fórmula Final de Estimación
                
                La estimación final $E_p$ se calcula proyectando la intención directa corregida por el sesgo muestral y ajustada por los factores de fidelidad y coyuntura:
                
                $$E_p = S_p \\times K_p \\times \\Phi_p \\times \\Lambda_p$$
                
                *Nota: El resultado se re-normaliza finalmente para asegurar que $\\sum E_p = 100\\%$.*
                
                ---
                
                ## 4. Ejemplo Práctico Comparativo
                """)
                
                # Generar ejemplo dinámico con datos reales del estudio
                partido_ejemplo = 'PP'
                if partido_ejemplo not in voto_directo:
                    partido_ejemplo = list(voto_directo.keys())[0] if voto_directo else 'PP'
                
                # Extraer datos reales
                vd_real = voto_directo.get(partido_ejemplo, 0)
                rec_real = recuerdo.get(partido_ejemplo, 0) if recuerdo else 0
                cis_real = estimacion_cis.get(partido_ejemplo, 0)
                gemini_real = aldabon_gemini.get(partido_ejemplo, 0)
                
                # Obtener parámetros usados
                config = estudio.get_context_biases()
                phi_real = config['fidelidad'].get(partido_ejemplo, 1.0)
                lam_real = custom_momentum.get(partido_ejemplo, config['momentum'].get(partido_ejemplo, 1.0))
                
                # Calcular K (sin amortiguación)
                partidos_ref = estudio.get_partidos_referencia()
                v_real = partidos_ref.get(partido_ejemplo, 0)
                sum_rec = sum(recuerdo.values()) if recuerdo else 1
                rec_norm = (rec_real / sum_rec) * 100 if sum_rec > 0 else 0
                k_val = v_real / rec_norm if rec_norm > 0 else 1.0
                
                # Calcular valores intermedios
                e_raw = vd_real * k_val * phi_real * lam_real
                suelo = vd_real  # 100% del VD como suelo
                
                st.markdown(f"""
                Datos reales del **{partido_ejemplo}** en este estudio:
                
                | Dato | Valor |
                |:--|:--|
                | Voto Directo ($S_p$) | {vd_real:.1f}% |
                | Recuerdo Bruto ($R_{{raw}}$) | {rec_real:.1f} (→ {rec_norm:.1f}% normalizado) |
                | Voto Real 2023 ($V_p$) | {v_real:.1f}% |
                | Estimación CIS | {cis_real:.1f}% |
                
                ### Cálculo Aldabón-Gemini 3.0
                
                1. **Factor K**: $K = {v_real:.1f}/{rec_norm:.1f} = {k_val:.2f}$ (aplicado al 100%)
                2. **Fidelidad**: $\\Phi_{{{partido_ejemplo}}} = {phi_real}$
                3. **Momentum**: $\\Lambda_{{{partido_ejemplo}}} = {lam_real:.2f}$ {"(slider ajustado)" if lam_real != config['momentum'].get(partido_ejemplo, 1.0) else "(valor por defecto)"}
                4. **Cálculo bruto**: $E = {vd_real:.1f}\\% \\times {k_val:.2f} \\times {phi_real} \\times {lam_real:.2f} = {e_raw:.1f}\\%$
                5. **Protección Suelo**: $Suelo = {vd_real:.1f}\\%$ (100% del VD)
                6. **Aplicación**: {"Se aplica suelo" if e_raw < suelo else "Se usa valor calculado"} ({max(suelo, e_raw):.1f}%)
                7. **Normalización**: Se ajusta al 100% sobre voto válido (excluyendo Abstención/NSNC).
                
                $$E_{{Final}} = {max(suelo, e_raw):.1f}\\% \\xrightarrow{{Normalización}} \\mathbf{{{gemini_real:.1f}\\%}}$$
                
                | Método | Estimación | Diferencia vs VD |
                |:--|:--|:--|
                | CIS | {cis_real:.1f}% | {cis_real - vd_real:+.1f}% |
                | Aldabón-Gemini | {gemini_real:.1f}% | {gemini_real - vd_real:+.1f}% |
                """)
        else:
            st.warning("No se encontraron datos de partidos en este estudio.")
            
    except Exception as e:
        import traceback
        st.error(f"Error al analizar el estudio: {e}")
        st.code(traceback.format_exc())
else:
    st.info("👈 Selecciona un estudio del sidebar o sube uno nuevo.")

# Footer
st.markdown("---")
st.markdown("*Desarrollado para análisis crítico de la 'cocina' electoral del CIS.*")

