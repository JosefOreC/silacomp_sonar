# Registro de Tareas y Avances de Implementación (TASKS)
## Sistema Inteligente para Comparación de Sílabos Universitarios — Fase 1

**Versión:** 1.0  
**Última actualización:** 2026-09-24  
**Documento de referencia:** [PLANTEAMIENTO_IMPLEMENTACION_COMPARACION_SILABOS.md](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/docs/PLANTEAMIENTO_IMPLEMENTACION_COMPARACION_SILABOS.md) | [FLUJO_FASE_1.md](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/docs/FLUJO_FASE_1.md)  
**Normas de actualización:** Ver [REGLAS_IMPLEMENTACION.md](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/docs/REGLAS_IMPLEMENTACION.md)

---

## Convenciones de Estado

- `[ ]` **Pendiente:** Tarea planificada aún no iniciada.
- `[/]` **En Progreso:** Tarea actualmente en desarrollo en la sesión activa.
- `[x]` **Completado:** Tarea implementada, probada y validada según criterios de aceptación.
- `[-]` **Descartado / Pospuesto:** Tarea aplazada justificadamente a una fase posterior.

---

## Resumen Ejecutivo de Avance — Fase 1

| Módulo / Paquete de Trabajo | Estado General | % Completado | Tareas Hechas | Total Tareas |
|---|:---:|:---:|:---:|:---:|
| 1. Configuración Inicial y Entorno | Completado | 100% | 4 | 4 |
| 2. Modelo de Dominio y Contratos | Completado | 100% | 4 | 4 |
| 3. Ingesta y Extracción PDF | Completado | 100% | 4 | 4 |
| 4. Estructuración y Segmentación | Completado | 100% | 4 | 4 |
| 5. Motor de Similitud y NLP | Completado | 100% | 5 | 5 |
| 6. Algoritmo de Comparación y Scoring | Completado | 100% | 4 | 4 |
| 7. Persistencia y Base de Datos | Completado | 100% | 3 | 3 |
| 8. API REST (FastAPI) | Completado | 100% | 5 | 5 |
| 9. Generador de Informes (HTML/PDF) | Completado | 100% | 4 | 4 |
| 10. Frontend: Dashboard y Carga | Completado | 100% | 4 | 4 |
| 11. Frontend: Resultados y Evidencias | Completado | 100% | 4 | 4 |
| 12. Frontend: Revisión Humana | Completado | 100% | 4 | 4 |
| 13. Pruebas Automatizadas y Validación | Completado | 100% | 4 | 4 |
| **SUBTOTAL FASE 1.0** | **Completado** | **100%** | **49** | **49** |
| 14. Fase 1.5: Extracción Espacial y Bounding Boxes | Completado | 100% | 4 | 4 |
| 15. Fase 1.5: API de PDF y Consulta de Evidencias | Completado | 100% | 3 | 3 |
| 16. Fase 1.5: Frontend — Visor Doble y EvidenceOverlay | Completado | 100% | 4 | 4 |
| 17. Fase 1.5: Frontend — Navegación Sincronizada y Revisión | Completado | 100% | 4 | 4 |
| 18. Fase 1.5: Evidencias en Reportes y Pruebas E2E | Pendiente | 0% | 0 | 2 |
| **TOTAL GENERAL (FASE 1.0 + FASE 1.5)** | **En Progreso** | **97%** | **64** | **66** |

---

## Desglose Granular de Tareas — Fase 1

### Paquete 1: Configuración Inicial, Repositorio y Entorno
- [x] **TASK-01.1:** Documentar especificación de flujo de Fase 1 y reglas de desarrollo. *(Completado el 2026-09-24)*
- [x] **TASK-01.2:** Inicializar estructura del repositorio (`backend/`, `frontend/`, `docs/`, `tests/`, `data/`). *(Completado el 2026-09-24)*
- [x] **TASK-01.3:** Configurar entorno virtual backend con Python (dependencias: `fastapi`, `uvicorn`, `pymupdf`, `scikit-learn`, `sentence-transformers`, `pydantic`, `reportlab`, `pytest`). *(Completado el 2026-09-24)*
- [x] **TASK-01.4:** Inicializar proyecto frontend con React + TypeScript + Vite y estilos base con diseño académico oscuro. *(Completado el 2026-09-24)*

---

### Paquete 2: Modelo de Dominio y Contratos (Clean Architecture)
- [x] **TASK-02.1:** Implementar entidades de dominio inmutables e independientes (`Syllabus`, `SyllabusPage`, `SyllabusSection`, `ContentItem`). *(Completado el 2026-09-24)*
- [x] **TASK-02.2:** Implementar entidades de comparación (`Comparison`, `ContentMatch`, `MatchEvidence`, `ScoreBreakdown`). *(Completado el 2026-09-24)*
- [x] **TASK-02.3:** Implementar entidades de revisión y trazabilidad (`Review`, `DatasetExample`, `ModelVersion`). *(Completado el 2026-09-24)*
- [x] **TASK-02.4:** Definir puertos/interfaces de abstracción (repositorios de persistencia, extractores de texto, vectorizadores). *(Completado el 2026-09-24)*

---

### Paquete 3: Ingesta, Validación y Extracción PDF
- [x] **TASK-03.1:** Implementar servicio de validación de documentos (formato PDF, tamaño máximo, archivo no vacío, verificación de texto digital). *(Completado el 2026-09-24)*
- [x] **TASK-03.2:** Implementar adaptador de extracción con `PyMuPDF` extrayendo texto estructurado por página. *(Completado el 2026-09-24)*
- [x] **TASK-03.3:** Implementar manejo de errores para PDFs escaneados o sin capa de texto (mensaje de advertencia informativo sobre OCR para Fase 2). *(Completado el 2026-09-24)*
- [x] **TASK-03.4:** Pruebas unitarias para extracción y validación de PDFs de prueba. *(Completado el 2026-09-24)*

---

### Paquete 4: Estructuración y Segmentación de Contenidos
- [x] **TASK-04.1:** Implementar detector heurístico de secciones académicas estándar (Datos generales, Sumilla, Competencias, Unidades, Metodología, Bibliografía). *(Completado el 2026-09-24)*
- [x] **TASK-04.2:** Implementar segmentador de unidades temáticas en `ContentItem` discretos con referencias de página y orden. *(Completado el 2026-09-24)*
- [x] **TASK-04.3:** Implementar normalizador de texto controlado (minúsculas, limpieza de caracteres, stopwords académicas preservando vocabulario técnico). *(Completado el 2026-09-24)*
- [x] **TASK-04.4:** Pruebas unitarias de segmentación con variantes estructurales de sílabos. *(Completado el 2026-09-24)*

---

