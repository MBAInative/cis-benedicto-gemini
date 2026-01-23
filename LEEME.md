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

## 🏛️ Soporte de Estudios Autonómicos y Metadatos

El sistema maneja la complejidad de los estudios regionales e incluye metadatos detallados para cada sondeo:

*   **Identificación Automática:** Extrae partidos regionales (CHA, PAR, TERUEL EXISTE) y normaliza coaliciones.
*   **Tratamiento de Datos:** Prioriza tablas agregadas (Total CCAA) sobre desgloses provinciales.
*   **Panel de Información:** El panel lateral muestra ahora datos críticos de la ficha técnica:
    *   **Referencia Electoral:** (Generales / Autonómicas).
    *   **Muestra (N):** Tamaño de la muestra (ej: 3.313 entrevistas).
    *   **Trabajo de Campo:** Fechas exactas del sondeo.

---

## 🛠️ Notas de Estabilidad y Despliegue (Cloud)

Para asegurar el funcionamiento en **Streamlit Cloud (Debian/Linux)**, se han implementado las siguientes mejoras de robustez:

1.  **Compatibilidad de Encoding:** Eliminados hacks de consola dependientes de Windows que bloqueaban el arranque en Linux.
2.  **Gestión de Permisos:** La creación de directorios temporales y archivos de auditoría está protegida para entornos con sistemas de archivos de solo lectura.
3.  **Depuración de Dependencias:** `requirements.txt` optimizado con versiones específicas y librerías necesarias para el renderizado de tablas (`jinja2`).
4.  **Blindaje de Arranque:** Sistema de diagnóstico integrado que captura y muestra errores de importación detallados en lugar de fallos genéricos.

---

## 🚀 Despliegue y Uso
*   **Local:** `streamlit run streamlit_app.py`
*   **Cloud:** Despliegue automático en Streamlit Cloud vía GitHub.
*   **Datos:** Los estudios deben colocarse en `data/cis_studies/` siguiendo la nomenclatura `ID-multi_A.xlsx`.

---
*Documento actualizado: 23 de Enero de 2026*
