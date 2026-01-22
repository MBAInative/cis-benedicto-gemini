# 🦅 Monitor CIS Aldabón-Gemini

## 🎯 Objetivo del Proyecto
Esta herramienta es un **sistema de auditoría y rectificación demoscópica** diseñado para analizar los estudios del CIS (Centro de Investigaciones Sociológicas) bajo una metodología alternativa a la oficial ("Alaminos-Tezanos").

El objetivo principal es corregir los sesgos sistemáticos (especialmente la sobrerrepresentación de la izquierda y la infravaloración del "Voto Oculto" de derecha) utilizando un modelo de post-estratificación basado en el **Recuerdo de Voto Real del 23J**.

---

## 🛠️ Arquitectura Técnica

El proyecto está construido en **Python** utilizando **Streamlit** para la interfaz web.

### Componentes Principales
1.  **`streamlit_app.py`**: 
    *   Punto de entrada de la aplicación.
    *   Gestiona la UI, los selectores de estudio y la visualización de gráficos (Altair).
    *   Incluye la "Guía Didáctica" y el "Anexo Técnico".
2.  **`cis_analyzer.py`**: 
    *   **Motor Lógico:** Contiene el algoritmo de rectificación Aldabón-Gemini v2.1.
    *   Calcula el **Factor K** (corrección de recuerdo), aplica las **Matrices de Fidelidad** y genera los diccionarios finales de estimación.
    *   Soporta tanto estudios **nacionales** como **autonómicos**.
3.  **`cis_pdf_processor.py`**:
    *   Módulo auxiliar (`pypdf`) encargado de leer los archivos PDF oficiales (`_Estimacion.pdf`).
    *   Esencial para los **Barómetros**, ya que el CIS a menudo separa la estimación final del Excel de datos brutos.
4.  **`cis_data_manager.py`**:
    *   Capa de abstracción de datos. Mapea nombres legibles (ej. "Diciembre 2025") a las rutas físicas de los archivos, gestionando la lógica de búsqueda.

---

## 📂 Estructura de Datos (`data/cis_studies/`)

El sistema implementa una **estrategia híbrida** de carga de datos para adaptarse a los distintos formatos que publica el CIS:

### 1. Avances de Resultados (`xxxx-multi_A.xlsx`)
*   **Contenido:** Todo en un solo Excel.
*   **Lógica:** `cis_analyzer.py` lee tanto el voto crudo (Hoja `Resultados`) como la estimación oficial (Hoja `Estimación de Voto` o `Estimación`) directamente del archivo `.xlsx`.

### 2. Barómetros Definitivos (`xxxx-multi.xlsx` + `xxxx_Estimacion.pdf`)
*   **Contenido:** Excel con datos crudos + PDF con la "cocina" oficial.
*   **Lógica:**
    *   El **Voto+Simpatía** (Input para Aldabón) se extrae del Excel (tabulaciones).
    *   La **Estimación Oficial** (Comparativa) se extrae del PDF mediante `cis_pdf_processor.py`.

### 3. Estudios Autonómicos (Preelectorales Regionales)
*   **Contenido:** Datos de una comunidad autónoma específica.
*   **Lógica:**
    *   Se extraen **TODOS los partidos** (nacionales + regionales como CHA, PAR, TERUEL EXISTE).
    *   El Excel puede contener múltiples tablas (total CCAA + provincias). Se usa **solo la primera tabla** (datos totales).

### Estudios Activos (Enero 2026)
Actualmente el sistema soporta los siguientes estudios:
*   **Febrero 2026** (Estudio 3543) – *Preelectoral Aragón* 🆕
*   **Enero 2026** (Estudio 3540)
*   **Diciembre 2025** (Estudio 3536) – *Requiere PDF*
*   **Noviembre 2025** (Estudio 3530)
*   **Octubre 2025** (Estudio 3528)
*   **Septiembre 2025** (Estudio 3524)

---

## 🧮 Metodología Aldabón-Gemini (Resumen Técnico)

Frente al modelo de Tezanos (basado en Simpatía/Liderazgo), este modelo aplica:

1.  **Normalización del Recuerdo ($R_{norm}$):** Convierte el recuerdo declarado en cuotas sobre voto válido.
2.  **Factor Detector de Mentiras ($K_p$):** 
    $$ K_p = \frac{\% \text{Voto Real 23J}}{\% \text{Recuerdo Declarado}} $$
    *   Si $K > 1$: Detecta **Voto Oculto** (típico en PP/VOX).
    *   Si $K < 1$: Detecta **Sobrerrepresentación** (típico en PSOE).
3.  **Ajuste Multivariable:**
    $$ E_p = S_p \times K_p \times \Phi_p \times \Lambda_p $$
    Donde $\Phi$ es la fidelidad histórica y $\Lambda$ es el factor de liderazgo/coyuntura.

### Diferencias entre Estudios Nacionales y Autonómicos

| Aspecto | Elecciones Generales | Elecciones Autonómicas |
|---------|---------------------|------------------------|
| **Baseline** | Resultados 23J (nacionales) | Sin baseline regional |
| **Factor K** | Calculado desde recuerdo 23J | K=1.0 para partidos regionales |
| **Partidos** | Solo nacionales (PP, PSOE, VOX...) | Todos (+ CHA, PAR, TERUEL EXISTE...) |
| **Corrección** | Completa (K × Φ × Λ) | Parcial (solo Φ × Λ si definidos) |

---

## 🚀 Estado de Despliegue
*   **Repositorio:** GitHub (`Proyectos/CIS`).
*   **Nube:** Streamlit Cloud.
*   **Dependencias:** `requirements.txt` actualizado con `pypdf`, `openpyxl`, `pandas`, `altair`.

## 📝 Notas para Futuros Agentes / Desarrolladores
*   **Mantenimiento:** Al añadir un nuevo estudio mensual, asegurar que se añade tanto al carpeta `data/cis_studies` como al `STUDY_MAP` en `cis_data_manager.py`.
*   **Fragilidad PDF:** La extracción de tablas de PDF usa expresiones regulares (`cis_pdf_processor.py`). Si el CIS cambia drásticamente el formato visual de sus informes PDF, este módulo podría necesitar ajustes.
*   **Estudios Autonómicos:** Los Excel pueden tener múltiples tablas (una por provincia). El parser toma solo la **primera ocurrencia** de cada partido para evitar usar datos provinciales.
*   **Partidos Regionales:** Los partidos sin datos en `voto_real_23` (ej. CHA, PAR) reciben K=1.0 y no se les aplica corrección de recuerdo.

---
*Documento actualizado el 22 de Enero de 2026*

