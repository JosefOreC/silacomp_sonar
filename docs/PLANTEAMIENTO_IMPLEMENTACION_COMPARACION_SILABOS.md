# PLANTEAMIENTO DE IMPLEMENTACIÓN

## Sistema inteligente para comparación de sílabos universitarios

**Versión:** 1.0  
**Tipo de documento:** Especificación de implementación  
**Objetivo:** Definir la arquitectura, metodología, flujo funcional, algoritmo inicial, generación de informes y evolución mediante validación humana.

---

# 1. Descripción general

El proyecto consiste en desarrollar una aplicación web capaz de comparar dos sílabos universitarios y determinar el grado de correspondencia académica entre ellos.

El sistema recibirá como entrada dos documentos PDF:

- **Sí­labo objetivo:** documento que representa el curso que se desea utilizar como referencia para la comparación.
- **Sí­labo comparado:** documento que será evaluado frente al sílabo objetivo.

La primera versión del sistema debe realizar una comparación explicable y producir:

1. Un porcentaje de correspondencia estimada.
2. Las secciones y contenidos donde se encontraron correspondencias.
3. La evidencia utilizada para identificar cada correspondencia.
4. Los contenidos que no encontraron correspondencia.
5. Un informe formal de comparación.
6. Una interfaz para que una persona pueda revisar y corregir las correspondencias propuestas por el sistema.

El sistema no debe afirmar que un curso ha sido oficialmente convalidado. La aplicación realiza una **pre-evaluación computacional de correspondencia académica**. La decisión académica final corresponde a la institución y a los responsables académicos competentes.

---

# 2. Objetivo general

Implementar un sistema web inteligente que permita comparar dos sílabos universitarios, identificar correspondencias entre sus contenidos académicos mediante técnicas de procesamiento de lenguaje natural y generar un informe formal, trazable y explicable que facilite la evaluación humana.

---

# 3. Objetivos específicos

1. Permitir la carga de dos sílabos en formato PDF.
2. Identificar y extraer el contenido textual de los documentos.
3. Detectar la estructura académica de cada sílabo.
4. Identificar unidades, temas, contenidos y otros elementos relevantes.
5. Normalizar el texto para facilitar la comparación.
6. Calcular similitud léxica entre contenidos.
7. Calcular similitud semántica entre contenidos.
8. Considerar información estructural del sílabo.
9. Identificar correspondencias entre contenidos del sílabo objetivo y del sílabo comparado.
10. Evitar depender exclusivamente de una comparación de texto completo.
11. Generar un porcentaje global de correspondencia.
12. Mostrar exactamente dónde se encontraron las correspondencias.
13. Mostrar evidencia textual y cuantitativa de cada correspondencia.
14. Identificar contenidos sin correspondencia.
15. Generar un informe formal descargable.
16. Permitir que una persona valide o corrija las correspondencias.
17. Registrar las decisiones humanas sin sobrescribir la predicción original del sistema.
18. Utilizar las validaciones humanas como dataset para posteriores modelos supervisados.
19. Evaluar objetivamente la evolución del modelo.
20. Mantener trazabilidad de documentos, resultados, decisiones humanas y versiones de modelos.

---

# 4. Conceptos principales

## 4.1. Sílabo objetivo

Es el sílabo utilizado como referencia principal de la comparación.

Ejemplo:

```text
Sílabo objetivo
Universidad: Universidad A
Curso: Base de Datos I
Código: INF-201
```

El sistema analizará sus unidades y contenidos y buscará correspondencias en el sílabo comparado.

---

## 4.2. Sílabo comparado

Es el sílabo que será contrastado contra el sílabo objetivo.

```text
Sílabo comparado
Universidad: Universidad B
Curso: Sistemas de Bases de Datos
Código: SIS-305
```

La comparación debe ser bidireccional en cuanto a cobertura:

```text
Objetivo → ¿dónde aparece en Comparado?
Comparado → ¿qué contenidos no están cubiertos por Objetivo?
```

Esto permite evitar una interpretación incorrecta basada únicamente en una dirección.

---

## 4.3. Correspondencia académica

Una correspondencia representa una relación entre dos contenidos que presentan un grado suficiente de similitud léxica, semántica y/o conceptual.

Ejemplo:

```text
Objetivo:
"Normalización de bases de datos y formas normales"

Comparado:
"Modelo relacional, normalización y formas normales"

Resultado:
Correspondencia alta
```

La correspondencia no debe depender únicamente de que las palabras sean iguales.

---

# 5. Alcance de la Fase 1

La Fase 1 constituye el primer producto funcional del sistema.

## Entrada

Exactamente dos documentos:

```text
PDF 1 → Sílabo objetivo
PDF 2 → Sílabo comparado
```

## Procesamiento

```text
Carga de PDFs
        ↓
Extracción de texto
        ↓
Detección de estructura
        ↓
Segmentación de contenidos
        ↓
Normalización
        ↓
Representación textual
        ↓
Similitud léxica
        ↓
Similitud semántica
        ↓
Análisis estructural
        ↓
Detección de correspondencias
        ↓
Cálculo de correspondencia global
        ↓
Generación de evidencia
        ↓
Generación de informe
        ↓
Revisión humana
```

## Salida

La Fase 1 debe entregar:

```text
1. Porcentaje global de correspondencia
2. Tabla de correspondencias
3. Evidencias
4. Contenidos no correspondidos
5. Resumen de resultados
6. Informe formal
7. Resultado disponible para revisión humana
```

---

# 6. Definición funcional de la Fase 1

La Fase 1 debe denominarse:

> **Comparación explicable de dos sílabos y generación de informe**

No debe reducirse a:

> PDF → porcentaje

La salida debe responder:

- ¿Cuánto coinciden?
- ¿Dónde coinciden?
- ¿Qué contenidos coinciden?
- ¿Con qué otro contenido coinciden?
- ¿Qué evidencia respalda la coincidencia?
- ¿Qué contenidos no encontraron correspondencia?
- ¿Qué tan fuerte es cada correspondencia?
- ¿Qué método/modelo produjo el resultado?

---

# 7. Flujo principal

## Paso 1. Cargar sílabo objetivo

El usuario selecciona un archivo PDF.

El sistema registra:

```text
id
nombre del archivo
tamaño
fecha de carga
cantidad de páginas
tipo de extracción
```

---

## Paso 2. Cargar sílabo comparado

El usuario selecciona el segundo PDF.

El sistema registra la misma información.

---

## Paso 3. Validar documentos

El sistema verifica:

- que ambos archivos sean PDF;
- que no estén vacíos;
- que tengan contenido extraíble;
- que no superen el límite configurado;
- que tengan una cantidad mínima razonable de texto.

En Fase 1 se priorizan PDFs digitales con texto seleccionable.

Los PDFs completamente escaneados serán tratados en la Fase 2 mediante OCR.

---

# 8. Extracción de texto

Tecnología inicial:

```text
Python
PyMuPDF
```

Cada página debe conservar su referencia.

Ejemplo:

```json
{
  "page": 4,
  "text": "... contenido ..."
}
```

La ubicación es importante porque el informe debe poder indicar dónde se encontró la evidencia.

---

# 9. Estructuración del sílabo

El texto extraído no debe compararse directamente como un único bloque.

El sistema debe intentar identificar:

```text
Datos generales
        ↓
Descripción / sumilla
        ↓
Competencias
        ↓
Resultados de aprendizaje
        ↓
Unidad I
    ├── contenido 1
    ├── contenido 2
    └── contenido 3
        ↓
Unidad II
    ├── contenido 1
    └── contenido 2
        ↓
Unidad III
        ↓
Metodología
        ↓
Evaluación
        ↓
Bibliografía
```

La estructura exacta puede variar entre universidades.

Por esta razón, la segmentación debe tolerar variaciones de formato.

---

# 10. Modelo de datos del contenido

Cada contenido identificado debe mantener información suficiente para su trazabilidad.

Ejemplo conceptual:

```json
{
  "id": "OBJ-CONT-001",
  "syllabus_id": "OBJ-001",
  "section": "Unidad I",
  "title": "Bases de datos relacionales",
  "text": "Modelo relacional, tablas, atributos y relaciones.",
  "page_start": 5,
  "page_end": 5,
  "order": 1
}
```

