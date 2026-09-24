# Reglas de Implementación y Guía de Desarrollo
## Sistema Inteligente para Comparación de Sílabos Universitarios

**Versión:** 1.0  
**Fecha:** Septiembre 2026  
**Documentos vinculados:**  
- [PLANTEAMIENTO_IMPLEMENTACION_COMPARACION_SILABOS.md](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/docs/PLANTEAMIENTO_IMPLEMENTACION_COMPARACION_SILABOS.md)  
- [FLUJO_FASE_1.md](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/docs/FLUJO_FASE_1.md)  
- [TASKS.md](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/docs/TASKS.md)

---

## 1. Principio Fundamental del Sistema

El sistema implementa una **plataforma de pre-evaluación computacional explicable**, no un tribunal académico automatizado:

$$\text{IA propone} \longrightarrow \text{Sistema explica con evidencia} \longrightarrow \text{Humano valida} \longrightarrow \text{Sistema registra de forma inmutable}$$

Queda estrictamente prohibido que el sistema declare cursos como "oficialmente convalidados" o que un modelo de lenguaje actúe como juez final no auditable.

---

## 2. Reglas de Arquitectura y Diseño de Software

### 2.1 Monolito Modular y Clean Architecture
1. **Dominio puro (`app/domain/`):**
   - Las entidades, objetos de valor y reglas de negocio no deben importar ni depender de frameworks web (`FastAPI`), ORMs (`SQLAlchemy`), librerías de extracción (`PyMuPDF`) ni librerías de NLP/ML (`scikit-learn`, `SentenceTransformers`, `torch`).
   - El dominio debe modelarse con clases puras de Python y validaciones internas.
2. **Capa de Aplicación (`app/application/`):**
   - Define los casos de uso (orquestadores de flujos) y los puertos/interfaces de entrada y salida (interfaces de repositorios, extractores, vectorizadores).
3. **Capa de Infraestructura (`app/infrastructure/`):**
   - Implementa los adaptadores técnicos concretos:
     - `pdf/`: Extracción mediante `PyMuPDF`.
     - `nlp/` y `embeddings/`: Embeddings de Sentence Transformers, TF-IDF de scikit-learn.
     - `persistence/`: SQLite y repositorios de base de datos.
     - `reports/`: Generador de reportes PDF con ReportLab y plantillas HTML.
4. **Capa de API (`app/api/`):**
   - Exclusivamente responsable de endpoints HTTP, serialización/deserialización con Pydantic y códigos de estado HTTP semánticos.
5. **Frontend Modular (`frontend/`):**
   - React + TypeScript con Vite.
   - Separación estricta entre servicios API (`services/`), tipos (`types/`), componentes visuales (`components/`) y vistas completas (`pages/`).
   - Cero uso de `any` en TypeScript; todo tipo de dato transferido desde el backend debe reflejarse en un contrato de tipos fuertemente tipado.

### 2.2 Prohibiciones Estrictas de Ingeniería
- **NO microservicios:** Mantener una arquitectura monolítica modular para garantizar simplicidad, consistencia transaccional y bajo costo operativo en Fase 1.
- **NO LLM como árbitro de correspondencia:** Prohibido delegar el cálculo del score a un prompt arbitrario de un LLM. El cálculo debe ser 100% auditable, matemático y reproducible (TF-IDF + embeddings densos + solapamiento de n-gramas + pesos configurables).
- **NO sobrescribir predicciones IA:** La tabla `ContentMatch` guarda la predicción original de la máquina. La revisión del docente o evaluador se guarda en `Review`. Jamás mutar la predicción original para preservar la trazabilidad científica.
- **NO pérdida de datos originales:** Cada contenido segmentado debe guardar su cita literal, orden y número de página original en el PDF.
- **NO data leakage:** Separar rigurosamente los datos de entrenamiento y evaluación por universidad/asignatura cuando se construya el dataset supervisado.

---

## 3. Reglas de Explicabilidad y Calidad de Salida

1. **Nunca entregar un porcentaje aislado:** Cualquier salida porcentual de correspondencia debe desglosarse en:
   - Cobertura de objetivos ($S_{obj} \rightarrow S_{cmp}$).
   - Cobertura de comparados ($S_{cmp} \rightarrow S_{obj}$).
   - Tabla de correspondencias con evidencia observable (palabras clave, valores de similitud léxica y semántica).
   - Lista explícita de temas/contenidos no cubiertos o sin correspondencia suficiente.
2. **Trazabilidad a nivel de página:** Toda correspondencia reportada debe indicar el número de página exacto donde se ubica el texto en ambos PDFs.
3. **Reproducibilidad y Versionado:** Cada ejecución de comparación debe almacenar los parámetros exactos utilizados:
   - Versión del algoritmo (ej. `baseline-001`).
   - Pesos asignados ($w_{sem}, w_{lex}, w_{key}, w_{est}$).
   - Umbrales categóricos empleados.