### Paquete 5: Motor de Similitud y NLP
- [x] **TASK-05.1:** Implementar módulo de similitud léxica mediante TF-IDF + Cosine Similarity. *(Completado el 2026-09-24)*
- [x] **TASK-05.2:** Implementar módulo de similitud semántica con Sentence Transformers (modelo multilingual local). *(Completado el 2026-09-24)*
- [x] **TASK-05.3:** Implementar extractor de overlap de términos clave y n-gramas técnicos compartidos. *(Completado el 2026-09-24)*
- [x] **TASK-05.4:** Implementar cálculo de similitud estructural y contextual (unidad y orden relativo). *(Completado el 2026-09-24)*
- [x] **TASK-05.5:** Pruebas unitarias para cálculo independiente de cada vector de características. *(Completado el 2026-09-24)*

---

### Paquete 6: Algoritmo de Comparación, Scoring y Clasificación
- [x] **TASK-06.1:** Implementar fórmula de score compuesto con pesos configurables ($w_{sem}, w_{lex}, w_{key}, w_{est}$). *(Completado el 2026-09-24)*
- [x] **TASK-06.2:** Implementar clasifición categórica con umbrales configurables (`MATCH`, `PARTIAL_MATCH`, `UNCERTAIN`, `NO_MATCH`). *(Completado el 2026-09-24)*
- [x] **TASK-06.3:** Implementar soporte para relaciones cardinales múltiples (1:1, 1:N, N:1). *(Completado el 2026-09-24)*
- [x] **TASK-06.4:** Implementar cálculo de métricas bidireccionales de cobertura ($S_{obj} \rightarrow S_{cmp}$ y $S_{cmp} \rightarrow S_{obj}$) y porcentaje global. *(Completado el 2026-09-24)*

---

### Paquete 7: Persistencia y Base de Datos (SQLite)
- [x] **TASK-07.1:** Configurar capa de infraestructura de persistencia SQLite y esquema relacional relacional de Fase 1. *(Completado el 2026-09-24)*
- [x] **TASK-07.2:** Implementar repositorios para sílabos, páginas, contenidos, comparaciones y coincidencias. *(Completado el 2026-09-24)*
- [x] **TASK-07.3:** Implementar persistencia inmutable de revisiones humanas y staging de ejemplos de dataset. *(Completado el 2026-09-24)*

---

### Paquete 8: API REST (FastAPI)
- [x] **TASK-08.1:** Implementar endpoints de carga de sílabos (`POST /api/syllabi/upload`). *(Completado el 2026-09-24)*
- [x] **TASK-08.2:** Implementar endpoint para ejecutar comparación (`POST /api/comparisons`). *(Completado el 2026-09-24)*
- [x] **TASK-08.3:** Implementar endpoints de consulta de resultados (`GET /api/comparisons/{id}`, `/matches`, `/unmatched`). *(Completado el 2026-09-24)*
- [x] **TASK-08.4:** Implementar endpoints de revisión humana (`POST /api/reviews`, `GET /api/reviews/comparison/{id}`). *(Completado el 2026-09-24)*
- [x] **TASK-08.5:** Implementar endpoint de estadísticas de dataset (`GET /api/dataset/statistics`). *(Completado el 2026-09-24)*

---

### Paquete 9: Generador de Informes Formales (HTML y PDF)
- [x] **TASK-09.1:** Diseñar plantilla de informe formal HTML con portada institucional, estilos `@media print`, resumen ejecutivo y desglose. *(Completado el 2026-09-24)*
- [x] **TASK-09.2:** Implementar generador de informe PDF formal utilizando `ReportLab` con todas las 12 secciones estándar del planteamiento. *(Completado el 2026-09-24)*
- [x] **TASK-09.3:** Incorporar cláusula de descargo de responsabilidad académica y ficha técnica de trazabilidad metodológica. *(Completado el 2026-09-24)*
- [x] **TASK-09.4:** Implementar endpoint para descarga directa del informe (`GET /api/comparisons/{id}/report/pdf` y `/html`). *(Completado el 2026-09-24)*

---

### Paquete 10: Frontend — Dashboard e Ingesta de Sílabos
- [x] **TASK-10.1:** Configurar cliente HTTP, enrutamiento y tema oscuro académico (paleta `#0B0F14`, `#121820`, `#1A222D`, `#F1F5F9`). *(Completado el 2026-09-24)*
- [x] **TASK-10.2:** Implementar componente de carga de sílabos con zona de arrastrar y soltar (Drag & Drop) y selección de roles (Objetivo / Comparado). *(Completado el 2026-09-24)*
- [x] **TASK-10.3:** Implementar vista de progreso de análisis con indicadores de etapa (Extracción $\rightarrow$ Segmentación $\rightarrow$ Comparación). *(Completado el 2026-09-24)*
- [x] **TASK-10.4:** Implementar pantalla de Dashboard con resumen de comparaciones anteriores y modelos activos. *(Completado el 2026-09-24)*

---

### Paquete 11: Frontend — Visualización de Resultados y Evidencias
- [x] **TASK-11.1:** Implementar encabezado de resultados con porcentaje global, cobertura bidireccional y tarjetas de síntesis (`ComparisonScore.tsx`). *(Completado el 2026-09-24)*
- [x] **TASK-11.2:** Implementar tabla interactiva de correspondencias con filtrado por categoría (`MATCH`, `PARTIAL_MATCH`, `UNCERTAIN`, `NO_MATCH`) (`MatchTable.tsx`). *(Completado el 2026-09-24)*
- [x] **TASK-11.3:** Implementar panel de detalle de correspondencia con desglose de scores, páginas de origen, fragmentos textuales y palabras clave resaltadas (`EvidencePanel.tsx`). *(Completado el 2026-09-24)*
- [x] **TASK-11.4:** Implementar sección de contenidos no correspondidos para ambos sílabos (`UnmatchedPanel.tsx`). *(Completado el 2026-09-24)*

---

### Paquete 12: Frontend — Revisión Humana e Informes
- [x] **TASK-12.1:** Implementar controles de validación en la UI (confirmar `MATCH`, corregir a `PARTIAL`, rechazar a `NO_MATCH`). *(Completado el 2026-09-24)*
- [x] **TASK-12.2:** Implementar modal para ingresar justificación académica del cambio y tipo de error detectado (`ReviewModal.tsx`). *(Completado el 2026-09-24)*
- [x] **TASK-12.3:** Implementar visualización que muestre claramente la predicción original de la IA junto a la decisión del evaluador (`AuditDatasetView.tsx`). *(Completado el 2026-09-24)*
- [x] **TASK-12.4:** Implementar botón y modal de descarga/previsualización del informe formal (HTML/PDF). *(Completado el 2026-09-24)*

---