Para el sílabo comparado:

```json
{
  "id": "CMP-CONT-014",
  "syllabus_id": "CMP-001",
  "section": "Unidad II",
  "title": "Modelo relacional",
  "text": "Conceptos de tablas, atributos, claves y relaciones.",
  "page_start": 7,
  "page_end": 7,
  "order": 3
}
```

---

# 11. Normalización del texto

Antes de calcular similitud se realizará una etapa de normalización.

Puede incluir:

- conversión a minúsculas;
- eliminación de espacios redundantes;
- normalización de caracteres;
- eliminación controlada de palabras vacías;
- normalización de puntuación;
- lematización cuando sea conveniente;
- conservación de términos técnicos importantes.

No se debe eliminar información técnica de forma agresiva.

Ejemplo:

```text
"Base de Datos Relacionales"
```

y

```text
"bases de datos relacionales"
```

deben poder reconocerse como conceptualmente cercanos.

---

# 12. Estrategia de comparación

No se utilizará únicamente una similitud de texto completo.

Se propone un enfoque híbrido.

## Componentes

```text
Similitud léxica
        +
Similitud semántica
        +
Coincidencia de palabras/frases relevantes
        +
Similitud estructural
        ↓
Score de correspondencia
```

---

# 13. Similitud léxica

Tecnología inicial:

```text
TF-IDF
Cosine Similarity
```

Permite detectar coincidencias directas de términos.

Ejemplo:

```text
Objetivo:
"Base de datos relacional"

Comparado:
"Bases de datos relacionales"
```

La similitud léxica debería ser elevada.

Sin embargo:

```text
Objetivo:
"Formas normales"

Comparado:
"Normalización de bases de datos"
```

podría presentar una similitud léxica menor aunque exista una relación conceptual.

Por eso no puede ser el único método.

---

# 14. Similitud semántica

Tecnología inicial:

```text
Sentence Transformers
Embeddings
Cosine Similarity
```

Cada contenido se transforma en un vector.

Ejemplo conceptual:

```text
Contenido A → embedding A
Contenido B → embedding B
                   ↓
          cosine similarity
                   ↓
             0.91
```

Esto permite detectar relaciones semánticas aunque las palabras utilizadas no sean idénticas.

---

# 15. Evidencia léxica

El sistema debe identificar términos o frases relevantes compartidos.

Ejemplo:

```text
Contenido objetivo:
"Modelo relacional, claves primarias y foráneas."

Contenido comparado:
"Modelo relacional y manejo de claves primarias y foráneas."
```

Evidencia:

```text
Modelo relacional
Claves primarias
Claves foráneas
```

Esta evidencia debe mostrarse en el informe.

---

# 16. Evidencia semántica

Cuando los contenidos no utilizan exactamente las mismas palabras, el sistema debe indicar que la correspondencia fue principalmente semántica.

Ejemplo:

```text
Objetivo:
"Formas normales y normalización"

Comparado:
"Normalización del modelo relacional"
```

El informe puede indicar:

```text
Tipo de evidencia:
Semántica

Similitud semántica:
0.89
```

No debe inventarse una explicación académica que no provenga de las características calculadas.

---

# 17. Evidencia estructural

También puede considerarse:

- misma unidad;
- posición aproximada dentro de la unidad;
- relación entre unidades;
- sección académica;
- cercanía entre contenidos.

La estructura no debe dominar el resultado.

Por ejemplo, que dos contenidos estén en la Unidad I no significa automáticamente que sean equivalentes.

---

# 18. Cálculo inicial del score

El score inicial puede construirse mediante una combinación configurable.

Ejemplo experimental:

```text
score =
    0.40 * semantic_similarity
  + 0.30 * lexical_similarity
  + 0.15 * keyword_overlap
  + 0.15 * structural_similarity
```

Estos pesos son parámetros experimentales.

NO representan una regla oficial de convalidación.

Deben mantenerse configurables para poder modificarlos y evaluarlos experimentalmente.

---

# 19. Correspondencia entre contenidos

Para cada contenido del sílabo objetivo se deben buscar candidatos dentro del sílabo comparado.

Ejemplo:

```text
OBJ-CONT-001
        ↓
CMP-CONT-003  score 0.93
CMP-CONT-008  score 0.78
CMP-CONT-011  score 0.41
```

El sistema debe conservar los candidatos relevantes.

No debe forzar una relación uno-a-uno.

---

# 20. Relaciones múltiples

El sistema debe permitir:

```text
A1 ↔ B1
A2 ↔ B1
A1 ↔ B1 + B2
A1 + A2 ↔ B1
```

Esto es importante porque un contenido académico puede dividirse o agruparse de manera diferente entre universidades.

---

# 21. Umbrales iniciales

Los umbrales deben ser configurables.

Ejemplo:

```text
>= 0.85 → MATCH
0.70 - 0.849 → PARTIAL_MATCH
0.50 - 0.699 → UNCERTAIN
< 0.50 → NO_MATCH
```

Los valores anteriores son iniciales y experimentales.

No deben presentarse como valores académicos oficiales.

La validación experimental deberá determinar posteriormente si esos umbrales son adecuados.

---

# 22. Etiquetas

Se utilizarán inicialmente:

```text
MATCH
PARTIAL_MATCH
NO_MATCH
UNCERTAIN
```

## MATCH

Existe evidencia suficiente para considerar que los contenidos corresponden.

## PARTIAL_MATCH

Existe relación, pero solamente una parte del contenido presenta correspondencia.

## NO_MATCH

No se encontró evidencia suficiente de correspondencia.

## UNCERTAIN

El sistema no tiene suficiente evidencia para clasificar automáticamente.

Los casos `UNCERTAIN` son especialmente importantes para revisión humana.

---

# 23. Correspondencia global

El porcentaje global no debe calcularse como una simple similitud entre los dos PDF completos.

Debe construirse a partir de las correspondencias académicas detectadas.

Una primera formulación experimental puede ser:

```text
Correspondencia global =
Σ(peso del contenido objetivo × score de cobertura)
/
Σ(peso de los contenidos objetivo)
```

La definición exacta debe quedar documentada y mantenerse estable durante cada experimento.

Debe evitarse que un contenido extremadamente largo domine todo el resultado únicamente por su cantidad de texto.

---

# 24. Bidireccionalidad

Además de:

```text
Objetivo → Comparado
```

se debe calcular:

```text
Comparado → Objetivo
```

Esto permite identificar:

```text
Contenidos del objetivo cubiertos
Contenidos del objetivo no cubiertos

Contenidos del comparado cubiertos
Contenidos del comparado no cubiertos
```

La aplicación podrá presentar ambos indicadores en el informe.

---

# 25. Resultado de la Fase 1

La pantalla de resultados debe mostrar:

```text
SÍLABO OBJETIVO
        VS
SÍLABO COMPARADO

Correspondencia estimada: 82.4 %
```

Luego:

```text
Resumen
├── Contenidos analizados
├── Correspondencias altas
├── Correspondencias parciales
├── Casos inciertos
└── Contenidos sin correspondencia
```

---

# 26. Tabla principal de correspondencias

Ejemplo:

| Sílabo objetivo             | Sílabo comparado        | Score | Tipo     | Evidencia                             |
| --------------------------- | ----------------------- | ----: | -------- | ------------------------------------- |
| Bases de datos relacionales | Modelo relacional       |  0.93 | MATCH    | Modelo relacional, tablas, relaciones |
| Normalización               | Normalización de datos  |  0.89 | MATCH    | Normalización                         |
| Álgebra relacional          | Operadores relacionales |  0.74 | PARTIAL  | Operadores, relaciones                |
| Transacciones               | Seguridad de BD         |  0.41 | NO_MATCH | Evidencia insuficiente                |

La tabla debe permitir abrir el detalle de cada relación.

---

# 27. Detalle de una correspondencia

Al seleccionar una correspondencia:

```text
CONTENIDO OBJETIVO

Unidad I
Bases de datos relacionales

Página: 5

"Modelo relacional, tablas, atributos,
claves y relaciones."
```

Contra:

