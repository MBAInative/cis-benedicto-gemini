
import streamlit as st
import pandas as pd
import altair as alt
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(__file__))

# Import modules
try:
    from cis_data_manager import list_available_studies, get_study_file
    from cis_analyzer import analyze_cis_professional
except ImportError as e:
    st.error(f"Error importando módulos locales: {e}. Verifique que cis_data_manager.py y cis_analyzer.py están en la carpeta.")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="CIS Monitor: Benedicto-Gemini",
    page_icon="⚖️",
    layout="wide"
)

# Título y Descripción
st.title("⚖️ CIS Monitor: Estimación Benedicto-Gemini")
st.markdown("""
**Análisis Rectificado del Barómetro CIS**

Este dashboard compara los datos oficiales del CIS (Tezanos) con la estimación rectificada utilizando el método **Benedicto-Gemini**, 
que aplica corrección por **Recuerdo de Voto Real** y matrices de transferencia de fidelidad.
""")

# --- CONFIGURACIÓN Y SELECTOR ---
st.sidebar.header("🗄️ Histórico de Estudios")

# 1. Selector de Barómetro
available_studies = list_available_studies()
selected_study_name = st.sidebar.selectbox("Seleccionar Estudio:", available_studies)

# 2. Carga y Análisis Dinámico
with st.spinner(f"Cargando datos de {selected_study_name}..."):
    file_path, status_msg = get_study_file(selected_study_name)
    
    if file_path:
        # Analizar archivo local
        results = analyze_cis_professional(file_path)
        
        if results:
            benedicto_data = results['benedicto']
            official_data = results['official']
            raw_data = results['raw']
            
            # Fill missing keys with 0
            all_labels = list(benedicto_data.keys())
            for d in [benedicto_data, official_data, raw_data]:
                for l in all_labels:
                    if l not in d: d[l] = 0.0
            
            labels = all_labels
            success_load = True
        else:
            st.error("Error analizando el archivo Excel. Verifique el formato.")
            success_load = False
            
    else:
        # Archivo no encontrado -> Mostrar instrucciones
        st.warning(f"⚠️ {status_msg}")
        success_load = False

if not success_load:
    st.info("Por favor descarga el archivo y colócalo en la carpeta `data/cis_studies` para continuar.")
    st.stop()



# --- KPIs (Dinámicos) ---
col1, col2, col3 = st.columns(3)
with col1:
    sesgo_psoe = official_data['PSOE'] - benedicto_data['PSOE']
    st.metric(
        label="Sesgo Tezanos (PSOE)",
        value=f"{sesgo_psoe:+.1f}%",
        delta="Sobrestimación CIS" if sesgo_psoe > 0 else "Subestimación",
        delta_color="inverse"
    )

with col2:
    voto_oculto_pp = benedicto_data['PP'] - raw_data['PP']
    st.metric(
        label="Voto Oculto (PP)",
        value=f"{voto_oculto_pp:+.1f}%",
        help="Diferencia entre intención directa y estimación final"
    )

with col3:
    st.metric(
        label="Indecisos Distribuidos",
        value="~15%",
        help="Basado en matrices de transferencia"
    )

# --- GRÁFICO COMPARATIVO ---
# --- GRÁFICO COMPARATIVO ---
st.subheader(f"Estimación {selected_study_name}")

# Crear DataFrame para el gráfico (Sin 40dB)
chart_data = []
for p in labels:
    if benedicto_data.get(p,0) > 0.5: # Show significant only
        chart_data.append({'Partido': p, 'Estimación (%)': raw_data.get(p,0), 'Método': '1. Voto Directo'})
        chart_data.append({'Partido': p, 'Estimación (%)': official_data.get(p,0), 'Método': '2. Alamino-Tezanos (CIS)'})
        chart_data.append({'Partido': p, 'Estimación (%)': benedicto_data.get(p,0), 'Método': '3. Benedicto-Gemini'})

