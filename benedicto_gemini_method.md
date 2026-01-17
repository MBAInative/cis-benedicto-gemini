# Método Benedicto-Gemini: Teoría y Aplicación

El método **Benedicto-Gemini** surge como una respuesta técnica a la opacidad y los sesgos observados en el modelo "Alaminos-Tezanos" del Centro de Investigaciones Sociológicas (CIS).

## 1. El Problema del Método Alaminos-Tezanos

El modelo oficial del CIS se basa en una "lógica difusa" (fuzzy logic) y un factor de "inercia-incertidumbre" que nunca ha sido auditado externamente. Los resultados históricos muestran una **sobrestimación sistemática de la izquierda** (en 41 de las últimas 42 elecciones).

### Fallos principales:
- **Cocina de Intencionalidad**: Utiliza variables subjetivas para "adivinar" el voto de los indecisos.
- **Sesgo de Ganador**: Tiende a inflar al partido en el gobierno basándose en una supuesta "inercia" que no se valida con datos reales de transferencia.

## 2. La Solución Benedicto-Gemini

Nuestro método utiliza una **Post-estratificación por Recuerdo de Voto Real**. 

### El Algoritmo:
1. **Identificación de la Muestra**: Tomamos los datos brutos de "Intención de Voto + Simpatía" (Voto Decidido).
2. **Corrección de Representatividad**: 
   - El CIS suele entrevistar a más votantes del PSOE de los que realmente votaron en 2023 (sesgo de autocomplacencia o muestreo).
   - Calculamos un **Factor de Corrección ($k$)** para cada grupo de votantes:
     $$k_r = \frac{\% \text{Voto Real 2023}_r}{\% \text{Recuerdo Voto en Encuesta}_r}$$
3. **Distribución de Indecisos**:
   - En lugar de usar "inercia", distribuimos a los indecisos basándose en sus **matrices de transferencia** (si votaron a A en 2023 y ahora dudan, su probabilidad de ir a B se calcula según la fuga detectada en los decididos de A).

## 3. Ventajas de Benedicto-Gemini
- **Neutralidad**: No asume comportamientos futuros basados en ideología.
- **Transparencia**: El script de Python adjunto permite replicar el cálculo con cualquier Barómetro.
- **Vínculo con la Realidad**: El punto de anclaje siempre es el último resultado electoral verificado (Julio 2023).