### Paquete 13: Pruebas Automatizadas y Validación de Calidad
- [x] **TASK-13.1:** Crear suite de datos de prueba sintéticos con casos controlados (caso 1: alta coincidencia, caso 2: parcial, caso 3: baja, caso 4: parafraseo, caso 5: brechas). *(Completado el 2026-09-24)*
- [x] **TASK-13.2:** Pruebas unitarias de algoritmos de similitud, scoring y ranking con `pytest`. *(Completado el 2026-09-24)*
- [x] **TASK-13.3:** Pruebas de integración extremo a extremo del flujo API: Carga $\rightarrow$ Comparación $\rightarrow$ Reporte $\rightarrow$ Revisión (`test_e2e_flow.py`). *(Completado el 2026-09-24)*
- [x] **TASK-13.4:** Verificación y validación de los criterios de aceptación formales de la Fase 1 (`README.md` y suite completa de 28 tests). *(Completado el 2026-09-24)*

---

## Desglose Granular de Tareas — Fase 1.5: Visualización y Trazabilidad en PDF

### Paquete 14: Extracción Espacial y Bounding Boxes (Backend)
- [x] **TASK-14.1:** Extender `PyMuPdfExtractor` para registrar dimensiones de página (`page_width`, `page_height`) y extraer bloques textuales con coordenadas `(x0, y0, x1, y1)`. *(Completado el 2026-09-24)*
- [x] **TASK-14.2:** Implementar entidad de dominio inmutable `EvidenceRegion` y servicio de búsqueda y mapeo espacial de fragmentos de evidencia (`page.search_for` en `SpatialLocatorService`). *(Completado el 2026-09-24)*
- [x] **TASK-14.3:** Actualizar `CompareSyllabiUseCase` y contratos de persistencia para asociar arreglos de regiones espaciales (`objective_evidence` y `compared_evidence`) a cada `ContentMatch`. *(Completado el 2026-09-24)*
- [x] **TASK-14.4:** Pruebas unitarias para extracción de coordenadas y validación de bounding boxes de evidencia (`test_spatial_locator.py`). *(Completado el 2026-09-24)*

---

### Paquete 15: API de PDF y Consulta de Evidencias (Backend)
- [x] **TASK-15.1:** Implementar endpoint para streaming del archivo PDF original de un sílabo (`GET /api/syllabi/{id}/pdf`). *(Completado el 2026-09-24)*
- [x] **TASK-15.2:** Implementar endpoint para consulta de evidencias espaciales con coordenadas y dimensiones (`GET /api/comparisons/{id}/evidence` y detalle por match). *(Completado el 2026-09-24)*
- [x] **TASK-15.3:** Pruebas de integración para endpoint de streaming binario de PDF y serialización de regiones de evidencia (`test_fase1_5_endpoints.py`). *(Completado el 2026-09-24)*

---

### Paquete 16: Frontend — Visor Doble y Capa de Evidencia (EvidenceOverlay)
- [x] **TASK-16.1:** Configurar cliente de renderizado de PDF en React (`pdfjs-dist` con worker local en `pdfSetup.ts`) con escalado responsivo. *(Completado el 2026-09-24)*
- [x] **TASK-16.2:** Implementar componente de visor unitario `PdfDocumentViewer.tsx` con controles de zoom (Ajustar a ancho, Ajustar a página, 100%, 150%) y navegación de páginas. *(Completado el 2026-09-24)*
- [x] **TASK-16.3:** Implementar componente de superposición visual no destructiva `EvidenceOverlay.tsx` para dibujar cuadros delimitadores con estados (`MATCH`, `PARTIAL_MATCH`, `UNCERTAIN`, `NO_MATCH`) y aristas ortogonales de 90° (`0px`). *(Completado el 2026-09-24)*
- [x] **TASK-16.4:** Implementar contenedor principal `DualPdfViewer.tsx` mostrando el sílabo requerido (izquierda) y el comparado (derecha) simultáneamente. *(Completado el 2026-09-24)*

---

### Paquete 17: Frontend — Navegación Sincronizada y Revisión desde Visor
- [x] **TASK-17.1:** Implementar barra de control `EvidenceNavigator.tsx` con botones Anterior / Siguiente, contador de evidencia (`Correspondencia X de Y`), atajos de teclado y score. *(Completado el 2026-09-24)*
- [x] **TASK-17.2:** Implementar sincronización automática bidireccional: al seleccionar una correspondencia, ambos visores saltan a sus páginas y centran la evidencia. *(Completado el 2026-09-24)*
- [x] **TASK-17.3:** Implementar panel de dictamen docente al pie del visor (`ViewerReviewPanel.tsx`) para ratificar, ajustar o marcar dudoso (`? REVISAR`) con justificación inmutable. *(Completado el 2026-09-24)*
- [x] **TASK-17.4:** Integrar botón de apertura del visor doble desde la matriz de correspondencias (`MatchTable.tsx`) y la ficha técnica (`EvidencePanel.tsx`). *(Completado el 2026-09-24)*

---

### Paquete 18: Evidencias en Reportes y Validación E2E de Fase 1.5
- [ ] **TASK-18.1:** Extender el generador de reportes PDF formal para incorporar referencias de coordenadas y trazabilidad espacial de evidencias.
- [ ] **TASK-18.2:** Pruebas automatizadas de extremo a extremo cubriendo el flujo completo de la Fase 1.5: Carga $\rightarrow$ Comparación $\rightarrow$ Visor Doble $\rightarrow$ Coordenadas $\rightarrow$ Revisión.

---

---

## Bitácora de Sesiones de Trabajo

### Sesión 01 — 2026-09-24
- **Objetivos de la sesión:**
  - Leer y analizar la totalidad de la especificación técnica institucional.
  - Diseñar el flujo detallado de la Fase 1.
  - Establecer el sistema de control de tareas granular.
  - Definir las reglas de desarrollo e instrucciones de actualización.
- **Tareas completadas:**
  - `TASK-01.1`: Creación de `docs/FLUJO_FASE_1.md`, `docs/TASKS.md`, `docs/REGLAS_IMPLEMENTACION.md` y `.agents/rules/reglas_implementacion.md`.
- **Decisiones técnicas adoptadas:**
  - Adopción estricta de Clean Architecture / Monolito modular.
  - Se prohíbe el uso de LLMs como jueces evaluadores automáticos; el motor de correspondencia se basará exclusivamente en modelos de NLP reproducibles y deterministas.
  - Separación física e inmutable entre predicción del modelo y revisión humana.
- **Bloqueadores / Riesgos identificados:**
  - Ninguno en esta sesión inicial de definición.
- **Próximas tareas para la Sesión 02:**
  - Inicializar la estructura física y dependencias (`TASK-01.2`, `TASK-01.3`, `TASK-01.4`).
  - Implementar las entidades de dominio y contratos (`TASK-02.1` a `TASK-02.4`).

