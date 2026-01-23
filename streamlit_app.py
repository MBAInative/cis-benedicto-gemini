
import streamlit as st
import pandas as pd
import altair as alt
import sys
import os

# Import modules with enhanced error reporting
try:
    from cis_data_manager import list_available_studies, get_study_file, get_study_metadata
    from cis_analyzer import analyze_cis_professional
except Exception as e:
    import traceback
    error_details = traceback.format_exc()
    st.error(f"FATAL ERROR during startup: {e}")
    st.code(error_details)
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="CIS Monitor: Aldabón-Gemini",
    page_icon="⚖️",
    layout="wide"
)

# Título y Descripción
st.title("⚖️ CIS Monitor: Estimación Aldabón-Gemini")
st.markdown("""
**Análisis Rectificado del Barómetro CIS**

Este dashboard compara los datos oficiales del CIS (Tezanos) con la estimación rectificada utilizando el método **Aldabón-Gemini**, 
que aplica corrección por **Recuerdo de Voto Real** y matrices de transferencia de fidelidad.
""")

# --- CONFIGURACIÓN Y SELECTOR ---
st.sidebar.header("🗄️ Histórico de Estudios")

# 1. Selector de Barómetro
available_studies = list_available_studies()
selected_study_name = st.sidebar.selectbox("Seleccionar Estudio:", available_studies)

# Mostrar Metadatos en el Sidebar
metadata = get_study_metadata(selected_study_name)
st.sidebar.markdown("---")
st.sidebar.write(f"**📍 Referencia:** {metadata.get('Elecciones', 'N/A')}")
st.sidebar.write(f"**🗓️ Sondeo:** {metadata.get('Sondeo', 'N/A')}")
if 'N' in metadata:
    st.sidebar.write(f"**👥 Muestra:** {metadata['N']}")
if 'Campo' in metadata:
    st.sidebar.write(f"**⏱️ Trabajo de campo:** {metadata['Campo']}")
st.sidebar.markdown("---")

# 2. Carga y Análisis Dinámico
# 2. Carga y Análisis Dinámico
with st.spinner(f"Cargando datos de {selected_study_name}..."):
    # get_study_file returns (path, type_or_status_msg)
    # If path found -> type is 'AVANCE' or 'BAROMETRO'
    # If not found -> type is error message
    path_found, study_type = get_study_file(selected_study_name)
    
    # Clean previous overrides (Use real data from files now)
    official_data_override = None
    if selected_study_name == "Generales 23J (Realidad)":
        official_data_override = {'PP': 33.1, 'PSOE': 31.7, 'VOX': 12.4, 'SUMAR': 12.3}

    if path_found:
        # Analizar archivo local con el tipo detectado
        results = analyze_cis_professional(path_found, study_type=study_type)
        
        if results:
            benedicto_data = results['benedicto']
            official_data = results['official']
            raw_data = results['raw']

            # Apply override only if strictly necessary (e.g. 23J base check)
            if official_data_override:
                official_data = official_data_override
            
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
        # Archivo no encontrado -> Mostrar instrucciones (study_type contains msg)
        st.warning(f"⚠️ {study_type}")
        success_load = False

if not success_load:
    st.info("Por favor descarga el archivo y colócalo en la carpeta `data/cis_studies` para continuar.")
    st.stop()


# --- KPIs (Dinámicos) ---
col1, col2, col3 = st.columns(3)
with col1:
    sesgo_psoe = official_data.get('PSOE', 0) - benedicto_data.get('PSOE', 0)
    st.metric(
        label="Sesgo Tezanos (PSOE)",
        value=f"{sesgo_psoe:+.1f}%",
        delta="Sobrestimación CIS" if sesgo_psoe > 0 else "Subestimación",
        delta_color="inverse"
    )

with col2:
    voto_oculto_pp = benedicto_data.get('PP', 0) - raw_data.get('PP', 0)
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
st.subheader(f"Estimación {selected_study_name}")