```text
CONTENIDO COMPARADO

Unidad II
Modelo relacional

Página: 7

"Modelo relacional, tablas, atributos,
claves primarias, claves foráneas y relaciones."
```

Resultado:

```text
Score global: 0.93

Similitud semántica: 0.95
Similitud léxica: 0.91
Coincidencia de términos: 0.94
Similitud estructural: 0.86
```

Evidencia:

```text
Modelo relacional
Tablas
Atributos
Relaciones
```

---

# 28. Informe formal

La Fase 1 debe generar un documento de salida formal.

Nombre conceptual:

```text
Informe de comparación de sílabos
```

El informe debe ser un producto principal del sistema, no un elemento secundario.

---

# 29. Estructura del informe

## Portada

Debe contener:

```text
INFORME DE COMPARACIÓN DE SÍLABOS

Sílabo objetivo:
[Curso]

Universidad:
[Universidad]

Sílabo comparado:
[Curso]

Universidad:
[Universidad]

Fecha:
[Fecha]

Sistema:
[Nombre del sistema]
```

---

# 30. Resumen ejecutivo

Debe explicar formalmente:

- documentos analizados;
- metodología utilizada;
- porcentaje de correspondencia;
- cantidad de contenidos evaluados;
- principales correspondencias;
- principales diferencias;
- alcance del resultado.

Ejemplo conceptual:

> Se realizó una comparación computacional entre el sílabo objetivo y el sílabo comparado mediante técnicas de análisis léxico, representación semántica y análisis estructural de los contenidos identificados. El resultado obtenido corresponde a una estimación de correspondencia académica basada en los criterios computacionales configurados para esta versión del sistema.

---

# 31. Datos de los documentos

Tabla:

| Campo                 | Sílabo objetivo | Sílabo comparado           |
| --------------------- | --------------- | -------------------------- |
| Universidad           | Universidad A   | Universidad B              |
| Curso                 | Base de Datos I | Sistemas de Bases de Datos |
| Código                | INF-201         | SIS-305                    |
| Páginas               | 12              | 15                         |
| Contenidos detectados | 24              | 27                         |
| Fecha de análisis     | Fecha           | Fecha                      |

---

# 32. Resultado general

Debe mostrar:

```text
CORRESPONDENCIA ESTIMADA

82.4 %
```

Además:

```text
Cobertura del objetivo: 86 %
Cobertura del comparado: 79 %
```

Los indicadores deben explicarse para evitar interpretaciones incorrectas.

---

# 33. Resumen de correspondencias

Ejemplo:

| Clasificación | Cantidad |
| ------------- | -------: |
| Match         |       15 |
| Partial Match |        5 |
| Uncertain     |        2 |
| No Match      |        2 |

---

# 34. Correspondencias detalladas

El informe debe contener una sección por correspondencia.

Ejemplo:

```text
3.1 Correspondencia 01

Contenido objetivo:
Unidad I – Bases de datos relacionales

Página:
5

Contenido comparado:
Unidad II – Modelo relacional

Página:
7

Score:
0.93

Clasificación:
MATCH

Evidencia:
- Modelo relacional
- Tablas
- Atributos
- Relaciones

Indicadores:
Similitud semántica: 0.95
Similitud léxica: 0.91
Coincidencia de términos: 0.94
Similitud estructural: 0.86
```

---

# 35. Contenidos sin correspondencia

Debe existir una sección específica:

```text
CONTENIDOS DEL SÍLABO OBJETIVO
SIN CORRESPONDENCIA SUFICIENTE
```

Ejemplo:

| Unidad | Contenido                 | Página | Mejor candidato | Score |
| ------ | ------------------------- | -----: | --------------- | ----: |
| III    | Optimización de consultas |      9 | Consultas SQL   |  0.46 |

También debe existir la sección inversa:

```text
CONTENIDOS DEL SÍLABO COMPARADO
SIN CORRESPONDENCIA SUFICIENTE
```

Esto hace que el informe sea más útil para una evaluación académica.

---

# 36. Metodología del informe

El informe debe documentar cómo se obtuvo el resultado.

Debe incluir:

```text
Extracción:
PyMuPDF

Procesamiento:
Normalización textual

Representación:
TF-IDF + embeddings

Comparación:
Similitud léxica + semántica + estructural

Modelo:
[versión]

Umbrales:
[configuración]

Fecha de procesamiento:
[fecha]
```

Esto es importante para reproducibilidad científica.

---

# 37. Trazabilidad

Cada evidencia debe poder rastrearse hasta:

```text
Documento
    ↓
Página
    ↓
Sección
    ↓
Unidad
    ↓
Contenido
    ↓
Correspondencia
    ↓
Score
```

La aplicación debe conservar los identificadores internos.

---

# 38. Generación del documento

La primera versión debe priorizar:

```text
Informe HTML imprimible
```

y posteriormente:

```text
Informe PDF formal
```

Si la implementación inicial permite generar PDF directamente sin comprometer la estabilidad del núcleo, puede incorporarse desde la Fase 1.

Tecnología propuesta para PDF:

```text
Python
ReportLab
```

La generación del informe debe estar separada de la lógica de comparación.

---

# 39. Revisión humana

Después de producir el resultado, el sistema debe permitir la validación humana.

Ejemplo:

```text
IA propone:

"Normalización"
        ↔
"Formas normales"

Score: 0.89

[ MATCH ]
[ PARTIAL ]
[ NO MATCH ]
[ UNCERTAIN ]
```

También debe permitir agregar una correspondencia que la IA no detectó.

---

# 40. Regla fundamental de la revisión humana

La decisión humana NO debe sobrescribir la predicción original.

Se deben almacenar ambas:

```text
Predicción IA:
MATCH

Decisión humana:
PARTIAL_MATCH
```

Esto permite estudiar posteriormente el error del modelo.

---

# 41. Registro de correcciones

Ejemplo:

```json
{
  "prediction_before": "MATCH",
  "human_decision": "PARTIAL_MATCH",
  "correction_type": "FALSE_POSITIVE_OR_OVER_ESTIMATION",
  "justification": "Solo existe coincidencia en una parte del contenido.",
  "model_version": "baseline-001",
  "timestamp": "2026-09-24T..."
}
```

---

# 42. Dataset de aprendizaje

Cada revisión humana puede convertirse posteriormente en una observación de entrenamiento.

Ejemplo:

```text
Contenido A
Contenido B
Features
Predicción IA
Decisión humana
Tipo de error
Justificación
Versión del modelo
```

La información debe conservarse de manera estructurada.

---

# 43. Evolución del sistema

La evolución propuesta es:

```text
FASE 1
Comparación explicable
        ↓
Revisión humana
        ↓
Dataset inicial
        ↓
FASE 2
Modelo supervisado
        ↓
Evaluación
        ↓
Nuevas revisiones
        ↓
Dataset ampliado
        ↓
Modelo mejorado
```

---

# 44. Fase 2: OCR

La Fase 2 debe ampliar la entrada a documentos escaneados.

Flujo:

```text
PDF escaneado
      ↓
Detección de ausencia de texto
      ↓
OCR
      ↓
Texto por página
      ↓
Misma pipeline de Fase 1
```

Tecnología propuesta:

```text
Tesseract OCR
```

El OCR debe conservar la página de origen.

---

# 45. Fase 2: aprendizaje supervisado

La segunda línea de evolución consiste en utilizar las decisiones humanas acumuladas.

Proceso:

```text
Revisiones humanas
       ↓
Dataset etiquetado
       ↓
Extracción de características
       ↓
Entrenamiento
       ↓
Modelo candidato
       ↓
Evaluación
       ↓
Comparación contra baseline
       ↓
Aprobación
       ↓
Nueva versión de producción
```

No debe existir entrenamiento automático e incontrolado después de cada revisión.

---

# 46. Modelo supervisado inicial

Modelo candidato inicial:

```text
Logistic Regression
```

Motivo:

- interpretable;
- rápido;
- adecuado para un primer modelo;
- fácil de evaluar;
- permite observar influencia de características;
- apropiado para un dataset inicialmente pequeño.

Posteriormente se pueden evaluar:

```text
Random Forest
Gradient Boosting
XGBoost
otros modelos
```

La selección debe realizarse mediante evidencia experimental y no por moda tecnológica.