### Sesión 02 — 2026-09-24
- **Objetivos de la sesión:**
  - Inicializar el esqueleto del repositorio con arquitectura limpia y monolito modular.
  - Configurar el entorno virtual Python (3.12) y todas las librerías científicas (`pymupdf`, `scikit-learn`, `sentence-transformers`, `fastapi`, `reportlab`).
  - Configurar el frontend con React + TypeScript + Vite y estilos académicos oscuros.
  - Implementar todas las entidades de dominio y puertos de abstracción libres de dependencias externas.
  - Implementar suite de pruebas unitarias de dominio y validar con pytest.
- **Tareas completadas:**
  - `TASK-01.2`: Inicialización de estructura de carpetas (`backend/`, `frontend/`, `tests/`, `data/`).
  - `TASK-01.3`: Configuración de `.venv` con Python 3.12, `requirements.txt` y resolución de hosts confiables de pip.
  - `TASK-01.4`: Creación de proyecto Vite React-TS en `frontend/`, diseño base con paleta oscura institucional y cliente API tipado.
  - `TASK-02.1`: Implementación de entidades de dominio puro `Syllabus`, `SyllabusPage`, `SyllabusSection`, `ContentItem`.
  - `TASK-02.2`: Implementación de entidades de comparación `Comparison`, `ContentMatch`, `MatchEvidence`, `ScoreBreakdown`.
  - `TASK-02.3`: Implementación de entidades de revisión humana inmutable `Review` y `DatasetExample`.
  - `TASK-02.4`: Definición de puertos abstractos `ISyllabusExtractor`, `ISegmentationService`, `INlpVectorService`, repositorios y generador de reportes.
- **Decisiones técnicas adoptadas:**
  - Se seleccionó Python 3.12 sobre 3.14 debido a la compatibilidad comprobada de binarios para PyTorch y Sentence Transformers en Windows.
  - Se configuró `.venv/pip.ini` con `trusted-host` para garantizar estabilidad de descargas en redes corporativas con inspección SSL.
  - El diseño frontend respeta rigurosamente la paleta académica oscura descrita en el capítulo 59 (`#0B0F14`, `#121820`, `#1A222D`, `#F1F5F9`).
- **Bloqueadores / Riesgos identificados:**
  - Ninguno. Todas las dependencias compilaron e instalaron satisfactoriamente y las pruebas unitarias pasaron 100%.
- **Próximas tareas para la Sesión 03:**
  - Paquete 3: Ingesta y Extracción PDF (`TASK-03.1` a `TASK-03.4`).
  - Paquete 4: Estructuración y Segmentación de Contenidos (`TASK-04.1` a `TASK-04.4`).

### Sesión 03 — 2026-09-24
- **Objetivos de la sesión:**
  - Implementar adaptador de extracción de PDF con PyMuPDF preservando la trazabilidad de páginas físicas.
  - Implementar detector defensivo de PDFs escaneados o sin texto digital con excepción específica `InsufficientDigitalTextError`.
  - Implementar normalizador de texto controlado con preservación de vocabulario y signos técnicos (`c++` -> `cpp`, `b+` -> `bplus`, `3fn`).
  - Implementar detector de secciones canónicas y segmentador temático en `ContentItem` atómicos.
  - Implementar caso de uso `ProcessSyllabusUseCase`.
  - Desarrollar suite de pruebas unitarias y fixtures con PyMuPDF.
- **Tareas completadas:**
  - `TASK-03.1`: Validación de documentos (existencia, tamaño, vacuidad y hash SHA-256).
  - `TASK-03.2`: Extracción estructurada por página con `PyMuPdfExtractor`.
  - `TASK-03.3`: Detección y rechazo de PDFs escaneados informando sobre OCR para Fase 2.
  - `TASK-03.4`: Pruebas unitarias de extracción en `tests/unit/test_pdf_extractor.py`.
  - `TASK-04.1`: Detector heurístico de secciones académicas (`SyllabusSegmenter`).
  - `TASK-04.2`: Segmentación de unidades y semanas en `ContentItem` con herencia contextual de la unidad.
  - `TASK-04.3`: Normalizador lingüístico `TextNormalizer` en `backend/app/infrastructure/nlp/normalizer.py`.
  - `TASK-04.4`: Pruebas de segmentación y caso de uso en `tests/unit/test_segmenter.py`.
- **Decisiones técnicas adoptadas:**
  - Los términos técnicos con signos (`c++`, `b+`, `.net`) se mapean unívocamente a tokens seguros (`cpp`, `bplus`, `dotnet`) para que el tokenizador de TF-IDF no elimine los símbolos.
  - Los `ContentItem` de una unidad heredan el subtítulo temático de la unidad para garantizar contexto semántico suficiente en la comparación cruzada.
- **Bloqueadores / Riesgos identificados:**
  - Ninguno. 13 de 13 pruebas unitarias pasando satisfactoriamente.
- **Próximas tareas para la Sesión 04:**
  - Paquete 5: Motor de Similitud y NLP (`TASK-05.1` a `TASK-05.5`).
  - Paquete 6: Algoritmo de Comparación, Scoring y Clasificación (`TASK-06.1` a `TASK-06.4`).

### Sesión 04 — 2026-09-24
- **Objetivos de la sesión:**
  - Implementar el motor híbrido de cálculo de similitud (Léxico TF-IDF, Semántico con Sentence Transformers, Overlap de n-gramas y Estructural contextual).
  - Implementar el caso de uso `CompareSyllabiUseCase` con fórmula de score compuesto parametrizable.
  - Implementar clasificación categórica con umbrales (`MATCH`, `PARTIAL_MATCH`, `UNCERTAIN`, `NO_MATCH`).
  - Implementar análisis bidireccional y detección de contenidos huérfanos/sin correspondencia en ambos sílabos.
  - Desarrollar suite de pruebas unitarias completas con 18 casos de prueba.
- **Tareas completadas:**
  - `TASK-05.1`: Módulo de similitud léxica TF-IDF con n-gramas unigrama y bigrama.
  - `TASK-05.2`: Módulo de similitud semántica densa con Sentence Transformers y fallback determinista offline.
  - `TASK-05.3`: Extractor de evidencia léxica de palabras y bigramas técnicos compartidos.
  - `TASK-05.4`: Algoritmo de similitud estructural por número de unidad y orden relativo curricular.
  - `TASK-05.5`: Pruebas unitarias de vectorización en `tests/unit/test_nlp_vector_service.py`.
  - `TASK-06.1`: Scoring compuesto ponderado ($w_{sem}, w_{lex}, w_{key}, w_{est}$) y ScoreBreakdown.
  - `TASK-06.2`: Clasificación categórica por umbrales configurables.
  - `TASK-06.3`: Mapeo cardinal flexible que permite relaciones 1:1 y 1:N.
  - `TASK-06.4`: Cálculo de coberturas bidireccionales y porcentaje global en `tests/unit/test_compare_syllabi_use_case.py`.
