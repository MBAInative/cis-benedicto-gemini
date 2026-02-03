# Parámetros y Coeficientes del Modelo Aldabón-Gemini

## Introducción

El modelo Aldabón-Gemini es un sistema de estimación electoral que transforma los datos "crudos" de una encuesta del CIS en una predicción de voto. Este documento explica los parámetros y coeficientes utilizados a un nivel accesible.

---

## 1. Parámetros de Entrada (Datos Objetivos)

Estos datos se extraen directamente de la encuesta del CIS:

### 1.1 Voto Directo (VD)
**¿Qué es?** La respuesta a la pregunta "¿A qué partido votaría usted si mañana hubiera elecciones?"

**Ejemplo del estudio 3524:**
| Partido | Voto Directo |
|---------|-------------|
| PSOE | 23.7% |
| PP | 16.4% |
| VOX | 12.8% |
| SUMAR | 5.6% |

> **Nota importante:** El CIS muestra sistemáticamente más Voto Directo para el PSOE que para el PP, aunque otros sondeos muestran lo contrario.

---

### 1.2 Recuerdo de Voto (R)
**¿Qué es?** La respuesta a la pregunta "¿A qué partido votó usted en las últimas elecciones?"

**Ejemplo del estudio 3524:**
| Partido | Recuerdo Bruto | Recuerdo Normalizado |
|---------|----------------|---------------------|
| PSOE | 38.4% | 38.4% |
| PP | 24.9% | 24.9% |

**¿Para qué sirve?** Nos permite detectar si los votantes de un partido están **sobre-representados** o **infra-representados** en la muestra.

---

### 1.3 Simpatía
**¿Qué es?** La respuesta a la pregunta "Sin tener en cuenta su voto, ¿hacia qué partido siente más simpatía?"

Actualmente no se usa directamente, pero podría incorporarse como factor de "crecimiento potencial".

---

## 2. Coeficientes Calculados

### 2.1 Factor de Corrección K

**Fórmula:**
$$K_p = \frac{V_{real,p}}{R_{norm,p}}$$

Donde:
- $V_{real}$ = Resultado real en las elecciones de 2023
- $R_{norm}$ = Recuerdo de voto normalizado

**Interpretación:**
- **K > 1**: Voto oculto (el partido está infra-representado en la muestra)
- **K < 1**: Sobre-representación (el partido está sobre-representado)
- **K = 1**: Representación fiel

**Ejemplo del estudio 3524:**

| Partido | Resultado 2023 | Recuerdo Norm | K | Interpretación |
|---------|----------------|---------------|---|----------------|
| PP | 33.1% | 24.9% | **1.33** | Voto oculto (+33%) |
| PSOE | 31.7% | 38.4% | **0.83** | Sobre-representado (-17%) |
| VOX | 12.4% | 12.6% | **0.98** | Representación fiel |

**¿Cómo se lee?** El K del PP es 1.33, lo que significa que por cada 100 personas que dicen recordar haber votado al PP, en realidad votaron 133. Hay "voto oculto" o vergonzante.

---

### 2.2 Fidelidad (Φ - Phi)

**¿Qué es?** La proporción de votantes de un partido que mantendrán su voto en las próximas elecciones.

**Valores actuales:** Todos en 1.0 (neutros). Podrían ajustarse si hay datos históricos de transferencia de voto.

**Ejemplo conceptual:**
- Φ = 0.80: El 80% de los votantes de 2023 repetirán voto
- Φ = 1.00: El 100% repetirán (neutro)

---

### 2.3 Momentum (Λ - Lambda)

**¿Qué es?** Un factor subjetivo que representa la "inercia" o "impulso" de un partido en el momento actual.

**Características:**
- Es el único parámetro **SUBJETIVO**
- El usuario lo ajusta mediante sliders en la aplicación
- Valores por defecto: 1.0 (neutro)

**Interpretación:**
- **Λ < 1.0**: Partido en declive (desgaste de gobierno, escándalos)
- **Λ = 1.0**: Sin cambio de tendencia
- **Λ > 1.0**: Partido en ascenso (viralidad, liderazgo fuerte)

**Ejemplos de ajuste:**
| Situación | Partido | Λ sugerido |
|-----------|---------|------------|
| Desgaste por 6 años de gobierno | PSOE | 0.90 |
| Beneficiario de alternancia | PP | 1.10 |
| Escándalo mediático | VOX | 0.85 |
| Viralidad en redes | SALF | 1.20 |

---

## 3. Fórmula Final

$$E_p = S_p \times K_p \times \Phi_p \times \Lambda_p$$

Donde:
- $S_p$ = Voto Directo del partido p
- $K_p$ = Factor de corrección por recuerdo
- $\Phi_p$ = Fidelidad (por defecto = 1.0)
- $\Lambda_p$ = Momentum (ajustable por usuario)

**Restricción:** La estimación nunca puede ser menor que el Voto Directo:
$$E_{final,p} = max(S_p, E_p)$$

---

## 4. Ejemplo Numérico Completo

**Estudio:** 3524 (Enero 2025)

### Paso 1: Datos de entrada
| Partido | VD (Sp) | Recuerdo | Resultado 2023 |
|---------|---------|----------|----------------|
| PP | 16.4% | 24.9% | 33.1% |
| PSOE | 23.7% | 38.4% | 31.7% |

### Paso 2: Calcular K
- PP: $K = 33.1 / 24.9 = 1.33$
- PSOE: $K = 31.7 / 38.4 = 0.83$

### Paso 3: Aplicar fórmula (Φ=1, Λ=1)
- PP: $E = 16.4 \times 1.33 \times 1.0 \times 1.0 = 21.8\%$
- PSOE: $E = 23.7 \times 0.83 \times 1.0 \times 1.0 = 19.7\%$

### Paso 4: Protección suelo
- PP: 21.8% > 16.4% (VD) → Se mantiene **21.8%**
- PSOE: 19.7% < 23.7% (VD) → Se aplica suelo **23.7%**

### Paso 5: Normalización
Los valores se ajustan para que sumen 100%.

---

## 5. Resumen de Parámetros

| Parámetro | Tipo | Fuente | Modifiable |
|-----------|------|--------|------------|
| Voto Directo (S) | Objetivo | Encuesta CIS | No |
| Recuerdo (R) | Objetivo | Encuesta CIS | No |
| Factor K | Calculado | R + Resultados 2023 | No |
| Fidelidad (Φ) | Estructural | Datos históricos | Futuro |
| Momentum (Λ) | **Subjetivo** | Juicio experto | **Sí (sliders)** |

---

## 6. Preguntas Frecuentes

**¿Por qué el PSOE aparece por encima del PP?**
Porque el Voto Directo del CIS está sistemáticamente inflado para el PSOE. La protección de suelo impide que baje de ese valor. Para corregirlo, el usuario puede reducir el Momentum del PSOE (ej: Λ=0.85).

**¿Por qué existe la protección de suelo?**
Es un criterio metodológico: el modelo puede "sumar" pero nunca "restar" respecto a lo declarado por los encuestados.

**¿El Factor K está amortiguado?**
Actualmente se aplica al 100% (sin amortiguación). Esto maximiza la corrección por voto oculto.