df_chart = pd.DataFrame(chart_data)

import altair as alt

# Gráfico de barras agrupadas MEJORADO (Estilo Clásico)
base = alt.Chart(df_chart).encode(
    x=alt.X('Partido:N', axis=alt.Axis(title=None, labelAngle=-45)),
)

bar = base.mark_bar().encode(
    y=alt.Y('Estimación (%)', title='Estimación de Voto (%)'),
    color=alt.Color('Método:N', legend=alt.Legend(title="Modelo", orient="top")),
    xOffset=alt.XOffset('Método:N'), # Desplazamiento para agrupar
    tooltip=['Partido', 'Estimación (%)', 'Método']
)

chart = bar.properties(
    height=500
).configure_view(
    stroke='transparent'
)

st.altair_chart(chart, use_container_width=True)

# --- TABLA DE DATOS ---
st.subheader("Datos Detallados")
table_df = pd.DataFrame({
    'Partido': labels,
    'Voto Directo': [raw_data.get(p,0) for p in labels],
    'Alamino-Tezanos': [official_data.get(p,0) for p in labels],
    'Benedicto-Gemini': [benedicto_data.get(p,0) for p in labels],
})
# Calculate diff
table_df['Diferencia (Ben vs CIS)'] = table_df['Benedicto-Gemini'] - table_df['Alamino-Tezanos']

st.dataframe(
    table_df.style.format("{:.1f}%", subset=['Voto Directo', 'Alamino-Tezanos', 'Benedicto-Gemini', 'Diferencia (Ben vs CIS)'])
    .applymap(lambda v: 'color: red' if v < 0 else 'color: green', subset=['Diferencia (Ben vs CIS)'])
)

# --- METODOLOGÍA ---
# --- METODOLOGÍA ---
with st.expander("ℹ️ Metodología Detallada: Alamino-Tezanos vs Benedicto-Gemini", expanded=True):
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("### 🔵 Alamino-Tezanos (Oficial CIS)")
        st.info("""
        **Modelo Bifactorial Inercia-Incertidumbre (2019)**
        
        Es el método oficial implantado por José Félix Tezanos.
        
        1. **Base**: Parte de la Intención Directa de Voto + Simpatía.
        2. **Imputación de Indecisos**: 
           - **Inercia**: Asume que el votante tiende a repetir su voto anterior.
           - **Incertidumbre**: Distribuye a los "No sabe" basándose en variables subjetivas como la valoración de líderes o la cercanía ideológica.
        3. **Sesgo Conocido**: Al asignar indecisos basándose fuertemente en la "simpatía" del momento, tiende a **sobreestimar** a los partidos de izquierda (PSOE) cuando estos tienen alta visibilidad, ignorando el "voto oculto" o vergonzante de la derecha.
        """)

    with col_b:
        st.markdown("### 🟣 Benedicto-Gemini (Rectificación)")
        st.success("""
        **Modelo de Rectificación por Fidelidad y Recuerdo**
        
        Método correctivo diseñado para neutralizar el sesgo muestral del CIS.
        
        1. **Corrección de Muestra (Factor $k$)**:
           - Corrección normalizada por Voto Válido para evitar sesgo de participación.
           - $$k_p = \\frac{\\% \\text{Voto Real 23J}_p}{\\% \\text{Recuerdo Recalibrado}_p}$$
        2. **Matrices de Transferencia (Fidelidad)**:
           - Ajuste fino por partido (PSOE fidelidad reforzada, PP normalizada).
        3. **Factor Liderazgo/Tendencia (Multivariable)**:
           - Incorporamos criterios tipo 40dB:
           - **Bonus Presidencial**: Plus por valoración de líder (PSOE).
           - **Trend**: Corrección por momento de campaña y viralidad (SALF).
        """)
    
    st.caption("Análisis generado por el motor Benedicto-Gemini v2.0 (Multivariable) | Datos base: Estudio CIS 3540")