- **Decisiones técnicas adoptadas:**
  - La representación semántica de cada ítem de contenido fusiona el título y el texto descriptivo (`f"{item.title}. {item.text}"`) para capturar la máxima señal temática durante la comparación.
  - Se implementó un algoritmo de respaldo semántico determinista en `NlpVectorService` para permitir operatividad en entornos cerrados o sin conexión.
- **Bloqueadores / Riesgos identificados:**
  - Ninguno. 18 de 18 pruebas unitarias pasando satisfactoriamente.
- **Próximas tareas para la Sesión 05:**
  - Paquete 7: Persistencia y Base de Datos SQLite (`TASK-07.1` a `TASK-07.3`).
  - Paquete 8: API REST con FastAPI (`TASK-08.1` a `TASK-08.5`).

### Sesión 05 — 2026-09-24
- **Objetivos de la sesión:**
  - Configurar infraestructura de persistencia SQLite relacional local (`convcomp.db`).
  - Implementar repositorios de dominio `SqliteSyllabusRepository`, `SqliteComparisonRepository` y `SqliteReviewRepository`.
  - Implementar persistencia inmutable de revisiones humanas que preservan intacta la predicción original de la IA.
  - Diseñar e implementar la API REST con FastAPI (Routers de Sílabos, Comparaciones, Revisiones y Dataset).
  - Implementar suite de pruebas de integración de base de datos y endpoints API.
- **Tareas completadas:**
  - `TASK-07.1`: Esquema relacional completo de SQLite en `backend/app/infrastructure/persistence/database.py`.
  - `TASK-07.2`: Implementación de repositorios de persistencia con soporte transaccional y consultas de contenido.
  - `TASK-07.3`: Persistencia inmutable de juicios humanos y staging de observaciones para dataset supervisado (`dataset_examples`).
  - `TASK-08.1`: Endpoint de carga de sílabos con validación y extracción (`POST /api/syllabi/upload`).
  - `TASK-08.2`: Endpoint para iniciar comparaciones (`POST /api/comparisons`).
  - `TASK-08.3`: Endpoints de consulta de resultados, correspondencias y contenidos huérfanos (`GET /api/comparisons/{id}`).
  - `TASK-08.4`: Endpoints de registro y consulta de revisiones humanas (`POST /api/reviews`).
  - `TASK-08.5`: Endpoint de métricas de dataset científico (`GET /api/dataset/statistics`).
- **Decisiones técnicas adoptadas:**
  - Las revisiones humanas (`Review`) se guardan en tabla separada con clave foránea a la comparación, garantizando que `content_matches` nunca muta su predicción original.
  - Se configuró middleware CORS permisivo en FastAPI para facilitar el desarrollo local desacoplado con el frontend de Vite.
- **Bloqueadores / Riesgos identificados:**
  - Ninguno. 24 de 24 pruebas unitarias y de integración pasando con 100% de éxito.
- **Próximas tareas para la Sesión 06:**
  - Paquete 9: Generador de Informes Formales (HTML y PDF con ReportLab) (`TASK-09.1` a `TASK-09.4`).
  - Paquete 10: Frontend: Dashboard y Carga de Sílabos (`TASK-10.1` a `TASK-10.4`).

### Sesión 06 — 2026-09-24
- **Objetivos de la sesión:**
  - Finalizar e integrar la descarga de informes formales (HTML `@media print` y PDF con `ReportLab`) en los endpoints de FastAPI (`TASK-09.1` a `TASK-09.4`).
  - Implementar la interfaz web completa en React + TypeScript + Vite:
    - Componente de cabecera con aviso institucional obligatorio (`Header.tsx`).
    - Carga de sílabos con Drag & Drop, selección de rol (Objetivo / Comparado) y validación de texto digital (`SyllabusUploader.tsx`).
    - Métricas globales y coberturas bidireccionales $S_{obj} \rightarrow S_{cmp}$ y $S_{cmp} \rightarrow S_{obj}$ (`ComparisonScore.tsx`).
    - Tabla interactiva de correspondencias con filtrado por categoría y búsqueda (`MatchTable.tsx`).
    - Inspección side-by-side de fragmentos textuales, páginas físicas de origen y factores NLP (`EvidencePanel.tsx`).
    - Análisis de brechas y temas huérfanos (`UnmatchedPanel.tsx`).
    - Modal de supervisión humana inmutable y trazable (`ReviewModal.tsx`).
    - Vista de métricas y exportador de dataset JSON para calibración (`AuditDatasetView.tsx`).
    - Panel de historial de comparaciones y sílabos registrados (`Dashboard.tsx`).
  - Integrar vistas en `App.tsx` y compilar bundle frontend con `npm run build` (0 errores).
  - Desarrollar prueba de integración End-to-End (`test_e2e_flow.py`) cubriendo el ciclo completo del sistema.
  - Documentar guía de ejecución local en `README.md` y script de ejecución `backend/run.py`.
- **Tareas completadas:**
  - Paquete 9 completado al 100% (`TASK-09.1` a `TASK-09.4`).
  - Paquete 10 completado al 100% (`TASK-10.1` a `TASK-10.4`).
  - Paquete 11 completado al 100% (`TASK-11.1` a `TASK-11.4`).
  - Paquete 12 completado al 100% (`TASK-12.1` a `TASK-12.4`).
  - Paquete 13 completado al 100% (`TASK-13.1` a `TASK-13.4`).
- **Decisiones técnicas adoptadas:**
  - Las coberturas se calculan y presentan como porcentajes directos (0-100%) manteniendo el score global en escala normalizada (0.0-1.0).
  - La descarga de informes en el navegador abre una ventana formal de PDF o una versión imprimible con `@media print` que conserva encabezados institucionales y la exención de responsabilidad.
  - La compilación del frontend con `tsc -b && vite build` valida cero errores de tipos en TypeScript.
- **Resultados de Validación:**
  - 28 de 28 pruebas automatizadas pasadas exitosamente con `pytest` en `tests/`.
  - Construcción del frontend terminada con éxito en 168ms sin errores de tipado.
  - Cumplimiento 100% de los criterios de aceptación formales de la Fase 1.

---