---

# 47. Características del modelo

Posibles features:

```text
semantic_similarity
lexical_similarity
keyword_overlap
length_similarity
section_similarity
unit_similarity
position_similarity
embedding_distance
```

El conjunto definitivo debe documentarse junto con la versión del modelo.

---

# 48. Baseline

Antes del modelo supervisado debe existir un baseline.

Ejemplo:

```text
Baseline:
Sentence Transformer
+
Cosine Similarity
```

Después:

```text
Modelo supervisado
```

La investigación debe determinar si el modelo supervisado mejora realmente al baseline.

---

# 49. Evaluación

Las métricas principales pueden incluir:

```text
Accuracy
Precision
Recall
F1-score
```

Para ranking:

```text
Precision@K
Recall@K
```

Si se utiliza un score continuo:

```text
MAE
RMSE
Pearson
Spearman
```

No todas deben utilizarse simultáneamente. Se seleccionarán según el tipo de salida y el diseño experimental.

---

# 50. Dataset científico

El dataset debe ser construido con casos reales o representativos.

Cada observación debe tener:

```text
contenido_objetivo
contenido_comparado
features
prediccion_modelo
etiqueta_humana
```

Para aumentar la calidad del ground truth, una muestra puede ser evaluada por dos expertos.

En ese caso se puede estudiar el acuerdo interevaluador.

Para dos evaluadores y etiquetas categóricas puede utilizarse, cuando corresponda:

```text
Cohen's Kappa
```

---

# 51. Prevención de data leakage

No se debe dividir aleatoriamente el dataset sin considerar la procedencia.

Si contenidos del mismo curso o versiones casi idénticas de un sílabo aparecen en entrenamiento y prueba, las métricas pueden quedar artificialmente infladas.

Por ello, cuando exista suficiente información, se recomienda dividir considerando:

```text
Universidad
Curso
Sílabo
Grupo de documentos
```

La estrategia concreta debe definirse según el dataset disponible.

---

# 52. Active Learning

En una etapa posterior se puede priorizar la revisión humana de casos donde el sistema presenta mayor incertidumbre.

Ejemplo:

```text
Score 0.50
Score 0.51
Score 0.52
```

Estos casos pueden ser más útiles para el aprendizaje que revisar únicamente:

```text
Score 0.99
Score 0.98
```

El objetivo es utilizar eficientemente el esfuerzo humano.

---

# 53. Versionado

Cada modelo debe tener una versión.

Ejemplo:

```text
baseline-001
supervised-001
supervised-002
```

Cada resultado debe conservar:

```text
model_version
algorithm
parameters
thresholds
date
```

Esto permite reproducir un resultado.

---

# 54. Arquitectura general

Se utilizará un monolito modular.

No se recomienda implementar microservicios para la primera versión.

Arquitectura:

```text
React + TypeScript
        │
        │ REST
        ▼
FastAPI
        │
        ├── Domain
        ├── Application
        └── Infrastructure
                ├── PDF
                ├── NLP
                ├── Embeddings
                ├── ML
                └── Persistence
```

---

# 55. Stack tecnológico

## Frontend

```text
React
TypeScript
Vite
```

## Backend

```text
Python
FastAPI
```

## Procesamiento PDF

```text
PyMuPDF
```

## OCR

```text
Tesseract OCR
```

## NLP

```text
scikit-learn
Sentence Transformers
```

## Persistencia inicial

```text
SQLite
```

Posteriormente:

```text
PostgreSQL
```

## Testing

```text
pytest
```

## Control de versiones

```text
Git
```

---

# 56. Arquitectura interna

Estructura propuesta:

```text
backend/
└── app/
    ├── domain/
    │   ├── syllabus.py
    │   ├── content.py
    │   ├── comparison.py
    │   ├── review.py
    │   └── model_version.py
    │
    ├── application/
    │   ├── process_syllabus.py
    │   ├── compare_syllabi.py
    │   ├── review_comparison.py
    │   ├── create_dataset.py
    │   ├── train_model.py
    │   └── evaluate_model.py
    │
    ├── infrastructure/
    │   ├── pdf/
    │   ├── ocr/
    │   ├── embeddings/
    │   ├── ml/
    │   └── persistence/
    │
    └── api/
        ├── syllabus.py
        ├── comparison.py
        ├── review.py
        ├── dataset.py
        └── model.py
```

---

# 57. Regla arquitectónica

El dominio no debe depender directamente de:

```text
FastAPI
Django
ORM
PyMuPDF
Tesseract
Sentence Transformers
scikit-learn
```

La lógica de negocio debe depender de abstracciones.

Ejemplo conceptual:

```text
Domain
   ↑
Application
   ↑
Ports
   ↑
Infrastructure
```

---

# 58. Frontend

Estructura:

```text
frontend/
└── src/
    ├── pages/
    │   ├── Dashboard
    │   ├── NewComparison
    │   ├── ComparisonResult
    │   ├── HumanReview
    │   ├── History
    │   └── ModelMetrics
    │
    ├── components/
    │   ├── SyllabusUploader
    │   ├── ComparisonScore
    │   ├── MatchTable
    │   ├── ReviewPanel
    │   ├── EvidencePanel
    │   └── ModelStatus
    │
    ├── services/
    │   ├── comparisonApi
    │   ├── reviewApi
    │   └── modelApi
    │
    └── types/
```

---

# 59. Interfaz de usuario

El diseño debe ser:

- oscuro;
- formal;
- académico;
- legible;
- consistente;
- orientado a datos.

Paleta base:

```text
Background: #0B0F14
Surface:    #121820
Elevated:   #1A222D
Text:       #F1F5F9
Secondary:  #94A3B8
Border:     #263241
```

Debe evitarse:

```text
texto oscuro sobre fondo oscuro
texto claro sobre controles claros
bajo contraste
exceso de colores
```

---

# 60. Pantallas principales

## Dashboard

Resumen de:

```text
Comparaciones realizadas
Últimos análisis
Modelos disponibles
Revisiones pendientes
```

## Nueva comparación

```text
Sílabo objetivo
[Seleccionar PDF]

Sílabo comparado
[Seleccionar PDF]

[Analizar]
```

## Resultado

```text
82.4 %

Resumen
Correspondencias
No correspondencias
Evidencias

[Generar informe]
[Revisar]
```

## Revisión humana

Interfaz para validar cada correspondencia.

## Historial

Comparaciones anteriores y sus versiones.

---

# 61. API inicial

## Subir sílabo

```http
POST /api/syllabi/upload
```

## Crear comparación

```http
POST /api/comparisons
```

Body conceptual:

```json
{
  "objective_syllabus_id": "...",
  "compared_syllabus_id": "..."
}
```

## Obtener comparación

```http
GET /api/comparisons/{id}
```

## Obtener correspondencias

```http
GET /api/comparisons/{id}/matches
```

## Registrar revisión

```http
POST /api/reviews
```

## Actualizar revisión

```http
PUT /api/reviews/{id}
```

## Estadísticas del dataset

```http
GET /api/dataset/statistics
```

## Entrenar modelo

```http
POST /api/models/train
```

## Modelos

```http
GET /api/models
```

## Métricas

```http
GET /api/models/{id}/metrics
```

---

# 62. Persistencia inicial

Entidades principales:

```text
Syllabus
SyllabusPage
SyllabusSection
ContentItem
Comparison
ContentMatch
Review
DatasetExample
ModelVersion
Report
```

---

# 63. Relación conceptual

```text
Syllabus
   │
   ├── Pages
   │
   └── Sections
          │
          └── ContentItems
                    │
                    ▼
              Comparison
                    │
                    └── ContentMatches
                              │
                              ▼
                           Review
                              │
                              ▼
                       DatasetExample
                              │
                              ▼
                         ModelVersion
```

---

# 64. Reporte como entidad

El informe generado debe conservar:

```text
report_id
comparison_id
report_version
generated_at
model_version
file_path
```

No debe ser necesario recalcular una comparación solamente para volver a descargar un informe ya generado.

---

# 65. Separación de responsabilidades

El sistema debe separar:

```text
Extracción
    ↓
Estructuración
    ↓
Comparación
    ↓
Interpretación
    ↓
Informe
    ↓
Revisión
```

