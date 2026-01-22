# 🦅 Monitor CIS Aldabón-Gemini

## 🎯 Objetivo del Proyecto
Esta herramienta es un **sistema de auditoría y rectificación demoscópica** diseñado para analizar los estudios del CIS (Centro de Investigaciones Sociológicas) bajo una metodología alternativa a la oficial ("Alaminos-Tezanos").

El objetivo principal es corregir los sesgos sistemáticos utilizando un modelo de post-estratificación basado en el **Recuerdo de Voto Real**.

---

## 🛠️ Arquitectura Técnica

### Componentes Principales
1.  **`streamlit_app.py`**: Interfaz de usuario dinámica y visualización.
2.  **`cis_analyzer.py`**: Motor lógico con el algoritmo Aldabón-Gemini v2.2.
    *   **Universalidad:** Soporta barómetros nacionales y preelectorales autonómicos.
    *   **Robustez:** Maneja variaciones en los formatos de Excel del CIS (nombres de hojas, estructuras de tablas).
3.  **`cis_data_manager.py`**: Gestión de rutas y mapeo de estudios históricos.

---

## 🧮 Metodología Aldabón-Gemini

El modelo aplica una rectificación profesional basada en el comportamiento electoral histórico:

1.  **Factor Detector de Mentiras ($K$):** Ajusta la muestra según la desviación entre el recuerdo de voto declarado y los resultados reales del 23J.
    $$ K = \frac{\% \text{Voto Real}}{\% \text{Recuerdo Normalizado}} $$
2.  **Ajuste por Fidelidad y Liderazgo:** Aplica matrices de transferencia basadas en la solidez estructural de cada electorado.
3.  **Extracción Multi-Nivel:** Capacidad de distinguir entre datos agregados (CCAA Total) y desgloses provinciales en el mismo archivo.

---

## 🏛️ Soporte de Estudios Autonómicos (Nuevo)

El sistema ha sido actualizado para manejar la complejidad de los estudios preelectorales regionales (Ej: **Aragón 3543**):

*   **Detección de Partidos Regionales:** Identifica y extrae automáticamente partidos como CHA, TERUEL EXISTE o PAR.
*   **Tratamiento Diferenciado:** 
    *   Partidos Nacionales: Mantienen su Factor K histórico.
    *   Partidos Regionales: Se analiza su fuerza directa con ajustes de fidelidad local.
*   **Normalización Inteligente:** Agrupa coaliciones (Ej: IU-MOVIMIENTO SUMAR -> SUMAR) para comparativas coherentes.

---

## 🚀 Despliegue y Uso
*   **Local:** `streamlit run streamlit_app.py`
*   **Cloud:** Despliegue automático en Streamlit Cloud vía GitHub.
*   **Datos:** Los estudios deben colocarse en `data/cis_studies/` siguiendo la nomenclatura `ID-multi_A.xlsx`.

---
*Documento actualizado: 22 de Enero de 2026*