4. **Cláusula de Responsabilidad Institucional:** Todo informe generado (HTML o PDF) y toda pantalla de resultados debe incluir obligatoriamente el descargo de responsabilidad académica:
   > *"El presente resultado es una pre-evaluación computacional explicable de correspondencia académica. No sustituye la evaluación oficial ni constituye resolución vinculante de convalidación."*

---

## 4. Reglas de Desarrollo de Código y Pruebas

1. **Tipado Estricto:**
   - En Python: uso obligatorio de Type Hints en todas las funciones y métodos públicos (`mypy` compliant).
   - En TypeScript: `strict: true` activado en `tsconfig.json`. Prohibido el uso de `any` (usar `unknown` con type guards o tipos definidos).
2. **Manejo Defensivo de Excepciones:**
   - No usar bloques `try/except: pass`.
   - Crear excepciones de dominio específicas (ej. `PdfCorruptedError`, `InsufficientDigitalTextError`, `SyllabusNotFoundError`).
   - Mapear las excepciones de dominio a respuestas HTTP claras (ej. HTTP 422 para PDFs escaneados sin texto digital, HTTP 404 para entidades no encontradas).
3. **Estrategia de Pruebas Automatizadas:**
   - **Pruebas unitarias (`tests/unit/`):** Obligatorias para normalizadores, cálculos de similitud léxica/semántica, cálculo de scores compuestos, algoritmos de ranking y generadores de evidencias.
   - **Pruebas de integración (`tests/integration/`):** Obligatorias para extracción de texto con PyMuPDF, repositorios SQLite y endpoints FastAPI.
   - **Datos de prueba reproducibles (`tests/fixtures/`):** Mantener un catálogo de sílabos sintéticos de prueba con casos conocidos (coincidencia idéntica, parafraseo, unidades permutadas, brechas de contenido).

---

## 5. Instrucciones para la Gestión y Actualización de TASKS (`docs/TASKS.md`)

El documento [docs/TASKS.md](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/docs/TASKS.md) es el artefacto vivo central para auditar el avance del proyecto. Debe mantenerse rigurosamente actualizado siguiendo estas directrices:

### 5.1 Protocolo al Iniciar Cada Sesión de Trabajo
1. **Inspección del estado actual:**
   - Leer `docs/TASKS.md` antes de iniciar cualquier desarrollo.
   - Identificar las tareas que se encuentran en estado `[ ] Pendiente` según la prioridad de los paquetes de trabajo.
2. **Definición de alcance de la sesión:**
   - Seleccionar un conjunto delimitado de tareas a ejecutar.
   - Cambiar su estado a `[/] En Progreso`.
   - Respetar el orden secuencial de dependencias: no implementar interfaces o APIs antes de tener las entidades de dominio y casos de uso listos.

### 5.2 Protocolo Durante la Sesión de Trabajo
1. Ejecutar las tareas seleccionadas cumpliendo con los estándares de Clean Architecture y tipado estricto.
2. Cada funcionalidad completada debe acompañarse de sus pruebas unitarias o de integración correspondientes.
3. Si durante la sesión surge un nuevo requerimiento, riesgo o tarea no contemplada, debe agregarse en el paquete de trabajo correspondiente bajo la numeración correspondiente.

### 5.3 Protocolo al Finalizar Cada Sesión de Trabajo
1. **Actualización de Casillas de Verificación:**
   - Cambiar el estado de las tareas finalizadas y probadas a `[x] Completado`.
   - Si una tarea quedó a medias, mantenerla como `[/] En Progreso` con una nota aclaratoria de lo que falta.
2. **Actualización del Resumen Ejecutivo:**
   - Recalcular el porcentaje de avance por paquete y el total general en la tabla de resumen.
3. **Registro en la Bitácora de Sesiones:**
   - Agregar una nueva entrada en la sección **Bitácora de Sesiones de Trabajo** con la siguiente estructura obligatoria:
     ```markdown
     ### Sesión NN — YYYY-MM-DD
     - **Objetivos de la sesión:** [Resumen de lo planificado para el día]
     - **Tareas completadas:** [Lista de IDs de tareas finalizadas, ej. TASK-02.1, TASK-02.2]
     - **Decisiones técnicas adoptadas:** [Registro breve de decisiones arquitecturales, dependencias o fórmulas adoptadas]
     - **Bloqueadores / Riesgos identificados:** [Problemas pendientes o riesgos de rendimiento/compatibilidad]
     - **Próximas tareas para la siguiente sesión:** [Tareas prioritarias inmediatas]
     ```
4. **Validación de Integridad:**
   - Verificar que no existan discrepancias entre el código en disco y el estado marcado en `TASKS.md`.