No se debe implementar todo dentro de una única función.

---

# 66. Uso de IA generativa

La IA generativa puede utilizarse para:

- acelerar desarrollo;
- asistir en documentación;
- ayudar en análisis exploratorio;
- proponer código;
- ayudar en refactorización.

No debe utilizarse como único motor para determinar la correspondencia.

La comparación principal debe ser:

```text
reproducible
medible
versionable
auditable
```

---

# 67. Uso de Gemini durante el desarrollo

Gemini puede utilizarse como asistente de programación mediante una metodología controlada.

Flujo:

```text
Especificación
      ↓
Prompt técnico
      ↓
Gemini
      ↓
Implementación
      ↓
Revisión humana
      ↓
Tests
      ↓
Correcciones
      ↓
Commit
```

Gemini no debe modificar la arquitectura sin autorización.

---

# 68. Reglas para Gemini

Los prompts deben indicar:

```text
NO cambiar la arquitectura sin autorización.
NO inventar criterios académicos.
NO utilizar un LLM como juez final de convalidación.
NO eliminar datos originales.
NO sobrescribir predicciones humanas.
NO entrenar modelos automáticamente sin control.
NO mezclar entrenamiento y prueba.
NO introducir dependencias innecesarias.
NO implementar microservicios.
```

---

# 69. Prompt estándar para implementación

Cada tarea puede utilizar:

```text
CONTEXTO

OBJETIVO

ARCHIVOS AFECTADOS

RESTRICCIONES

CONTRATOS

CRITERIOS DE ACEPTACIÓN

PRUEBAS

RESULTADO ESPERADO
```

Antes de realizar cambios complejos, la IA debe indicar:

1. archivos que modificará;
2. arquitectura afectada;
3. dependencias nuevas;
4. riesgos;
5. estrategia de pruebas.

---

# 70. Orden de implementación

## Etapa 1

Crear repositorio.

```text
frontend/
backend/
docs/
tests/
```

## Etapa 2

Implementar entidades de dominio.

## Etapa 3

Implementar carga de PDF.

## Etapa 4

Implementar extracción con PyMuPDF.

## Etapa 5

Implementar normalización.

## Etapa 6

Implementar segmentación.

## Etapa 7

Implementar embeddings.

## Etapa 8

Implementar similitud léxica.

## Etapa 9

Implementar similitud semántica.

## Etapa 10

Implementar combinación de features.

## Etapa 11

Implementar ranking de correspondencias.

## Etapa 12

Implementar cálculo global.

## Etapa 13

Implementar API.

## Etapa 14

Implementar interfaz de carga.

## Etapa 15

Implementar pantalla de resultados.

## Etapa 16

Implementar evidencia.

## Etapa 17

Implementar generación de informe.

## Etapa 18

Implementar revisión humana.

## Etapa 19

Persistir revisiones.

## Etapa 20

Crear dataset.

---

# 71. Primera versión funcional

La primera versión funcional debe conseguir:

```text
PDF objetivo
        +
PDF comparado
        ↓
Extracción
        ↓
Segmentación
        ↓
Comparación
        ↓
Porcentaje
        ↓
Correspondencias
        ↓
Evidencia
        ↓
Informe
        ↓
Revisión humana
```

Esto constituye el núcleo del producto.

---

# 72. Qué NO debe implementarse inicialmente

No incluir inicialmente:

```text
Microservicios
Chatbot complejo
Agentes autónomos
Entrenamiento online
Base de datos distribuida
Infraestructura cloud compleja
Fine-tuning de modelos grandes
OCR avanzado antes del flujo digital
Sistema institucional de convalidación
Decisiones académicas automáticas
```

Estas funcionalidades pueden evaluarse posteriormente.

---

# 73. Prioridades

## P0 — Núcleo obligatorio

```text
Carga PDF
Extracción
Estructuración
Comparación
Score
Correspondencias
Evidencias
Informe
Revisión humana
```

## P1 — Investigación

```text
Dataset
Baseline
Modelo supervisado
Métricas
Versionado
Evaluación
```

## P2 — Ampliación

```text
OCR
Active Learning
Dashboard de métricas
```

## P3 — Producto ampliado

```text
Usuarios
Historial avanzado
PostgreSQL
Reportes avanzados
```

---

# 74. Criterios de aceptación de Fase 1

La Fase 1 se considera funcional cuando:

### Entrada

- se pueden cargar exactamente dos PDFs;
- uno puede definirse como objetivo;
- el otro como comparado.

### Procesamiento

- se extrae texto;
- se conserva la página;
- se detectan contenidos;
- se calculan similitudes;
- se generan correspondencias.

### Resultado

- se obtiene un porcentaje;
- se muestran correspondencias;
- se muestran evidencias;
- se muestran contenidos sin correspondencia;
- se puede abrir el detalle de una correspondencia.

### Informe

- se genera un documento formal;
- incluye información de ambos sílabos;
- incluye metodología;
- incluye resultado global;
- incluye correspondencias;
- incluye evidencias;
- incluye contenidos sin correspondencia;
- incluye versión del modelo/método;
- incluye advertencia de que se trata de una pre-evaluación computacional.

### Revisión

- el usuario puede modificar la clasificación;
- la predicción original permanece almacenada;
- la decisión humana queda registrada.

---

# 75. Reglas de calidad

## Regla 1

El porcentaje nunca debe ser el único resultado.

## Regla 2

Cada correspondencia importante debe tener evidencia.

## Regla 3

Cada evidencia debe poder rastrearse hasta una página del PDF.

## Regla 4

La predicción IA y la decisión humana deben mantenerse separadas.

## Regla 5

Los parámetros del algoritmo deben estar versionados.

## Regla 6

No deben inventarse criterios académicos.

## Regla 7

La salida debe indicar que se trata de una evaluación computacional.

## Regla 8

Los resultados deben ser reproducibles.

## Regla 9

La comparación debe tolerar que las universidades utilicen estructuras diferentes.

## Regla 10

El sistema debe permitir corregir errores humanos y del modelo sin eliminar el historial.

---

# 76. Consideración sobre criterios de convalidación

Si se incorporan reglas académicas institucionales, estas deben mantenerse separadas del modelo de similitud.

Arquitectura conceptual:

```text
Modelo de correspondencia
        ↓
"¿Estos contenidos presentan correspondencia?"
        ↓
Rule Engine
        ↓
"¿El resultado cumple los criterios configurados?"
```

No se debe mezclar:

```text
similaridad semántica
```

con:

```text
regla académica
```

Por ejemplo, un parámetro institucional como un porcentaje mínimo de correspondencia debe estar en una configuración/regla independiente.

Los criterios normativos deben verificarse contra la versión vigente de la normativa institucional antes de incorporarse como reglas definitivas.

---

# 77. Pre-evaluación

El sistema puede producir:

```text
Resultado de pre-evaluación:
Cumple criterio configurado
```

o:

```text
Resultado de pre-evaluación:
No cumple criterio configurado
```

No debe mostrar:

```text
"Curso oficialmente convalidado"
```

porque la aplicación no tiene autoridad académica para emitir esa decisión.

---

# 78. Explicabilidad

El sistema debe responder:

```text
¿Por qué encontró correspondencia?
```

La respuesta debe provenir de variables observables:

```text
Similitud semántica
Similitud léxica
Términos compartidos
Sección
Unidad
Ubicación
Score final
```

No debe depender obligatoriamente de una explicación generada por un LLM.

---

# 79. Ejemplo completo de salida

```text
SÍLABO OBJETIVO
Base de Datos I

SÍLABO COMPARADO
Sistemas de Bases de Datos

CORRESPONDENCIA ESTIMADA
82.4 %

----------------------------------------

CORRESPONDENCIA 01

Objetivo:
Unidad I – Bases de datos relacionales

Comparado:
Unidad II – Modelo relacional

Score:
0.93

Clasificación:
MATCH

Evidencia:
- Modelo relacional
- Tablas
- Atributos
- Relaciones

Similitud semántica:
0.95

Similitud léxica:
0.91

----------------------------------------

CORRESPONDENCIA 02

Objetivo:
Unidad II – Normalización

Comparado:
Unidad II – Formas normales

Score:
0.89

Clasificación:
MATCH

Evidencia:
- Normalización
- Formas normales

----------------------------------------

CONTENIDOS SIN CORRESPONDENCIA

Objetivo:
Unidad IV – Optimización avanzada

Mejor candidato:
Consultas SQL

Score:
0.42

Clasificación:
NO_MATCH
```