### Sesión 07 — 2026-09-24
- **Objetivos de la sesión:**
  - Corregir y clarificar la redacción e interpretación académica de los indicadores bidireccionales en el panel de resultados de comparación (`ComparisonScore.tsx`).
  - Crear e integrar un componente modal interactivo de soporte institucional y glosario metodológico (`SupportGuideModal.tsx`) accesible desde la barra superior (`Header.tsx`) y junto a las métricas.
  - Implementar la traducción y localización formal de todos los *Value Objects* del sistema al español (`utils/translations.ts`), sincronizando etiquetas, insignias y descripciones con el vocabulario pedagógico universitario.
  - Asegurar la legibilidad y contraste visual de todos los campos de entrada y menús desplegables (`<input>`, `<select>`, `<option>`) con texto negro sobre fondo blanco.
  - Verificar la integridad del build de producción del frontend (`npm run build`) y el paso de la suite de pruebas.
- **Tareas completadas:**
  - `TASK-UI-01`: Reestructuración semántica de los indicadores en `ComparisonScore.tsx`:
    - **Exigencia Cubierta (Curso Destino)**: Explica claramente qué porcentaje del curso obligatorio acredita el estudiante.
    - **Aprovechamiento del Curso de Origen**: Explica qué porcentaje de lo cursado previamente le es convalidado vs. contenidos adicionales descartados.
    - **Afinidad Global de Contenidos**: Promedio ponderado de correspondencia temática.
  - `TASK-UI-02`: Creación del módulo central de traducción `frontend/src/utils/translations.ts` con mapeo pedagógico de clasificaciones (`MATCH`, `PARTIAL_MATCH`, `UNCERTAIN`, `NO_MATCH`), decisiones humanas (`CONFIRMED`, `FALSE_POSITIVE`, etc.) y tipos de evidencia (`LEXICAL`, `SEMANTIC`, `HYBRID`).
  - `TASK-UI-03`: Implementación de `SupportGuideModal.tsx` con 5 pestañas didácticas:
    1. Guía de Indicadores de Cobertura y Afinidad.
    2. Glosario de Clasificaciones Algorítmicas en Español.
    3. Guía de Auditoría Humana y Tipos de Corrección.
    4. Desglose de Factores NLP Híbridos (Semántico 40%, Léxico 30%, Claves 15%, Estructural 15%).
    5. Marco Ético e Institucional (aviso de herramienta de apoyo, no vinculante).
  - `TASK-UI-04`: Integración del modal de soporte en `Header.tsx` (botón visible `📖 Guía & Soporte`) y en `ComparisonScore.tsx` (botón `❓ Guía de Indicadores`), administrado con estado global en `App.tsx`.
  - `TASK-UI-05`: Localización al español de `AuditDatasetView.tsx`, `MatchTable.tsx`, `EvidencePanel.tsx` y `ReviewModal.tsx`.
  - `TASK-UI-06`: Corrección de contraste y tipografía (letras negras `#000000` sobre fondo `#FFFFFF` en inputs y selects de carga y modal de revisión).
- **Decisiones técnicas adoptadas:**
  - Se mantuvo la inmutabilidad de los identificadores en inglés a nivel de API/Base de datos (`MATCH`, `OVERESTIMATION`, etc.) para preservar la compatibilidad con el esquema de dominio y estándares de código limpio, mientras que la capa de presentación delega 100% en `translations.ts`.
- **Resultados de Validación:**
  - Compilación exitosa del frontend con `tsc -b && vite build` (0 errores).
  - Verificación del backend y suite completa de pruebas unitarias/integración.

---

### Sesión 08 — 2026-09-24
- **Objetivos de la sesión:**
  - Rediseñar la paleta cromática completa del frontend: sustituir todos los tonos azules y cianes por una escala formal de grises, grafito, pizarra y acentos plateados (`index.css`).
  - Reestructurar la interfaz con un diseño y disposición correspondiente a informes técnicos y expedientes universitarios de producción.
  - Eliminar de raíz paréntesis que no aporten información relevante (`(Curso Destino)`, `(Curso Origen)`, `(Fase 1)`, `(TF-IDF)`, etc.).
  - Retirar metadatos y etiquetas orientadas a desarrolladores (`Fase 1 · NLP Híbrido`, `dataset_examples`, `calibración offline`, nombres de modelos en bruto, etc.) para proyectar un acabado de producción formal.
- **Tareas completadas:**
  - `TASK-PROD-01`: Reconfiguración cromática formal en `frontend/src/index.css`:
    - Variables de fondo en grafito profundo (`#111215`, `#18191f`, `#22242c`).
    - Bordes en pizarra y gris neutro (`#32353e`, `#4b5563`, `#525866`).
    - Botones principales en gris formal de producción (`#374151` con hover `#4b5563`).
    - Supresión de gradientes azules y sombras luminosas.
  - `TASK-PROD-02`: Rediseño de `Header.tsx`:
    - Emblema institucional sobrio en grafito (`CC`).
    - Supresión de la insignia `Fase 1 · NLP Híbrido`, reemplazada por `Dictamen Técnico`.
    - Pestañas con nomenclatura de expediente: *Nueva Evaluación*, *Registro de Sílabos*, *Informe Técnico*, *Registro de Auditoría*, *Guía Metodológica*.
  - `TASK-PROD-03`: Rediseño de `ComparisonScore.tsx` con estructura de informe técnico formal:
    - Encabezado con código de expediente (`EXP-XXXX`), fecha de emisión formal y estado.
    - Cuadro comparativo de asignaturas: *Asignatura Requerida · Plan Destino* y *Asignatura Cursada · Institución de Origen*.
    - Reemplazo de indicadores a terminología depurada sin paréntesis: *Exigencia Curricular Acreditada* y *Aprovechamiento Curricular de Origen*.
    - Ocultamiento del modelo técnico de Sentence-Transformers y visualización sobria de porcentajes.
  - `TASK-PROD-04`: Rediseño de `MatchTable.tsx`:
    - Encabezado formal: *Matriz Analítica de Correspondencias Curriculares*.
    - Columnas depuradas: *Contenido Requerido*, *Contenido de Origen*, *Equivalencia*, *Afinidad*, *Términos Coincidentes*, *Auditoría*, *Acción*.
    - Filtros categoriales en formato tabular limpio sin paréntesis innecesarios.
  - `TASK-PROD-05`: Rediseño de `EvidencePanel.tsx`:
    - Ficha técnica de cotejo lado a lado con delimitadores neutros en gris pizarra.
    - Criterios explicados formalmente: *Similitud Conceptual y Semántica*, *Concordancia Textual y Léxica*, *Vocabulario Especializado*, *Correspondencia Estructural*.
  - `TASK-PROD-06`: Limpieza de `UnmatchedPanel.tsx`:
    - Titulación formal: *Análisis de Brechas Curriculares y Contenidos Sin Equivalencia*.
    - Supresión de emojis informales (⚠️, ℹ️) y eliminación de paréntesis.
  - `TASK-PROD-07`: Actualización de `ReviewModal.tsx` y `AuditDatasetView.tsx`:
    - Campos de entrada de máxima claridad y contraste (letras negras `#000000` sobre `#FFFFFF`).
    - Supresión de menciones internas a la tabla `dataset_examples`, `fine-tuning` o códigos de máquina entre paréntesis.
    - Registro de dictamen presentado como *Principio de Inmutabilidad y Trazabilidad Institucional*.
  - `TASK-PROD-08`: Actualización de `SupportGuideModal.tsx` y `translations.ts`:
    - Guía metodológica institucional en formato de reporte técnico, suprimiendo jerga de desarrollo y emojis.