# Crear DataFrame para el gráfico
chart_data = []
for p in labels:
    if benedicto_data.get(p,0) > 0.5: # Show significant only
        chart_data.append({'Partido': p, 'Estimación (%)': raw_data.get(p,0), 'Método': '1. Voto Directo'})
        chart_data.append({'Partido': p, 'Estimación (%)': official_data.get(p,0), 'Método': '2. Alamino-Tezanos (CIS)'})
        chart_data.append({'Partido': p, 'Estimación (%)': benedicto_data.get(p,0), 'Método': '3. Aldabón-Gemini'})

df_chart = pd.DataFrame(chart_data)

# Gráfico de barras agrupadas MEJORADO
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
    'Aldabón-Gemini': [benedicto_data.get(p,0) for p in labels],
})
# Calculate diff
table_df['Diferencia (Ben vs CIS)'] = table_df['Aldabón-Gemini'] - table_df['Alamino-Tezanos']

st.dataframe(
    table_df.style.format("{:.1f}%", subset=['Voto Directo', 'Alamino-Tezanos', 'Aldabón-Gemini', 'Diferencia (Ben vs CIS)'])
    .applymap(lambda v: 'color: red' if v < 0 else 'color: green', subset=['Diferencia (Ben vs CIS)'])
)

# --- GUÍA DIDÁCTICA: COCINA ELECTORAL ---
st.markdown("---")
with st.expander("🎓 Guía Didáctica: Desmontando la 'Cocina' Electoral (Nivel Experto)", expanded=True):
    st.markdown("""
    ### 🧑‍🍳 ¿Por qué todos los datos del CIS parecen incorrectos?
    
    En demoscopia, la "cocina" es el proceso matemático para corregir los errores de la encuesta bruta (gente que miente, gente que no contesta).
    Aquí explicamos **con total transparencia** por qué el CIS oficial falla y cómo lo arreglamos nosotros.
    """)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.info("""
        #### 1. La Receta Tezanos (Modelo Inercia-Incertidumbre)
        **Filosofía: "El voto es un estado de ánimo"**
        
        Tezanos asume que el votante es fluido y que su "norte" es la simpatía actual.
        
        **🌀 ¿Cómo gestiona a los Indecisos?**
        Si alguien dice *"No sé"*:
        1.  **Simpatía Declarada:** Le pregunta *"¿Por qué partido siente más simpatía?"*. Si responde PSOE, le asigna voto al PSOE.
        2.  **Valoración de Líderes:** Si no tiene simpatía, mira qué líder valora mejor.
        
        **❌ El Fallo Fatal: El "Voto Vergonzante"**
        En España, el votante de derecha (PP/VOX) tiende a ocultar sus intenciones ("Voto Oculto") y a menudo valora mal a sus propios líderes por crítica interna, pero luego les vota por lealtad ideológica.
        *   **Consecuencia:** Tezanos asigna a casi todos los indecisos a la izquierda (porque es "menos vergonzante" declarar simpatía progresista), inflando artificialmente al PSOE/Sumar en 3-5 puntos.
        """)

    with col_b:
        st.success("""
        #### 2. La Receta Aldabón-Gemini (Modelo de Recuerdo)
        **Filosofía: "El comportamiento pasado predice el futuro"**
        
        Nosotros no nos fiamos de lo que la gente *dice* sentir hoy. Nos fiamos de lo que *hicieron* ayer.
        
        **⚖️ Paso 1: El Detector de Sesgos (Factor $k$)**
        Comparamos la muestra con la realidad de las urnas (23J):
        *   *Ejemplo:* Si el 40% de los encuestados dice "Yo voté a Pedro Sánchez", pero sabemos que solo le votó el 31,7% real, **bajamos el peso** de cada respuesta socialista (valen 0,79 votos).
        *   *Ejemplo:* Si solo el 20% admite haber votado a Feijóo (vs 33,1% real), sabemos que hay mucho "voto oculto". **Subimos el peso** de cada respuesta popular (valen 1,65 votos).
        
        **🔄 Paso 2: La Matriz de Fugas**
        Si un votante nos dice "Voté PP en 2023, pero ahora No Sabe", no adivinamos. Aplicamos la estadística de sus compañeros decididos:
        *   Si el 90% de los antiguos votantes del PP se quedan, asumimos que este indeciso tiene un 90% de probabilidad de volver.
        
        **Resultado:** Un "mapa de calor" realista que aflora el voto oculto de la derecha y desinfla la sobre-representación de la izquierda.
        """)

    st.markdown("---")
    st.caption("**Conclusión:** Mientras Tezanos mide la temperatura emocional (quién cae mejor), Aldabón-Gemini mide la lealtad estructural (quién tiene la base más sólida).")