---

# 80. Estructura recomendada del informe PDF

```text
PORTADA
│
├── 1. Identificación de los documentos
│
├── 2. Objetivo del análisis
│
├── 3. Metodología
│
├── 4. Resultado general
│
├── 5. Resumen de correspondencias
│
├── 6. Correspondencias detalladas
│      ├── 6.1 Correspondencia 01
│      ├── 6.2 Correspondencia 02
│      └── ...
│
├── 7. Contenidos sin correspondencia
│
├── 8. Análisis bidireccional
│
├── 9. Evidencias
│
├── 10. Parámetros y versión del modelo
│
├── 11. Observaciones
│
└── 12. Nota sobre alcance y decisión académica
```

---

# 81. Nota formal del informe

El informe debe incorporar una nota similar a:

> El presente documento corresponde a un informe de análisis computacional de correspondencia entre los sílabos proporcionados. Los resultados se obtienen mediante técnicas de procesamiento de lenguaje natural, análisis léxico, análisis semántico y criterios estructurales configurados para el sistema. La información presentada constituye una pre-evaluación y elemento de apoyo para la revisión académica, por lo que no sustituye la evaluación, validación ni decisión de las autoridades o responsables académicos correspondientes.

---

# 82. Consideraciones científicas

El proyecto no debe limitarse a demostrar que una aplicación funciona.

Para convertirlo en un proyecto científico, se debe evaluar:

```text
¿La combinación de características mejora la identificación
de correspondencias frente a un baseline?
```

y posteriormente:

```text
¿La incorporación de validaciones humanas mejora el desempeño
del modelo?
```

Estas preguntas permiten construir experimentos medibles.

---

# 83. Experimento principal propuesto

## Modelo A — Baseline

```text
Sentence Transformer
+
Cosine Similarity
```

## Modelo B — Híbrido

```text
TF-IDF
+
Embeddings
+
Features estructurales
```

## Modelo C — Supervisado

```text
Features híbridas
+
Etiquetas humanas
+
Logistic Regression
```

Se comparan mediante las métricas definidas.

---

# 84. Experimento de aprendizaje

```text
Dataset inicial
        ↓
Modelo baseline
        ↓
Evaluación
        ↓
Revisión humana
        ↓
Dataset v1
        ↓
Modelo supervisado v1
        ↓
Evaluación
        ↓
Más revisiones
        ↓
Dataset v2
        ↓
Modelo supervisado v2
        ↓
Evaluación
```

La mejora debe demostrarse mediante datos, no asumirse.

---

# 85. Métricas del sistema

Además de las métricas del modelo, pueden medirse:

```text
Tiempo de extracción
Tiempo de comparación
Tiempo de generación del informe
Tiempo total de procesamiento
Tiempo promedio de revisión humana
Cantidad de contenidos analizados
Cantidad de correspondencias
Cantidad de falsos positivos
Cantidad de falsos negativos
```

---

# 86. Indicadores de explicabilidad

Se pueden medir:

```text
Porcentaje de correspondencias con evidencia
Porcentaje de correspondencias con página identificable
Porcentaje de correspondencias validadas por humano
Cantidad de correcciones humanas
```

---

# 87. Manejo de errores

El sistema debe detectar:

```text
PDF inválido
PDF vacío
PDF sin texto
Texto insuficiente
Error de extracción
Error de embedding
Error de procesamiento
```

Cada error debe generar un mensaje comprensible para el usuario.

Ejemplo:

```text
No se pudo extraer suficiente texto del documento.
El archivo parece ser un documento escaneado.
Este tipo de documento será compatible mediante OCR
en la Fase 2.
```

---

# 88. Seguridad y datos

Los documentos pueden contener información académica institucional.

Por ello:

- validar extensiones;
- limitar tamaño;
- evitar ejecución de archivos;
- almacenar archivos de forma controlada;
- evitar exponer rutas internas;
- validar entradas;
- registrar errores sin almacenar información innecesaria;
- separar archivos temporales de persistentes.

---

# 89. Pruebas

## Unitarias

Probar:

```text
normalización
similitud
clasificación
cálculo de score
cálculo global
ranking
```

## Integración

Probar:

```text
PDF → extracción → comparación
```

## API

Probar:

```text
upload
comparison
matches
review
report
```

## Frontend

Probar principalmente:

```text
carga
resultado
detalle
revisión
descarga
```

---

# 90. Datos de prueba

Crear sílabos de prueba controlados:

```text
Caso 1:
Alta coincidencia

Caso 2:
Coincidencia parcial

Caso 3:
Baja coincidencia

Caso 4:
Mismo concepto con diferentes palabras

Caso 5:
Contenidos divididos en unidades diferentes

Caso 6:
Contenido inexistente en el otro sílabo
```

Esto permitirá detectar errores antes de utilizar documentos reales.

---

# 91. Repositorio documental

Se recomienda:

```text
docs/
├── arquitectura.md
├── metodologia.md
├── algoritmo.md
├── informe.md
├── api.md
├── modelo-datos.md
├── experimentos.md
└── decisiones-tecnicas.md
```

---

# 92. Registro de decisiones técnicas

Cada decisión importante debe registrar:

```text
Problema
Alternativas
Decisión
Justificación
Consecuencia
Fecha
```

Ejemplo:

```text
Problema:
Comparar textos académicos con vocabulario diferente.

Alternativas:
TF-IDF
Embeddings
LLM

Decisión:
TF-IDF + embeddings.

Justificación:
Combina coincidencia léxica y semántica y permite
un proceso reproducible.
```

---

# 93. Principio central del sistema

La arquitectura completa debe respetar:

```text
IA propone
        ↓
Sistema explica
        ↓
Humano valida
        ↓
Sistema registra
        ↓
Dataset aprende
        ↓
Modelo mejora
        ↓
Sistema vuelve a evaluar
```

No:

```text
IA decide
        ↓
Sistema acepta automáticamente
```

---

# 94. Resultado esperado del proyecto

Al finalizar la primera etapa, el usuario debe poder realizar:

```text
1. Subir sílabo objetivo.
2. Subir sílabo comparado.
3. Ejecutar análisis.
4. Obtener porcentaje de correspondencia.
5. Ver correspondencias específicas.
6. Ver evidencia.
7. Identificar contenidos no correspondidos.
8. Revisar manualmente las relaciones.
9. Generar y descargar un informe formal.
```

El resultado debe ser comprensible para una persona académica que no conozca los detalles internos del algoritmo.

---

# 95. Resumen de fases

## FASE 1 — Comparación explicable + informe

```text
Entrada:
2 PDF

Salida:
% de correspondencia
+
correspondencias
+
evidencias
+
contenidos no correspondidos
+
informe formal
+
revisión humana
```

## FASE 2 — OCR + aprendizaje supervisado

```text
Entrada:
PDF digital o escaneado

Salida:
OCR
+
dataset
+
modelo supervisado
+
métricas
+
versionado
```

## FASE 3 — Aprendizaje activo y evaluación avanzada

```text
Active Learning
Ground Truth ampliado
Evaluación interevaluador
Experimentos
Mejora controlada del modelo
```

## FASE 4 — Producto ampliado

```text
Usuarios
Historial
PostgreSQL
Reportes avanzados
Gestión documental
```

---

# 96. Orden final recomendado de desarrollo

```text
01. Crear repositorio
02. Definir contratos y entidades
03. Implementar carga de PDF
04. Implementar extracción
05. Implementar estructura
06. Implementar normalización
07. Implementar segmentación
08. Implementar TF-IDF
09. Implementar embeddings
10. Implementar features
11. Implementar score
12. Implementar ranking
13. Implementar comparación bidireccional
14. Implementar API
15. Implementar UI de carga
16. Implementar UI de resultados
17. Implementar evidencia
18. Implementar generador de informe
19. Implementar descarga
20. Implementar revisión humana
21. Persistir revisiones
22. Crear dataset
23. Implementar baseline
24. Implementar modelo supervisado
25. Implementar evaluación
26. Implementar versionado
27. Implementar OCR
28. Implementar Active Learning
```