- **Resultados de Validación:**
  - `npm run build` ejecutado exitosamente con 0 errores de compilación (`built in 168ms`).
  - Búsqueda global confirma 0 ocurrencias de códigos azules o términos de desarrollo en el frontend.

---

### Sesión 09 — 2026-09-24
- **Objetivos de la sesión:**
  - Suprimir rigurosamente todos los bordes redondeados (`border-radius`) en la totalidad de la interfaz de usuario: tarjetas, cuadros de entrada, botones, desplegables, tablas, insignias, barras de progreso y modales.
  - Asegurar una estética sobria, limpia y de expediente técnico con esquinas rectas y aristas ortogonales de 90 grados (`0px`).
  - Establecer una regla de anulación global en el sistema de estilos (`index.css`) y sanitizar todas las declaraciones en línea en los componentes React.
- **Tareas completadas:**
  - `TASK-UI-SHARP-01`: Reconfiguración global de variables CSS de radio en `frontend/src/index.css`:
    - `--radius-sm: 0px;`
    - `--radius-md: 0px;`
    - `--radius-lg: 0px;`
    - Regla universal con máxima especificidad: `*, *::before, *::after { border-radius: 0 !important; }` garantizando que ningún elemento del DOM presente bordes redondeados.
  - `TASK-UI-SHARP-02`: Sanitización exhaustiva de propiedades `borderRadius` en línea (`4px`, `6px`, `8px`, `12px`, `2px`) a `0px` en todos los componentes:
    - [Header.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/Header.tsx): emblemas, botones de navegación, badges.
    - [ComparisonScore.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/ComparisonScore.tsx): tarjetas de expediente, cuadros de asignaturas, contenedores de métricas.
    - [SyllabusUploader.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/SyllabusUploader.tsx): cajas de selección de rol, zonas de carga de archivos, inputs de texto, selects y alertas.
    - [MatchTable.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/MatchTable.tsx): buscador, botones de filtro categorial, etiquetas de términos clave coincidentes.
    - [EvidencePanel.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/EvidencePanel.tsx): cajas de texto comparadas, barras de porcentaje, tarjetas de detalle.
    - [UnmatchedPanel.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/UnmatchedPanel.tsx): paneles de brechas curriculares, tarjetas de temas huérfanos.
    - [ReviewModal.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/ReviewModal.tsx): modal de dictamen, inputs, selectores y botones de confirmación.
    - [SupportGuideModal.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/SupportGuideModal.tsx): ventana de guía metodológica, pestañas y cajas informativas.
    - [Dashboard.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/Dashboard.tsx) y [AuditDatasetView.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/AuditDatasetView.tsx): tablas de historial y registros de auditoría.
- **Resultados de Validación:**
  - `npm run build` ejecutado exitosamente con 0 errores (`built in 85ms`).
  - Inspección con `grep_search` confirma 0 ocurrencias de radios mayores a `0px` en todo el código fuente del frontend.

---

### Sesión 10 — 2026-09-24
- **Objetivos de la sesión:**
  - Rediseñar integralmente la Guía Metodológica institucional ([SupportGuideModal.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/SupportGuideModal.tsx)) para erradicar la sobrecarga visual y facilitar la lectura continua.
  - Implementar una estructura de diseño vertical ergonómica, eliminando las cuadrículas horizontales comprimidas y sustituyéndolas por un flujo secuencial a ancho completo.
  - Elevar la calidad tipográfica y el contraste visual: jerarquía tipográfica definida, incremento del tamaño de fuente base a 13.5px/14px, interlineado amplio (1.65), textos en blanco de alta legibilidad (`#FFFFFF` y `#E2E8F0`) y cajas resaltadas con directrices de decisión académica.
  - Incorporar una barra de navegación lateral vertical fija con índice de secciones (1 a 5) y desplazamiento suave directo (`scrollIntoView`).
- **Tareas completadas:**
  - `TASK-GUIDE-VERT-01`: Arquitectura de visualización en dos paneles:
    - Índice vertical izquierdo con selector de secciones numeradas y estado activo.
    - Panel de lectura vertical derecho con ancho de lectura confortable para evitar fatiga ocular.
  - `TASK-GUIDE-VERT-02`: Maquetación vertical de contenidos pedagógicos:
    - **Parte 1 (Indicadores Principales)**: Tarjetas verticales con definición conceptual, fórmula y recuadro de «Regla de Decisión Académica».
    - **Parte 2 (Niveles de Correspondencia)**: Bloques verticales por nivel (`Equivalente Total`, `Equivalente Parcial`, `Incierto`, `Sin Equivalencia`) con rangos de afinidad y acción sugerida para la comisión.
    - **Parte 3 (Dictamen y Calificación)**: Opciones de calificación docente con garantía de trazabilidad e inmutabilidad.
    - **Parte 4 (Ponderación Multivariada)**: Explicación vertical de los 4 factores (Semántica 40%, Léxica 30%, Claves 15%, Estructural 15%).
    - **Parte 5 (Marco Institucional)**: Principio de apoyo analítico no vinculante y soberanía docente.
  - `TASK-GUIDE-VERT-03`: Preservación estricta de esquinas rectas (`borderRadius: 0px`) en todos los botones, selectores y contenedores.
- **Resultados de Validación:**
  - Compilación exitosa del frontend con `tsc -b && vite build` (0 errores, `built in 94ms`).
  - Hot Module Replacement (HMR) activo en el servidor de desarrollo Vite.

---

### Sesión 11 — 2026-09-24
- **Objetivos de la sesión:**
  - Erradicar la presencia de textos en tonos grises oscuros o apagados sobre fondos oscuros que generaban fatiga visual y bajo contraste (`#6b7280`, `#9ca3af`).
  - Elevar sustancialmente la legibilidad de toda la plataforma a estándares de alto contraste y confort visual (relación de contraste superior a 10:1 conforme a criterios WCAG AAA).
  - Redefinir las variables globales de tipografía en [index.css](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/index.css) y sustituir colores hardcodeados en componentes React.
  - Verificar en navegador con subagente automatizado la claridad visual, encabezados, tablas y el contenido de la Guía Metodológica.
