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
- **Aldabón-Gemini**: Factor K (Recuerdo) + Ajustes de Fidelidad Histórica
- **Aldabón-Claude**: Factor K Puro (Corrección por sesgo de memoria sin aditivos)
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
        
        # Extraer datos
        voto_directo = estudio.extraer_voto_directo()
        estimacion_cis = estudio.extraer_estimacion_cis()
        aldabon_gemini = estudio.calcular_aldabon_gemini()
        aldabon_claude = estudio.calcular_aldabon_claude()
        
        # Determinar partidos a mostrar
        all_parties = set()
        for d in [voto_directo, estimacion_cis, aldabon_gemini, aldabon_claude]:
            all_parties.update(d.keys())
        
        # Filtrar partidos con valores > 0.5%
        # Partidos principales (excluyendo categorías técnicas para el orden base)
        main_parties = sorted([p for p in all_parties 
                         if any(d.get(p, 0) > 0.5 for d in [voto_directo, estimacion_cis, aldabon_gemini, aldabon_claude])
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
            # --- TABLA COMPARATIVA ---
            st.subheader("📊 Tabla Comparativa de Métodos")
            
            table_data = {
                'Categoría': parties,
                'Voto Directo (Crudo)': [voto_directo.get(p, 0) for p in parties],
                'Estimación CIS': [estimacion_cis.get(p, 0) if p in cats_estimacion else 0 for p in parties],
                'Aldabón-Gemini': [aldabon_gemini.get(p, 0) if p in cats_estimacion else 0 for p in parties],
                'Aldabón-Claude': [aldabon_claude.get(p, 0) if p in cats_estimacion else 0 for p in parties],
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
                    'Aldabón-Claude': '{:.1f}%',
                    'Diff (Gemini - CIS)': '{:+.1f}%'
                }).applymap(
                    lambda v: 'color: green' if v > 0 else 'color: red' if v < 0 else '',
                    subset=['Diff (Gemini - CIS)']
                ),
                use_container_width=True
            )
            
            # --- GRÁFICO DE BARRAS ---
            st.subheader("📈 Comparativa Visual")
            
            # Preparar datos para gráfico
            chart_data = []
            for p in parties[:10]:  # Top 10 partidos
                chart_data.append({'Partido': p, 'Método': 'Voto Directo', 'Valor': voto_directo.get(p, 0)})
                chart_data.append({'Partido': p, 'Método': 'Estimación CIS', 'Valor': estimacion_cis.get(p, 0)})
                chart_data.append({'Partido': p, 'Método': 'Aldabón-Gemini', 'Valor': aldabon_gemini.get(p, 0)})
                chart_data.append({'Partido': p, 'Método': 'Aldabón-Claude', 'Valor': aldabon_claude.get(p, 0)})
            
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
            with st.expander("🎓 Explicación de los Métodos (Aldabón-Gemini 2.6)"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    ### Método Alamino-Tezanos (CIS)
                    - Usa **Lógica Difusa**: Asigna indecisos según simpatía o cercanía.
                    - **Efecto Inercia**: El recuerdo histórico pesa mucho más que la intención directa.
                    - Suele favorecer ligeramente a los partidos de la coalición de gobierno.
                    """)
                    
                    st.markdown("""
                    ### Método Aldabón-Gemini (v2.6)
                    - **Inference Engine**: Detecta automáticamente ruralidad y polarización del estudio.
                    - **Recall Bias Sensor**: Detecta si la muestra está "inflada" con votantes de un bloque.
                    - **Protección de Suelo**: Nunca estima por debajo del **90% del Voto Directo** declarado.
                    """)
                
                with col2:
                    st.markdown("""
                    ### Voto Directo (Crudo)
                    - Es la intención de voto declarada por el ciudadano en la encuesta.
                    - Representa el **"suelo de realidad"** del que parte el modelo.
                    - No incluye corrección técnica por mentira o falta de recuerdo.
                    """)
                    
                    st.markdown("""
                    ### Método Aldabón-Claude
                    - **K-Factor Amortiguado (0.40)**: Equilibra recuerdo e intención actual.
                    - **Modelo Estático**: No aplica penalizaciones por sesgo de muestra.
                    - La predicción más conservadora basada estrictamente en la declaración.
                    """)
            
            # --- GUÍA DIDÁCTICA: FÓRMULAS ---
            with st.expander("📐 Explicación Técnica de las Fórmulas (Aldabón-Gemini 2.6)", expanded=False):
                st.markdown("""
                ## ¿Cómo se "cocina" una encuesta? (Nivel Bachillerato)
                
                Para que veas cómo funciona la cocina, vamos a usar los mismos datos para los tres modelos con el **"Partido de la Esperanza" (PE)**:
                
                *   **Voto Directo (VD)**: **20%** (lo que dicen hoy).
                *   **Recuerdo de Voto (RV)**: **25%** (lo que dicen que votaron en 2023).
                *   **Voto Real 2023 (VR)**: **20%** (lo que votaron de verdad).
                *   **Indecisos (ID)**: **15%**.
                
                ---
                
                ### 1. Modelo Alamino-Tezanos (CIS)
                **Lógica**: Suma los indecisos según su simpatía.
                *   **Paso 1**: Mira a los indecisos (15%) y ve que 1 de cada 3 (33%) simpatiza con el PE.
                *   **Paso 2 (Cálculo)**: $20\\% (VD) + (15\\% (ID) \\times 0.33) = 20\\% + 5\\%$
                *   **Resultado Final**: **25.0%**
                *   *¿Qué ha pasado?*: El modelo ha "rescatado" a los indecisos y los ha sumado al partido.
                
                ---
                
                ### 2. Modelo Aldabón-Claude (Matemático)
                **Lógica**: Corrige el error de memoria usando el **Factor K**.
                *   **Paso 1 (Error de Memoria)**: La gente dice que votó 25% pero fue un 20%. El error es $20 / 25 = 0.8$.
                *   **Paso 2 (Amortiguación)**: No aplicamos el error a lo bruto, usamos un factor de 0.40.
                    $K = 1 + (0.8 - 1) \\times 0.40 = 1 - 0.08 = 0.92$.
                *   **Paso 3 (Cálculo)**: $20\\% (VD) \\times 0.92 = 18.4\\%$.
                *   **Resultado Final**: **18.4%**
                *   *¿Qué ha pasado?*: Al detectar que la muestra estaba "inflada" de ex-votantes de ese partido, ha bajado la estimación para ser realistas.
                
                ---
                
                ### 3. Modelo Aldabón-Gemini 2.6 (Inteligente)
                **Lógica**: Usa el Factor K + Sensor de Sesgo + Suelo de Protección.
                *   **Paso 1 (Capa Base)**: Parte del cálculo de Claude ($18.4\\%$).
                *   **Paso 2 (Sensor de Sesgo)**: Como el sesgo de recuerdo es alto ($25/20 = 1.25$), Gemini sospecha desmovilización y aplica una penalización de fidelidad del 3% ($0.97$).
                    $18.4\\% \\times 0.97 = 17.85\\%$.
                *   **Paso 3 (Protección de Suelo)**: Gemini mira el Voto Directo (20%) y aplica la regla del 90%.
                    $Suelo = 20\\% \\times 0.90 = 18.0\\%$.
                *   **Paso 4 (Comparación)**: Como $17.85\\%$ es menor que el suelo ($18.0\\%$), el modelo **protege el voto confesado**.
                *   **Resultado Final**: **18.0%**
                *   *¿Qué ha pasado?*: Gemini detectó el sesgo pero, por sentido común sociológico, no permitió que el partido bajara de su suelo de realidad.
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