---

# 97. Definición final del producto

El sistema debe entenderse como:

> **Una plataforma de apoyo a la evaluación de correspondencia académica entre sílabos universitarios, basada en procesamiento de lenguaje natural, análisis semántico y estructural, generación de evidencia y validación humana.**

La Fase 1 debe demostrar el núcleo de esta propuesta:

```text
SÍLABO OBJETIVO
        +
SÍLABO COMPARADO
        ↓
ANÁLISIS COMPUTACIONAL
        ↓
CORRESPONDENCIA
        ↓
EVIDENCIA
        ↓
INFORME FORMAL
        ↓
VALIDACIÓN HUMANA
```

El porcentaje de correspondencia es solamente uno de los resultados. El valor principal del sistema está en explicar **qué coincide, dónde coincide, qué no coincide y qué evidencia sustenta cada relación**.

---

# FASE 1.5 — VISUALIZACIÓN Y TRAZABILIDAD DE EVIDENCIAS EN LOS PDF

## Objetivo

La Fase 1.5 es una ampliación prioritaria posterior a la Fase 1.0. No modifica el algoritmo principal de comparación; agrega una capa visual que permita comprobar directamente dónde encontró evidencia el sistema en el **sílabo objetivo** y en el **sílabo comparado**.

La experiencia debe pasar de:

```text
2 PDF → análisis → porcentaje → informe
```

a:

```text
2 PDF
  ↓
análisis
  ↓
% de correspondencia
  ↓
correspondencias
  ↓
seleccionar una correspondencia
  ↓
abrir ambos PDF
  ↓
saltar a las páginas relevantes
  ↓
señalar las evidencias con cuadros
  ↓
revisión humana
```

## 1. Visor doble

La pantalla de revisión mostrará simultáneamente:

```text
┌─────────────────────────────┬─────────────────────────────┐
│ SÍLABO OBJETIVO             │ SÍLABO COMPARADO            │
│ Página 5 / 12               │ Página 7 / 15              │
│                             │                             │
│        PDF                  │        PDF                  │
│   ┌───────────────┐         │   ┌───────────────┐         │
│   │ EVIDENCIA     │         │   │ EVIDENCIA     │         │
│   └───────────────┘         │   └───────────────┘         │
└─────────────────────────────┴─────────────────────────────┘
```

Debe permitir:

- navegación por páginas;
- zoom;
- desplazamiento;
- ajuste a página/ancho;
- selección de evidencia;
- navegación anterior/siguiente.

## 2. Navegación sincronizada

Al seleccionar una correspondencia, ambos visores deben desplazarse automáticamente hacia sus evidencias.

Ejemplo:

```text
Correspondencia #03

Objetivo:
Unidad II – Normalización — página 6

Comparado:
Unidad II – Formas normales — página 8
```

Resultado:

```text
Visor objetivo   → página 6 → evidencia centrada
Visor comparado → página 8 → evidencia centrada
```

## 3. Coordenadas de evidencia

La extracción debe conservar información espacial del texto. La Fase 1.0 no debe almacenar únicamente texto y página; para la Fase 1.5 se requiere información de posición.

Ejemplo:

```json
{
  "page": 5,
  "text": "Modelo relacional, tablas, atributos",
  "bbox": {
    "x0": 82,
    "y0": 314,
    "x1": 486,
    "y1": 352
  }
}
```

Cuando sea necesario, se conservarán coordenadas por palabra o fragmento para generar cuadros precisos.

## 4. Modelo de evidencia

Una correspondencia debe conservar evidencia independiente para ambos documentos:

```text
ContentMatch
│
├── objective_evidence[]
│      ├── page
│      ├── text
│      └── regions[]
│
└── compared_evidence[]
       ├── page
       ├── text
       └── regions[]
```

Debe soportar relaciones:

```text
1 → 1
1 → N
N → 1
N → N
```

## 5. Cuadros indicadores

Los cuadros se dibujarán como una capa sobre el PDF:

```text
PDF original
      +
EvidenceOverlay
      ↓
Visualización con indicadores
```

El PDF original **no debe modificarse**.

Los cuadros deben seguir correctamente la evidencia cuando el usuario haga zoom o desplazamiento.

## 6. Estados visuales

Se utilizarán inicialmente:

```text
MATCH
PARTIAL_MATCH
UNCERTAIN
NO_MATCH
```

### MATCH

Correspondencia suficientemente fuerte según los criterios configurados.

### PARTIAL_MATCH

Existe relación, pero solo una parte del contenido presenta correspondencia.

### UNCERTAIN

Existe una posible relación, pero la evidencia no es suficientemente concluyente y requiere revisión humana.

### NO_MATCH

No existe evidencia suficiente de correspondencia.

No debe dibujarse artificialmente una correspondencia en el documento cuando no existe una región correspondiente.

## 7. Cuadro para elementos dudosos

Debe existir una representación explícita de casos dudosos, por ejemplo:

```text
┌────────────────────────────┐
│ ? REVISAR                  │
└────────────────────────────┘
```

Esto permite señalar casos similares a los mecanismos visuales de revisión documental utilizados en sistemas de comparación o inspección.

`UNCERTAIN` no significa `NO_MATCH`; significa que el sistema requiere revisión.

## 8. Revisión humana desde el visor

Debajo de los documentos debe aparecer el detalle de la evidencia:

```text
Correspondencia #04

Objetivo: Normalización
Comparado: Formas normales
Score: 0.89

[ MATCH ] [ PARCIAL ] [ DUDOSO ] [ NO MATCH ]
```

El usuario puede modificar la clasificación y agregar una observación.

La predicción original nunca debe sobrescribirse:

```json
{
  "prediction_before": "MATCH",
  "human_decision": "UNCERTAIN"
}
```

## 9. Navegación entre evidencias

Debe existir:

```text
← Anterior       Evidencia 3 de 18       Siguiente →
```

Al cambiar de evidencia:

1. cambia la correspondencia;
2. cambia la página del objetivo;
3. cambia la página del comparado;
4. se actualizan los cuadros;
5. ambos visores hacen scroll hacia la región relevante;
6. se actualiza el detalle.

## 10. Múltiples regiones

Una correspondencia puede estar formada por varias regiones en cualquiera de los dos documentos.

Por ello se requieren arreglos:

```text
objective_evidence.regions[]
compared_evidence.regions[]
```

No se debe limitar el modelo a una única caja por correspondencia.

## 11. Visor web

Se recomienda evaluar **PDF.js** como motor de visualización.

Componentes conceptuales:

```text
ObjectivePdfViewer
ComparedPdfViewer
EvidenceOverlay
EvidenceNavigator
EvidenceDetail
ReviewPanel
```

## 12. Contenido sin correspondencia

Si el sistema no encuentra correspondencia suficiente, debe mostrar el contenido y su mejor candidato, pero no inventar una evidencia equivalente:

```text
Contenido objetivo:
Optimización avanzada de consultas

Página: 9

Mejor candidato:
Consultas SQL

Score: 0.42

Estado:
NO_MATCH
```

## 13. Casos dudosos automáticos

El sistema puede priorizar para revisión casos que presenten, por ejemplo:

```text
score intermedio
+
pequeña diferencia entre candidatos
+
evidencia contradictoria
```

Ejemplo:

```text
Candidato 1: 0.71
Candidato 2: 0.70
```

La fórmula de incertidumbre debe mantenerse configurable y validarse experimentalmente.

No debe asumirse que un valor fijo como `0.68` significa siempre `UNCERTAIN`.

## 14. Impacto en el informe

La Fase 1.5 debe enriquecer el informe formal de la Fase 1.0.

Cada correspondencia podrá incluir:

```text
Sílabo objetivo — página 5
[render de la página con evidencia resaltada]

Sílabo comparado — página 7
[render de la página con evidencia resaltada]
```

Además:

```text
Estado: MATCH
Score: 0.93
Evidencia:
- Modelo relacional
- Tablas
- Atributos
- Relaciones
```