- **Tareas completadas:**
  - `TASK-CONTRAST-01`: Reconfiguración de variables de color de texto en `frontend/src/index.css`:
    - `--text-main: #FFFFFF;` (blanco puro de máxima nitidez).
    - `--text-primary: #FFFFFF;` (títulos, encabezados y valores clave).
    - `--text-secondary: #E2E8F0;` (Slate 200: lectura continua nítida y descansada, sustituyendo el gris apagado `#9ca3af`).
    - `--text-muted: #CBD5E1;` (Slate 300: subtítulos, notas al pie y cabeceras de tabla plenamente legibles, sustituyendo el gris oscuro `#6b7280`).
  - `TASK-CONTRAST-02`: Actualización de estilos específicos en componentes:
    - [MatchTable.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/MatchTable.tsx): sustitución de números de página y encabezados de tabla a `var(--text-secondary)`.
    - [EvidencePanel.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/EvidencePanel.tsx): barra de progreso semántico en gris platino claro `#cbd5e1`.
    - [SupportGuideModal.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/SupportGuideModal.tsx): acentos de navegación y bordes de llamada a `#FFFFFF` y `#CBD5E1`.
  - `TASK-CONTRAST-03`: Inspección visual automatizada en navegador con subagente (`http://localhost:5173`):
    - Comprobación de cabecera, dropzone de carga de sílabos y campos de formulario con letras negras sobre fondo blanco.
    - Apertura, navegación y verificación del modal de Guía Metodológica confirmando eliminación total de gris sobre gris.
- **Resultados de Validación:**
  - Compilación exitosa del frontend con `tsc -b && vite build` (0 errores, `built in 92ms`).
  - Grabación y capturas de pantalla de verificación archivadas en los artefactos del sistema.

---

### Sesión 12 — 2026-09-24
- **Objetivos de la sesión:**
  - Analizar a profundidad los requerimientos de la **Fase 1.5 — Visualización y Trazabilidad de Evidencias en los PDF** (Capítulo 97 a 99 del planteamiento institucional).
  - Diseñar y formalizar la arquitectura técnica y el documento de flujo para la Fase 1.5 ([docs/FLUJO_FASE_1_5.md](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/docs/FLUJO_FASE_1_5.md)).
  - Crear la nueva rama de trabajo en Git: `feature/fase1_5`.
  - Estructurar el desglose granular de tareas en 5 paquetes de trabajo (Paquetes 14 a 18) en `docs/TASKS.md`.
  - Definir la estrategia de extracción espacial de coordenadas (`x0, y0, x1, y1`) con PyMuPDF sin alterar los PDFs originales, la API de servido de PDFs y el diseño del Visor Doble interactivo con `EvidenceOverlay`.
- **Tareas completadas:**
  - Análisis exhaustivo de los 25 apartados de la Fase 1.5 en [PLANTEAMIENTO_IMPLEMENTACION_COMPARACION_SILABOS.md](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/docs/PLANTEAMIENTO_IMPLEMENTACION_COMPARACION_SILABOS.md).
  - Elaboración y formalización de [docs/FLUJO_FASE_1_5.md](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/docs/FLUJO_FASE_1_5.md).
  - Incorporación de los paquetes de trabajo 14 al 18 en `docs/TASKS.md` elevando el alcance global del proyecto a 66 tareas controladas.
- **Decisiones técnicas adoptadas:**
  - Principio de No Destructividad: El PDF original nunca es intervenido en el servidor; los cuadros delimitadores se dibujan en una capa vectorial/HTML superpuesta en el cliente (`EvidenceOverlay`).
  - Extracción con PyMuPDF (`fitz`): se conservarán las dimensiones de página (`page_width`, `page_height`) y las coordenadas exactas de bloques y palabras clave (`search_for`).
  - El Visor Doble (`DualPdfViewer`) incorporará navegación sincronizada automática, zoom no deformable y panel de dictamen humano directo para casos confirmados y dudosos (`? REVISAR`).
- **Próximas tareas a iniciar:**
  - Paquete 14: Extracción Espacial y Bounding Boxes (`TASK-14.1` a `TASK-14.4`).
  - Paquete 15: API de PDF y Consulta de Evidencias (`TASK-15.1` a `TASK-15.3`).

---

### Sesión 13 — 2026-09-24
- **Objetivos de la sesión:**
  - Implementar de extremo a extremo la **Fase 1.5: Visualización y Trazabilidad de Evidencias en los PDF** (Paquetes 14, 15, 16 y 17).
  - Conservar estrictamente el algoritmo matemático, ponderaciones y scoring de la Fase 1.0.
  - Implementar el servicio `SpatialLocatorService` en PyMuPDF para extraer dimensiones de página y recuadros delimitadores (`x0, y0, x1, y1`) basados en títulos, fragmentos textuales y palabras clave coincidentes.
  - Actualizar persistencia en SQLite (`content_matches.evidence_regions_json`) y orquestador `CompareSyllabiUseCase`.
  - Crear endpoints REST:
    - `GET /api/syllabi/{id}/pdf` para streaming no destructivo del PDF original.
    - `GET /api/comparisons/{id}/evidence` para consulta estructurada de coordenadas.
    - `GET /api/comparisons/{id}/matches/{match_id}/evidence` para detalle espacial por correspondencia.
  - Configurar `pdfjs-dist` en el frontend y construir los componentes:
    - `EvidenceOverlay.tsx` (capa SVG/HTML de alta precisión con esquinas a 90° sin bordes redondeados).
    - `PdfDocumentViewer.tsx` (visor individual con zoom al ancho, a la página, 100%, 150% y navegación de páginas).
    - `EvidenceNavigator.tsx` (barra de avance secuencial con atajos de teclado `←` / `→` e indicadores de score).
    - `ViewerReviewPanel.tsx` (panel de dictamen rápido para ratificar match, ajustar a parcial, marcar dudoso `? REVISAR` o descartar).
    - `DualPdfViewer.tsx` (visor doble pericial interactivo a pantalla completa).
  - Integrar el botón "Visor PDF" en `MatchTable.tsx` y `EvidencePanel.tsx`.
- **Tareas completadas:**
  - Paquete 14 completado al 100% (`TASK-14.1` a `TASK-14.4`).
  - Paquete 15 completado al 100% (`TASK-15.1` a `TASK-15.3`).
  - Paquete 16 completado al 100% (`TASK-16.1` a `TASK-16.4`).
  - Paquete 17 completado al 100% (`TASK-17.1` a `TASK-17.4`).
- **Resultados de Validación:**
  - Suite completa de 32 pruebas automatizadas en backend (`pytest tests/`) ejecutadas con 100% de éxito.
  - Compilación de producción en frontend (`npm run build`) completada con 0 errores de tipado.
  - Verificación visual automatizada en navegador con subagente (`browser_subagent`) validando apertura de visor doble, renderizado de páginas simultáneas, cuadros delimitadores ortogonales y sincronización con flechas de avance.








