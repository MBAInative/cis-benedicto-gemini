# CIS Monitor - Guía Técnica de Implementación

Este documento resume el conocimiento técnico acumulado sobre la estructura de los datos del CIS para facilitar el mantenimiento y evolución del proyecto.

## 1. Tipos de Estudios y Estructura de Archivos

| Tipo de Estudio | Fuente de Datos | Característica Principal |
| :--- | :--- | :--- |
| **Barómetro Nacional** | Excel + PDF externo | La estimación suele estar solo en el PDF (columna "voto válido"). |
| **Avance Generales** | Excel | Todo está en el Excel (Hoja "Estimación de Voto" o "Resultados"). |
| **Avance Autonómico** | Excel | Detectado por la presencia de la hoja "RV EA23" y menciones en la ficha técnica. |

## 2. Estructura de las Hojas de Excel

### Ficha Técnica
*   **Referencia**: Buscada por patrón regex `35\d{2}`.
*   **Campo (Fechas)**: Patrón regex para rangos "Del X al Y de Mes".
*   **Ámbito**: Detectado analizando el texto (Nacional, Aragón, Extremadura).

### Hojas de Resultados (Especialidad Autonómica)
En estudios autonómicos (ej. 3538), no existe hoja de "Estimación". Se usa la hoja `Resultados [Comunidad]`.
*   **Voto Directo**: Extraído de la pregunta de intención de voto espontánea (ej. P11R). **CRÍTICO**: Excluir tablas marcadas como "RECODIFICADA" o "SIMPATÍA" para obtener el voto crudo del boletín.
*   **Estimación**: Si existe, suele estar en una columna lateral (Col 3) de la tabla recodificada por simpatía.

### Hoja Estimación de Voto (Nacionales)
*   **Columna 0**: Nombre del partido o categoría (Blank, Nulo, etc.).
*   **Columna 1**: Voto Directo (Crudo sobre censo).
*   **Columna 3**: Estimación CIS (Sobre voto válido).

## 3. Lógica de "Cocina" Aldabón

### Diferenciación Gemini vs Claude
*   **Aldabón-Gemini**: `Estimación = VD * K * Ajuste_Fidelidad`.
*   **Aldabón-Claude**: `Estimación = VD * K` (Factor K puro).

### Factor K (Corrección de Sesgo)
`K = Voto_Real_Referencia / Recuerdo_Encuesta`
*   Corrige el sesgo de memoria de los encuestados.
*   Si el PP tuvo 33% real pero solo 25% de los encuestados dicen haberle votado, K = 1.32.

### Normalización Crítica
Para que las estimaciones sean realistas:
1.  Se aplica la fórmula a cada partido.
2.  **IMPORTANTE**: Se excluyen categorías de no-voto (NS, NC, Abstención) antes de normalizar.
3.  Se redistribuyen los valores para que el sumatorio de **Partidos Políticos** sea exactamente **100%**.

## 4. Notas para Futuros Desarrolladores

*   **Regex de PDF**: El CIS cambia a veces el formato. Los patrones deben ser flexibles para saltar el margen de error `±X.X`.
*   **Simpatía vs Intención**: En el Voto Directo mostrado al usuario, siempre priorizar la intención espontánea. La simpatía es parte de la "cocina".
*   **Partidos Locales**: El mapeo en `_normalizar_partido` debe actualizarse con cada nueva comunidad (ej. variantes de Podemos/IU en Extremadura).