Cuando sea técnicamente viable, el informe PDF incorporará renders de las páginas con los indicadores.

## 15. Trazabilidad

La Fase 1.5 debe mantener:

```text
Documento
   ↓
Página
   ↓
Región
   ↓
Fragmento
   ↓
Contenido
   ↓
Correspondencia
   ↓
Score
   ↓
Clasificación
   ↓
Revisión humana
```

Esto permite auditar por qué una correspondencia fue propuesta y qué evidencia la sustentó.

## 16. Cambios en backend

El flujo pasa de:

```text
PDF → texto → contenido → correspondencia
```

a:

```text
PDF
 ↓
texto + página + coordenadas
 ↓
contenido + regiones
 ↓
correspondencia + evidencias
```

La modificación principal se concentra en:

```text
extracción
persistencia de coordenadas
modelo de evidencia
API
```

No se debe rehacer el algoritmo de comparación de la Fase 1.0.

## 17. Cambios en API

Puede incorporarse:

```http
GET /api/comparisons/{id}/evidence
```

o devolver las evidencias dentro de:

```http
GET /api/comparisons/{id}/matches
```

La respuesta debe incluir:

```text
match
score
classification
objective_evidence
compared_evidence
page
regions
```

## 18. Persistencia

Entidad lógica recomendada:

```text
EvidenceRegion
```

Campos conceptuales:

```text
id
match_id
syllabus_id
content_id
page_number
text
x0
y0
x1
y1
evidence_type
created_at
```

Tipos de evidencia:

```text
LEXICAL
SEMANTIC
STRUCTURAL
COMBINED
```

La implementación inicial puede mantener las regiones embebidas si simplifica el desarrollo, siempre que no se pierda trazabilidad.

## 19. Relación con el aprendizaje supervisado

La Fase 1.5 mejora el futuro dataset porque permite registrar no solo la corrección humana, sino la evidencia que el evaluador revisó.

Ejemplo:

```text
Predicción: MATCH
Evidencia: página 5 ↔ página 7
Decisión: UNCERTAIN
Justificación: la coincidencia textual no representa equivalencia completa.
```

Esto permitirá estudiar posteriormente qué tipos de evidencia provocan falsos positivos o falsos negativos.

## 20. Relación con Active Learning

Los casos dudosos pueden priorizarse para revisión:

```text
Comparación
    ↓
Casos inciertos
    ↓
Visualización de evidencia
    ↓
Revisión humana
    ↓
Etiqueta
    ↓
Dataset
```

## 21. Reglas de calidad

1. Nunca modificar el PDF original.
2. Toda evidencia debe estar asociada a una página.
3. Toda evidencia visual debe tener coordenadas.
4. Las coordenadas deben permanecer alineadas durante el zoom.
5. Seleccionar una correspondencia debe sincronizar ambos documentos.
6. Una correspondencia puede tener múltiples regiones.
7. `UNCERTAIN` no significa `NO_MATCH`.
8. La decisión humana nunca elimina la predicción original.
9. El usuario debe poder navegar entre evidencias.
10. La trazabilidad debe conservar documento, página, región y correspondencia.
11. Los indicadores no deben depender exclusivamente del color.
12. Las evidencias deben poder reutilizarse para el informe.
13. Los casos dudosos deben poder convertirse en datos de revisión.
14. La visualización no debe alterar el score calculado por la Fase 1.0.

## 22. Criterios de aceptación

### Visores

- [ ] Se visualiza el sílabo objetivo.
- [ ] Se visualiza el sílabo comparado.
- [ ] Ambos PDFs aparecen simultáneamente.
- [ ] Se puede cambiar de página.
- [ ] Se puede hacer zoom.
- [ ] Se puede desplazar el documento.
- [ ] Se puede ajustar página/ancho.

### Evidencias

- [ ] Cada correspondencia puede abrirse.
- [ ] Se muestra la página del objetivo.
- [ ] Se muestra la página del comparado.
- [ ] El sistema salta automáticamente a las páginas.
- [ ] Se dibujan cuadros sobre las evidencias.
- [ ] Los cuadros se mantienen alineados con el texto.
- [ ] Se soportan múltiples regiones.
- [ ] Se muestran los fragmentos asociados.

### Revisión

- [ ] Se puede marcar MATCH.
- [ ] Se puede marcar PARTIAL.
- [ ] Se puede marcar UNCERTAIN.
- [ ] Se puede marcar NO MATCH.
- [ ] Se puede registrar una observación.
- [ ] Se conserva la predicción original.
- [ ] Se conserva la decisión humana.

### Navegación

- [ ] Existe anterior/siguiente.
- [ ] Se indica la evidencia actual.
- [ ] Ambos visores se sincronizan al cambiar de evidencia.
- [ ] El sistema centra la región relevante.

### Informe

- [ ] El informe puede incluir las evidencias.
- [ ] Se identifica la página de origen.
- [ ] Se pueden incorporar renders de las páginas con indicadores.
- [ ] El PDF original permanece intacto.

## 23. Prioridad actual

```text
FASE 1.0 — COMPLETADA
Comparación + porcentaje + informe
        │
        ▼
FASE 1.5 — PRIORIDAD ACTUAL
Visor doble + cuadros de evidencia + revisión visual
        │
        ▼
FASE 2.0
OCR + dataset + modelo supervisado
        │
        ▼
FASE 3.0
Active Learning + evaluación científica avanzada
        │
        ▼
FASE 4.0
Producto ampliado
```

La Fase 1.5 debe ejecutarse antes del aprendizaje supervisado porque proporciona una interfaz adecuada para generar revisiones humanas trazables.

## 24. Orden actualizado de implementación

```text
01. Crear repositorio
02. Definir contratos y entidades
03. Implementar carga de PDF
04. Implementar extracción
05. Implementar estructura
06. Implementar normalización
07. Implementar segmentación
08. Implementar TF-IDF
09. Implementar embeddings
10. Implementar features
11. Implementar score
12. Implementar ranking
13. Implementar comparación bidireccional
14. Implementar API
15. Implementar UI de carga
16. Implementar UI de resultados
17. Implementar evidencia textual
18. Implementar generador de informe
19. Implementar descarga
20. Implementar revisión humana

--- FASE 1.0 COMPLETADA ---

21. Implementar extracción/persistencia de coordenadas
22. Implementar visor PDF objetivo
23. Implementar visor PDF comparado
24. Implementar EvidenceOverlay
25. Implementar navegación por páginas
26. Implementar navegación sincronizada
27. Implementar cuadros de evidencia
28. Implementar múltiples regiones
29. Implementar estados MATCH/PARTIAL/UNCERTAIN/NO_MATCH
30. Implementar marcado manual de casos dudosos
31. Persistir revisión y justificación
32. Integrar evidencias visuales al informe

--- FASE 1.5 COMPLETADA ---

33. Crear dataset
34. Implementar baseline
35. Implementar modelo supervisado
36. Implementar evaluación
37. Implementar versionado
38. Implementar OCR
39. Implementar Active Learning
40. Implementar evaluación científica avanzada
```

## 25. Definición final de las primeras fases

### FASE 1.0

> **Comparación explicable + informe formal**

```text
2 PDFs
 ↓
Extracción
 ↓
Estructuración
 ↓
Comparación
 ↓
Porcentaje
 ↓
Correspondencias
 ↓
Evidencia
 ↓
Informe
 ↓
Revisión humana
```

### FASE 1.5

> **Visualización y trazabilidad de evidencias en ambos documentos**

```text
Comparación existente
 ↓
Abrir PDF objetivo + PDF comparado
 ↓
Seleccionar correspondencia
 ↓
Ir a página objetivo
 ↓
Ir a página comparada
 ↓
Dibujar cuadros de evidencia
 ↓
Mostrar detalle
 ↓
Marcar MATCH / PARCIAL / DUDOSO / NO MATCH
 ↓
Registrar decisión
 ↓
Actualizar informe
```

### FASE 2.0

> **OCR + aprendizaje supervisado**

```text
PDF digital/escaneado
 ↓
OCR
 ↓
Extracción estructurada
 ↓
Dataset de revisiones
 ↓
Entrenamiento
 ↓
Evaluación
 ↓
Modelo versionado
```