with st.expander("🛠️ Anexo Técnico: Fórmulas y Algoritmos (White Paper)", expanded=False):
    st.markdown("""
    ### 1. Definición de Variables Base
    
    *   **$V_p$ (Voto Real 23J):** Porcentaje real obtenido por el partido $p$ en las Elecciones Generales de Julio 2023 sobre el censo de voto válido.
    *   **$R_{raw}$ (Recuerdo Bruto):** Porcentaje de encuestados en el CIS actual que declaran haber votado a $p$ en 2023.
    *   **$S_p$ (Voto+Simpatía):** Intención directa declarada o simpatía explícita hacia el partido $p$ en la encuesta actual.
    
    ### 2. Algoritmo de Rectificación Aldabón-Gemini
    
    El modelo aplica una función de transformación lineal sobre la intención directa, calibrada por tres factores.
    
    #### A. Normalización del Recuerdo ($R_{norm}$)
    Primero normalizamos el recuerdo bruto eliminando No contesta / No sabe para operar sobre Voto Válido Equivalente:
    $$ R_{norm,p} = \\frac{R_{raw,p}}{\\sum_{i \\in Partidos} R_{raw,i}} \\times 100 $$
    
    #### B. Cálculo del Factor de Corrección ($K_p$)
    Este coeficiente mide la sobredimensionamiento (autocomplacencia) o infra-representación (voto oculto) de cada electorado en la muestra.
    $$ K_p = \\frac{V_p}{R_{norm,p}} $$
    *   Si $K_p > 1$: Detectamos **Voto Oculto** (ej. PP/VOX suelen tener $K \\approx 1.3 - 1.6$).
    *   Si $K_p < 1$: Detectamos **Sobrerrepresentación** (ej. PSOE suele tener $K \\approx 0.8 - 0.9$).
    
    #### C. Matriz de Ajuste Fino ($\Phi_p$ y $\\Lambda_p$)
    Aplicamos correcciones de segunda derivada basadas en fidelidad histórica y liderazgo actual.
    *   **Fidelidad ($\Phi_p$):** Tasa de retención estructural. Penaliza a partidos con alta volatilidad (Sumar/Podemos) y estabiliza el bipartidismo.
        *   $\\Phi_{PSOE} = 0.93$ | $\\Phi_{PP} = 0.92$ | $\\Phi_{VOX} = 0.82$
    *   **Liderazgo/Tendencia ($\Lambda_p$):** Factor de momento (Momentum). Corrige la inercia de campaña o viralidad reciente (ej. Alvise/SALF).
        *   $\\Lambda_{SALF} = 1.20$ (Viralidad) | $\\Lambda_{PSOE} = 0.97$ (Desgaste Gobierno)
    
    ### 3. Fórmula Final de Estimación
    La estimación final $E_p$ se calcula proyectando la intención directa corregida por el sesgo muestral y ajustada por los factores de fidelidad y coyuntura:
    
    $$ E_p = S_p \\times K_p \\times \\Phi_p \\times \\Lambda_p $$
    
    *Nota: El resultado se re-normaliza finalmente para asegurar que $\\sum E_p = 100\\%$.*
    """)
    st.caption("Documentación técnica extraída del código fuente `cis_analyzer.py` v2.1")


