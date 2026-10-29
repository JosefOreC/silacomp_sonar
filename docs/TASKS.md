# Registro de Tareas y Avances de Implementación (TASKS)
## Sistema Inteligente para Comparación de Sílabos Universitarios — Fases 1.0 a 3.0

**Versión:** 3.5

**Última actualización:** 2026-10-29
**Documento de referencia:** [PLANTEAMIENTO_IMPLEMENTACION_COMPARACION_SILABOS.md](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/docs/PLANTEAMIENTO_IMPLEMENTACION_COMPARACION_SILABOS.md) | [FLUJO_FASE_1.md](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/docs/FLUJO_FASE_1.md)  
**Normas de actualización:** Ver [REGLAS_IMPLEMENTACION.md](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/docs/REGLAS_IMPLEMENTACION.md)

---

## Convenciones de Estado

- `[ ]` **Pendiente:** Tarea planificada aún no iniciada.
- `[/]` **En Progreso:** Tarea actualmente en desarrollo en la sesión activa.
- `[x]` **Completado:** Tarea implementada, probada y validada según criterios de aceptación.
- `[-]` **Descartado / Pospuesto:** Tarea aplazada justificadamente a una fase posterior.

---

## Resumen Ejecutivo de Avance

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
| 18. Fase 1.5: Evidencias en Reportes y Pruebas E2E | Completado | 100% | 2 | 2 |
| **SUBTOTAL FASE 1.5** | **Completado** | **100%** | **17** | **17** |
| 19. Fase 2.0: Ingesta con OCR para Documentos Escaneados | Completado | 100% | 4 | 4 |
| 20. Fase 2.0: Dataset Científico y Feature Engineering | Completado | 100% | 2 | 2 |
| 21. Fase 2.0: Modelado Supervisado y Calibración | Completado | 100% | 3 | 3 |
| 22. Fase 2.0: Versionado y Ciclo de Vida de Modelos (API) | Completado | 100% | 3 | 3 |
| 23. Fase 2.0: Frontend — Gestión de Modelos y Auditoría | Completado | 100% | 4 | 4 |
| 24. Fase 2.0: Pruebas Automatizadas y Validación E2E | Completado | 100% | 3 | 3 |
| **TOTAL GENERAL (FASE 1.0 + 1.5 + 2.0)** | **Completado** | **100%** | **85** | **85** |
| 25. Fase 2.1: Consolidación y validación científica | Completado | 100% | 8 | 8 |
| **TOTAL CON FASE 2.1** | **Completado** | **100%** | **93** | **93** |
| 26. Fase 3: Ground truth y evaluación interevaluador | Completado | 100% | 7 | 7 |
| 27. Fase 3: Selección de casos para aprendizaje activo | Completado | 100% | 3 | 3 |
| 28. Fase 3: Experimentos y mejora controlada | Completado | 100% | 2 | 2 |
| **SUBTOTAL FASE 3 PLANIFICADA** | **Completado** | **100%** | **12** | **12** |
| **TOTAL CON FASE 3 PLANIFICADA** | **Completado** | **100%** | **105** | **105** |
| 29. Fase 3.2: Validación integrada en navegador | Completado | 100% | 2 | 2 |
| **TOTAL CON VALIDACIÓN INTEGRADA** | **Completado** | **100%** | **107** | **107** |
| 30. Docker y análisis SonarQube | Completado | 100% | 4 | 4 |
| **TOTAL CON DESPLIEGUE Y CALIDAD** | **Completado** | **100%** | **111** | **111** |
| 31. Cumplimiento del manual de evaluación de calidad | Completado localmente | 100% | 4 | 4 |
| **TOTAL CON EVALUACIÓN ACADÉMICA LOCAL** | **Completado** | **100%** | **115** | **115** |
| 32. Integración y protección de calidad continua | Completado localmente | 100% | 8 | 8 |
| **TOTAL CON SESIÓN 29** | **Completado localmente** | **100%** | **123** | **123** |
| 33. Rediseño web SaaS de ConvComp | Completado localmente | 100% | 4 | 4 |
| **TOTAL CON REDISEÑO WEB** | **Completado localmente** | **100%** | **127** | **127** |
| 34. Comparaciones por lotes y ranking de candidatos | Completado localmente | 100% | 5 | 5 |
| **TOTAL CON COMPARACIÓN POR LOTES** | **Completado localmente** | **100%** | **132** | **132** |

---

### Paquete 31: Cumplimiento del manual de evaluación de calidad

- [x] **TASK-31.1:** Auditar rúbrica, preparar pipeline oficial y metadatos académicos, eliminar exclusiones incompatibles y permitir versionar cobertura real. *(Validado localmente el 2026-10-17)*
- [x] **TASK-31.2:** Corregir hallazgos de fiabilidad y mantenibilidad preservando contratos de API y reglas del dominio. *(0 incidencias abiertas, 2026-10-17)*
- [x] **TASK-31.3:** Generar cobertura backend/frontend con pruebas de comportamiento y verificar cobertura global mínima de 80%. *(82,4% global; 113 pruebas Python, 100 Vitest y 4 Playwright aprobadas)*
- [x] **TASK-31.4:** Repetir análisis real con condiciones efectivas, documentar puntuación por criterio y pendientes de entrega oficial. *(Gate PASSED; rúbrica local 20/20, pendiente pipeline institucional)*

### Paquete 32: Integración y protección de calidad continua

Plan: [PLAN_SESION_29.md](PLAN_SESION_29.md). Objetivos confirmados: continuar
implementación y sostener la máxima puntuación de SonarQube.

- [x] **TASK-32.1:** Auditar documentos y evidencia histórica; registrar alcance y criterios de la sesión. *(2026-10-28)*
- [x] **TASK-32.2:** Endurecer verificación de condiciones efectivas, umbrales y cero incidencias abiertas, con regresiones automatizadas. *(34 pruebas de rúbrica/verificador aprobadas, 2026-10-28)*
- [x] **TASK-32.3:** Añadir pruebas del visor doble: navegación de ambos PDF, cierre y revisión inmutable. *(6 pruebas aprobadas, 2026-10-28)*
- [x] **TASK-32.4:** Probar integración de la aplicación y corregir fallos reproducibles de navegación y revisión. *(La revisión del visor actualiza el dictamen humano en resultados; 4 pruebas de aplicación y 6 del ciclo de modelos aprobadas, 2026-10-28)*
- [x] **TASK-32.5:** Establecer protección de cobertura frontend y regenerar LCOV sin exclusiones de fuentes. *(116 pruebas aprobadas; 86,57% líneas, 73,65% ramas; mínimos 80/70, 2026-10-28)*
- [x] **TASK-32.6:** Ejecutar validaciones completas y repetir análisis SonarQube sobre el estado final. *(137 Python, 116 Vitest y 4 navegador aprobadas; gate PASSED, rúbrica local 20/20, cobertura global 85,0%, 2026-10-28)*
- [x] **TASK-32.7:** Actualizar evidencias, bitácora y preparación de entrega institucional, distinguiendo resultados locales y oficiales. *(Reportes regenerados; entrega GitLab/Quantum pendiente de destino y acceso, 2026-10-28)*
- [x] **TASK-32.8:** Restaurar los componentes de virtualización necesarios para Docker Desktop y verificar su funcionamiento antes de continuar la implementación. *(2026-10-28: tras la intervención y el reinicio, servidor Docker 29.7.2 operativo; PostgreSQL y SonarQube saludables.)*

### Paquete 33: Rediseño web SaaS de ConvComp

Referencia solicitada: [Dribbble — AI Search Analytics Platform](https://dribbble.com/shots/27822756-SaaS-Landing-Page-AI-Search-Analytics-Platform).
La referencia directa son las dos capturas SaaS y la paleta violeta adjuntas
por el usuario. Decisiones de diseño: [DISENO_WEB.md](DISENO_WEB.md).

- [x] **TASK-33.1:** Adaptar identidad visual, tipografía, navegación y estilos compartidos a la referencia proporcionada. *(Violeta, lavanda y paneles blancos, 2026-10-28)*
- [x] **TASK-33.2:** Rediseñar el inicio y la carga de ambos sílabos manteniendo los contratos y flujos existentes. *(Panel compartido; metadatos independientes y reintentos probados, 2026-10-28)*
- [x] **TASK-33.3:** Validar presentación adaptable y flujos en escritorio/móvil; corregir problemas observados. *(6 pruebas de navegador aprobadas en 42,7 s; capturas inspeccionadas; teclado/foco en la guía, 2026-10-28)*
- [x] **TASK-33.4:** Regenerar cobertura, repetir SonarQube y actualizar evidencias y bitácora del rediseño. *(120 Vitest y 6 navegador aprobadas; gate PASSED, A/A/A, 85,6% global, duplicación 0,8%, cero hallazgos y rúbrica local 20/20; Docker saludable, 2026-10-28)*

### Paquete 34: Comparaciones por lotes y ranking de candidatos

El usuario priorizó ampliar las funciones de comparación. Alcance: un sílabo
objetivo frente a hasta cinco candidatos, resultados individuales persistentes,
ranking explicable y recuperación del lote. Usuarios/autenticación y la
migración de base de datos quedan fuera de este incremento.

- [x] **TASK-34.1:** Definir dominio, contratos y límites del lote, sin agregación curricular ficticia ni cambios al algoritmo de pares. *(Dominio puro; 1–5 candidatos y 20 000 pares como máximo)*
- [x] **TASK-34.2:** Persistir solicitudes y resultados del lote con idempotencia y conservación de avances parciales. *(SQLite aditivo, UUID único y pruebas de interrupción/relectura)*
- [x] **TASK-34.3:** Implementar orquestación y API con modelo fijo por lote, ranking y errores por candidato. *(35 pruebas nuevas de dominio/API aprobadas; contratos REST existentes preservados)*
- [x] **TASK-34.4:** Integrar selección, resultados, historial y acceso a informes en la interfaz violeta. *(Selección y recuperación UI/Chrome verificadas; versión 3.3.0 publicada localmente)*
- [x] **TASK-34.5:** Verificar dominio/API/UI/navegador, regenerar cobertura, publicar localmente, repetir SonarQube y cerrar evidencias. *(172 Python, 134 Vitest y 8 Chrome aprobadas; gate PASSED, 20/20 local, 2026-10-29)*

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
- [x] **TASK-06.3:** Implementar soporte para relaciones cardinales múltiples controladas (1:1, 1:N, N:1) con eliminación de redundancia y asignación competitiva (supresión de candidatos repetidos, deduplicación de tópicos, priorización de ítems libres para evitar inanición/starvation, filtrado de preámbulo administrativo en unidades y atajo de correspondencia idéntica 100%). *(Completado el 2026-09-24)*
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
- [x] **TASK-18.1:** Extender el generador de reportes PDF formal para incorporar referencias de coordenadas y trazabilidad espacial de evidencias. *(Completado el 2026-09-24)*
- [x] **TASK-18.2:** Pruebas automatizadas de extremo a extremo cubriendo el flujo completo de la Fase 1.5: Carga $\rightarrow$ Comparación $\rightarrow$ Visor Doble $\rightarrow$ Coordenadas $\rightarrow$ Revisión. *(Completado el 2026-09-24)*

---

## Desglose Granular de Tareas — Fase 2.0: OCR y Aprendizaje Supervisado con Calibración

### Paquete 19: Ingesta con OCR para Documentos Escaneados
- [x] **TASK-19.1:** Definir puerto `IOCREngine` en `domain/ports.py` y modelos de bloques OCR con texto y cajas delimitadoras `(x0, y0, x1, y1)`. *(Completado el 2026-10-04)*
- [x] **TASK-19.2:** Implementar adaptador `RapidOcrEngine` (usando `rapidocr_onnxruntime` + renderizado PyMuPDF) con escalado a coordenadas tipográficas (72 DPI). *(Completado el 2026-10-04)*
- [x] **TASK-19.3:** Integrar fallback y detección de PDFs escaneados en `PyMuPdfExtractor` y `ProcessSyllabusUseCase` ejecutando OCR automático, inyectando capa indexable y marcando `ocr_applied=True`. *(Completado el 2026-10-04)*
- [x] **TASK-19.4:** Pruebas unitarias y de integración para ingesta OCR en PDFs escaneados sintetizados y validación de coordenadas para el visor (`test_ocr_engine.py`). *(Completado el 2026-10-04)*

---

### Paquete 20: Dataset Científico y Feature Engineering
- [x] **TASK-20.1:** Implementar servicio de preparación de dataset (`DatasetService`): extracción de vectores multivariados $X=[s_{sem}, s_{lex}, s_{asym}, s_{struct}, s_{key}]$, balanceo de clases y partición estratificada Train/Val/Test por universidad sin data leakage. *(Completado el 2026-10-04)*
- [x] **TASK-20.2:** Implementar endpoint para exportación formal del dataset científico acumulado (`GET /api/dataset/export?format=json|csv`). *(Completado el 2026-10-04)*

---

### Paquete 21: Modelado Supervisado y Calibración
- [x] **TASK-21.1:** Definir puerto `ISupervisedModelTrainer` y entidades de modelo entrenado en dominio. *(Completado el 2026-10-04)*
- [x] **TASK-21.2:** Implementar entrenador de modelos supervisados con `scikit-learn`: Regresión Logística regularizada con calibración de probabilidades (`CalibratedClassifierCV`) y clasificador Random Forest explicable. *(Completado el 2026-10-04)*
- [x] **TASK-21.3:** Implementar evaluador científico de modelos (`ModelEvaluationService`) calculando $F_1$, Precisión, Recall, AUC-ROC, matriz de confusión y benchmarking contra el baseline heurístico. *(Completado el 2026-10-04)*

---

### Paquete 22: Versionado y Ciclo de Vida de Modelos (API & Backend)
- [x] **TASK-22.1:** Configurar persistencia de versiones de modelos en SQLite (`model_versions`: hiperparámetros, pesos aprendidos, métricas de test y estado `ACTIVE`/`CANDIDATE`). *(Completado el 2026-10-04)*
- [x] **TASK-22.2:** Integrar inferencia supervisada en `CompareSyllabiUseCase` con fallback adaptativo y trazabilidad del modelo activo en cada comparación. *(Completado el 2026-10-04)*
- [x] **TASK-22.3:** Implementar endpoints REST para gestión de modelos (`GET /api/models`, `POST /api/models/train`, `POST /api/models/{id}/activate`, `GET /api/models/{id}/evaluation`). *(Completado el 2026-10-04)*

---

### Paquete 23: Frontend — Gestión de Modelos y Auditoría de Aprendizaje
- [x] **TASK-23.1:** Implementar vista de gestión y auditoría de modelos `ModelManagementView.tsx` en el frontend con lista de versiones y panel de detalle. *(Completado el 2026-10-05)*
- [x] **TASK-23.2:** Implementar visualización de métricas científicas ($F_1$, Precisión, Recall) y matriz de confusión interactiva comparativa contra el baseline. *(Completado el 2026-10-05)*
- [x] **TASK-23.3:** Implementar controles para disparo de re-entrenamiento controlado y promoción de modelos a producción (`Activar`). *(Completado el 2026-10-05)*
- [x] **TASK-23.4:** Integrar pestaña "Modelos IA" en navegación de `Header.tsx` con acceso desde la aplicación principal. *(Completado el 2026-10-05)*

---

### Paquete 24: Pruebas Automatizadas y Validación E2E de Fase 2.0
- [x] **TASK-24.1:** Pruebas unitarias de motor OCR y precisión de bounding boxes en PyMuPDF (`test_ocr_engine.py`). *(Completado el 2026-10-04)*
- [x] **TASK-24.2:** Pruebas unitarias de entrenamiento supervisado, cálculo de métricas y calibración probabilística (`test_supervised_model.py`). *(Completado el 2026-10-04)*
- [x] **TASK-24.3:** Pruebas de integración E2E del ciclo de vida de modelos: Entrenamiento $\rightarrow$ Evaluación $\rightarrow$ Activación $\rightarrow$ Exportación de Dataset (`test_model_lifecycle_endpoints.py`). *(Completado el 2026-10-04)*

---

---

## Fase 2.1: Consolidación antes de aprendizaje activo

### Paquete 25: Coherencia, reproducibilidad y evaluación sin filtración
- [x] **TASK-25.1:** Sincronizar versión, fase, README y contratos del endpoint de salud. *(Completado el 2026-10-15)*
- [x] **TASK-25.2:** Declarar dependencias OCR y directas de ML en ambos manifiestos del backend. *(Completado el 2026-10-15)*
- [x] **TASK-25.3:** Aislar base, cargas, reportes y modelos de las pruebas; comprobar que la base local no cambia. *(Completado el 2026-10-15)*
- [x] **TASK-25.4:** Recuperar procedencia académica e IDs reales de contenidos en el dataset, incluyendo registros históricos consultables. *(Completado el 2026-10-15)*
- [x] **TASK-25.5:** Separar entrenamiento y evaluación por grupos académicos, evitar que bootstrap sintético contamine evaluación real y añadir pruebas de regresión. *(Completado el 2026-10-15)*
- [x] **TASK-25.6:** Dividir la carga del visor PDF y la gestión de modelos; validar compilación y ejecutar la suite aislada. *(Completado el 2026-10-15)*
- [x] **TASK-25.7:** Alinear el benchmark con el scoring adaptativo vigente y retirar métricas estáticas del baseline en la API; distinguir evaluación por pares de comparación completa. *(Completado el 2026-10-15)*
- [x] **TASK-25.8:** Resolver advertencias existentes de lint en efectos y dependencias de componentes React, corregir los contratos tipados de las vistas afectadas y usar los recuentos reales del dataset en Auditoría. *(Completado el 2026-10-15)*

## Fase 3: Ground truth, aprendizaje activo y evaluación avanzada

### Paquete 26: Ground truth y evaluación interevaluador
- [x] **TASK-26.1:** Preservar revisiones como eventos inmutables; validar autor y pertenencia de los contenidos, y conservar la predicción real del sistema. *(Completado el 2026-10-15)*
- [x] **TASK-26.2:** Consolidar pares por comparación y contenidos, con un voto vigente por revisor; distinguir revisión única, acuerdo y desacuerdo sin sobrescribir etiquetas originales. *(Completado el 2026-10-15)*
- [x] **TASK-26.3:** Calcular acuerdo observado y kappa de Cohen por pareja de revisores, indicando tamaño de muestra y casos no calculables. *(Completado el 2026-10-15)*
- [x] **TASK-26.4:** Exponer resumen, pares y exportación del ground truth mediante API tipada y filtros de comparación. *(Completado el 2026-10-15)*
- [x] **TASK-26.5:** Permitir entrenamiento con pares consensuados y registrar la política y revisiones fuente en el experimento. *(Completado el 2026-10-15)*
- [x] **TASK-26.6:** Incorporar panel de consenso y acuerdo entre revisores en Auditoría con estados vacíos y errores explícitos. *(Completado el 2026-10-15)*
- [x] **TASK-26.7:** Validar dominio, persistencia, endpoints y entrenamiento, actualizar documentación y ejecutar pruebas aisladas, compilación y lint. *(Completado el 2026-10-15)*

### Paquete 27: Aprendizaje activo
- [x] **TASK-27.1:** Definir y probar priorización determinista de casos por incertidumbre, desacuerdo y ausencia de revisión, sin modificar predicciones. *(Completado el 2026-10-15)*
- [x] **TASK-27.2:** Implementar cola paginada y filtrable con razones de prioridad y exclusión de pares ya consensuados. *(Completado el 2026-10-15)*
- [x] **TASK-27.3:** Integrar revisión desde la cola y medir cobertura de anotación antes y después de cada lote. *(Completado el 2026-10-15)*

### Paquete 28: Experimentos y mejora controlada
- [x] **TASK-28.1:** Versionar snapshots de ground truth y evaluar comparaciones completas en grupos reservados, con métricas de cobertura y correspondencias. *(Completado el 2026-10-15)*
- [x] **TASK-28.2:** Comparar versiones sobre el mismo conjunto reservado y registrar criterios de promoción y regresiones. *(Completado el 2026-10-15)*

### Paquete 29: Validación integrada en navegador
- [x] **TASK-29.1:** Incorporar y ejecutar pruebas de navegador con API y almacenamiento aislados para reserva, experimentos y recuperación de informes. *(Completado el 2026-10-15)*
- [x] **TASK-29.2:** Corregir incidencias reproducibles del flujo y documentar el procedimiento de validación y sus límites. *(Completado el 2026-10-15)*

La Fase 4 (usuarios, PostgreSQL y gestión documental) permanece fuera del alcance de estos paquetes. El avance de Fase 3 se refiere a implementación; la anotación académica real y los experimentos institucionales requieren datos revisados.

### Paquete 30: Docker y análisis SonarQube
- [x] **TASK-30.1:** Preparar Dockerfiles y Compose con persistencia, proxy web y comprobaciones de salud; validar configuración. *(Configuración Compose validada el 2026-10-15; construcción y ejecución pendientes en TASK-30.3)*
- [x] **TASK-30.2:** Configurar SonarQube, PostgreSQL, escáner y cobertura Python con instrucciones de ejecución. *(Configuración validada el 2026-10-15; generación efectiva de cobertura y análisis pendientes en TASK-30.3)*
- [x] **TASK-30.3:** Construir y arrancar los contenedores, comprobar persistencia, generar reportes de cobertura y ejecutar el análisis real de SonarQube. *(Completado el 2026-10-15: 99 pruebas aprobadas y análisis finalizado; hallazgos documentados en RESULTADO_SONARQUBE.md)*
- [x] **TASK-30.4:** Publicar Docker en localhost:5173, unificar la configuración y documentación de acceso y comprobar la interfaz en navegador. *(Completado el 2026-10-15: Chromium, consultas API y contenedores saludables)*

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

---

### Sesión 14 — 2026-09-24
- **Objetivos de la sesión:**
  - Diagnosticar y corregir anomalías en la segmentación curricular y comparaciones de sílabos idénticos (resolución del bug 67%/66% y eliminación de redundancias).
  - Optimizar el algoritmo de asignación competitiva de candidatos priorizando ítems libres (`usage == 0`) para evitar inanición (*starvation*) y repeticiones.
  - Implementar precomputación vectorial por lote (`encode_texts` en Sentence Transformers + producto punto) reduciendo tiempos de comparación de 60s a <1s.
  - Completar el **Paquete 18: Evidencias en Reportes y Validación E2E de Fase 1.5** (`TASK-18.1` y `TASK-18.2`).
  - Incorporar trazabilidad espacial (Bounding Boxes, coordenadas de puntos tipográficos 72 DPI y extractos) en los generadores de reportes formales PDF y HTML.
  - Extender la suite de pruebas automatizadas con el flujo completo E2E de Fase 1.5.
- **Tareas completadas:**
  - Corrección de `SyllabusSegmenter`: soporte para todas las viñetas Unicode (`•●○■▪\*\-–—`), descarte de preámbulos administrativos y filtrado de tablas/rúbricas.
  - Optimización de `CompareSyllabiUseCase`: selección competitiva sin redundancia, atajo de identidad exacta 100% y batch embeddings.
  - Resincronización y re-segmentación limpia de todos los sílabos en `convcomp.db`.
  - `TASK-18.1`: Incorporación de coordenadas espaciales y Anexo 5 en reportes formales PDF y HTML.
  - `TASK-18.2`: Implementación de prueba E2E de Fase 1.5 en `tests/integration/test_fase1_5_endpoints.py`.
- **Resultados de Validación:**
  - Suite completa de **35 pruebas automatizadas pasando al 100%** en `pytest`.
  - Compilación frontend de producción (`npm run build`) en 990 ms con 0 errores de TypeScript.
---

### Sesión 15 — 2026-10-01
- **Objetivos de la sesión:**
  - Diagnosticar y corregir la anomalía del visor PDF donde se marcaban zonas incorrectas (cabeceras en lugar de tópicos) o se remarcaba únicamente una sola palabra aislada (< 80 pt) en lugar del contenido temático correspondiente.
  - Implementar algoritmo de fusión de fragmentos tipográficos en líneas completas y agrupamiento de líneas contiguas en recuadros envolventes (*envelope bounding boxes*) coherentes.
  - Eliminar la búsqueda ingenua de palabras clave aisladas (`keywords[:3]`) que saltaban a ocurrencias accidentales en cabeceras o tablas.
  - Corregir la resolución de número de página en `SyllabusSegmenter` y `SpatialLocatorService` para temas que cruzan a páginas posteriores dentro de una misma unidad.
  - Implementar auto-desplazamiento suave (*auto-scroll*) en el visor PDF hacia la primera evidencia de la página renderizada.
  - Actualizar retroactivamente todas las correspondencias de la base de datos `convcomp.db`.
- **Tareas completadas:**
  - `TASK-VIEWER-FIX-01`: Reingeniería de [SpatialLocatorService](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/backend/app/infrastructure/pdf/spatial_locator.py):
    - Limpieza de prefijos sintéticos generados durante la segmentación (`THEME - `, `UNIDAD X: `, `Semana Y: `, viñetas).
    - Fusión de rectángulos de palabras en líneas tipográficas completas (`_merge_rects_into_lines`).
    - Agrupamiento de líneas contiguas en bounding boxes de párrafo (`_cluster_contiguous_lines`).
    - Búsqueda adaptativa de página real en páginas adyacentes si el tema cruza de página.
  - `TASK-VIEWER-FIX-02`: Actualización de [CompareSyllabiUseCase](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/backend/app/application/compare_syllabi.py) para asignar `actual_obj_page` y `actual_cmp_page` basados en las evidencias localizadas.
  - `TASK-VIEWER-FIX-03`: Mejora en [SyllabusSegmenter](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/backend/app/infrastructure/nlp/segmenter.py) con `_resolve_item_page` para detectar de forma temprana en qué página del texto crudo cae cada tópico.
  - `TASK-VIEWER-FIX-04`: Optimización en [EvidenceOverlay.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/EvidenceOverlay.tsx) con control de desborde superior para insignias (`top < 24`) e índice ordinal para evitar solapamiento.
  - `TASK-VIEWER-FIX-05`: Implementación de auto-centrado y desplazamiento suave en [PdfDocumentViewer.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/PdfDocumentViewer.tsx).
  - `TASK-VIEWER-FIX-06`: Script de migración y refresco retroactivo en [refresh_evidence_regions.py](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/backend/scripts/refresh_evidence_regions.py) actualizando 1567 correspondencias existentes en `convcomp.db`.
- **Resultados de Validación:**
  - Suite de **37 pruebas automatizadas pasando al 100%** en `pytest` (incluyendo 2 nuevas pruebas unitarias para ancho de frase y auto-detección de página).
  - Compilación frontend de producción (`npm run build`) limpia en 686 ms con 0 errores.
  - Inspección pericial en base de datos validando que tópicos de 1 sola palabra (6-36 pt) ahora abarcan adecuadamente las frases completas (100-360 pt) y párrafos consolidados.
---

### Sesión 16 — 2026-10-01
- **Objetivos de la sesión:**
  - Optimizar la IA de comparación de sílabos resolviendo la deficiencia del emparejamiento voraz (*greedy*) mediante optimización global en grafo bipartito (`scipy.optimize.linear_sum_assignment` / Algoritmo Húngaro).
  - Implementar ajuste dinámico y adaptativo de pesos multivariados para neutralizar penalizaciones estructurales artificiales ante diferencias en el orden curricular de unidades entre universidades (ej. Unidad 1 vs Unidad 5).
  - Potenciar el vocabulario técnico de ingeniería mediante un diccionario canónico de acrónimos y conceptos clave (`TECHNICAL_ACRONYMS`) integrado en normalización, TF-IDF y Sentence Transformers.
  - Actualizar la versión formal del algoritmo a `bipartite-adaptive-002` garantizando 100% de explicabilidad, determinismo matemático y compatibilidad con el sistema de trazabilidad espacial y revisiones humanas.
  - Desarrollar pruebas unitarias para validación anti-canibalización y preservación de score entre unidades dispares.
- **Tareas completadas:**
  - `TASK-AI-OPT-01`: Incorporación de `TECHNICAL_ACRONYMS` y `expand_technical_acronyms` en [normalizer.py](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/backend/app/infrastructure/nlp/normalizer.py) con soporte bidireccional para bases de datos (BBDD, SGBD, RDBMS), redes (WAN, LAN, VPN, OSPF, BGP, ACL, CIDR), sistemas (POO, MVC, API, REST, CRUD) y modelado (1FN, 2FN, 3FN).
  - `TASK-AI-OPT-02`: Integración de expansión canónica de acrónimos en [vector_service.py](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/backend/app/infrastructure/nlp/vector_service.py) para vectorización en lote (`encode_texts`) y similitud semántica.
  - `TASK-AI-OPT-03`: Implementación de [linear_sum_assignment](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/backend/app/application/compare_syllabi.py) en `CompareSyllabiUseCase` para maximizar globalmente la afinidad bipartita entre los conjuntos temáticos de ambos sílabos.
  - `TASK-AI-OPT-04`: Algoritmo de ponderación adaptativa en `_compute_pair_score`: neutralización del peso estructural (a `0.0`) y transferencia a componentes semántica (`0.50`) y léxica (`0.35`) cuando la afinidad conceptual es sólida ($\ge 0.75$ léxica o $\ge 0.80$ semántica), garantizando la correcta clasificación como `MATCH`.
  - `TASK-AI-OPT-05`: Nueva suite de pruebas unitarias en [test_compare_syllabi_use_case.py](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/tests/unit/test_compare_syllabi_use_case.py):
    - `test_bipartite_matching_prevents_greedy_cannibalization`: valida que un tema inicial no canibalice el candidato de afinidad perfecta de un tema posterior.
    - `test_adaptive_weights_preserves_score_across_different_units`: valida que temas conceptualmente idénticos en unidades distantes conserven clasificación `MATCH` sin castigo estructural.
- **Resultados de Validación:**
  - Suite completa de **40 pruebas automatizadas pasando al 100%** en `pytest` (41 s).
  - Compilación frontend de producción (`npm run build`) limpia en 565 ms con 0 errores de TypeScript.
  - `TASK-AI-UNIV-01`: Implementación de Contención Direccional Asimétrica (`compute_asymmetric_containment`) y Coeficiente de Szymkiewicz-Simpson en [vector_service.py](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/backend/app/infrastructure/nlp/vector_service.py), eliminando el sesgo de longitud en cualquier disciplina académica.
  - `TASK-AI-UNIV-02`: Descomposición granular asimétrica multi-frase (`_get_item_phrases`) y evaluación cruzada en [compare_syllabi.py](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/backend/app/application/compare_syllabi.py), detectando sub-tópicos independientes dentro de párrafos extensos.
  - `TASK-AI-UNIV-03`: Calibración de umbrales pedagógicos de convalidación universitaria (`MATCH >= 0.75`, `PARTIAL_MATCH >= 0.58`, `UNCERTAIN >= 0.45`) con piso representativo ($\ge 0.80$) ante contención léxica directa ($\ge 0.85$).
  - `TASK-AI-UNIV-04`: Prueba unitaria universal de convalidación orientada al objetivo (`test_target_driven_subsumption_universal_coverage`) en [test_compare_syllabi_use_case.py](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/tests/unit/test_compare_syllabi_use_case.py).
  - `TASK-AI-UNIV-05`: Resincronización y actualización retroactiva en `convcomp.db` con [resync_and_recompare_syllabi.py](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/backend/scripts/resync_and_recompare_syllabi.py).
- **Resultados de Validación:**
  - Suite completa de **40 pruebas automatizadas pasando al 100%** en `pytest` (41 s).
  - Compilación frontend de producción (`npm run build`) limpia en 368 ms con 0 errores de TypeScript.
  - **Métricas Reales en Caso Real (Continental vs UTP):**
    - Score Global: de 0.59 inicial a **0.8905** (homologabilidad académica sólida).
    - Cobertura Objetivo: de 38.9% inicial a **100.0%** (16/16 temas formativos del sílabo objetivo convalidados exitosamente).
    - Cero falsos negativos: temas como "Capa de aplicación", "Fundamentos de seguridad en redes", "Configuración básica de router", "Sistemas numéricos" y "Resolución de redireccionamiento (ARP)" ahora clasificados con evidencia localizada completa.
---

### Sesión 17 — 2026-10-04
- **Objetivos de la sesión:**
  - Iniciar formalmente la **Fase 2.0 (OCR + Aprendizaje Supervisado y Calibración)**.
  - Documentar especificación de flujo en `docs/FLUJO_FASE_2.md` y desglosar los Paquetes 19 al 24 en `docs/TASKS.md`.
  - Implementar arquitectura de Ingesta OCR (`IOCREngine` y `RapidOcrEngine`) con escalado a coordenadas tipográficas (72 DPI) y compatibilidad total con el visor pericial de Fase 1.5.
  - Implementar pipeline de Aprendizaje Supervisado (`DatasetService`, `SklearnSupervisedTrainer`, calibración de probabilidades y evaluación contra baseline).
  - Implementar versionado formal de modelos (`model_versions`, `SqliteModelVersionRepository` y endpoints API).
  - Implementar ciclo de vida completo: Entrenamiento → Evaluación científica → Activación en producción → Inferencia con fallback.
- **Tareas completadas:**
  - `TASK-19.1` a `TASK-19.4`: Paquete 19 — Ingesta OCR completo (`IOCREngine`, `RapidOcrEngine`, integración en `PyMuPdfExtractor`, pruebas unitarias).
  - `TASK-20.1` a `TASK-20.2`: Paquete 20 — `DatasetService` con extracción de 5 características, exportación CSV/JSON y dataset bootstrap sintético de calibración.
  - `TASK-21.1` a `TASK-21.3`: Paquete 21 — `SklearnSupervisedTrainer` con Regresión Logística Calibrada y Random Forest, evaluación científica con benchmarking vs baseline heurístico.
  - `TASK-22.1` a `TASK-22.3`: Paquete 22 — `SqliteModelVersionRepository`, `ModelInferenceService`, `TrainModelUseCase` y endpoints REST completos (`/api/models`).
  - `TASK-24.1` a `TASK-24.3`: Pruebas unitarias de OCR (`test_ocr_engine.py`), ML (`test_supervised_model.py`) e integración de ciclo de vida (`test_model_lifecycle_endpoints.py`).
- **Resultados de Validación:**
  - Suite de **51 pruebas automatizadas pasando al 100%** en `pytest` (81.35 s).

---

### Sesión 18 — 2026-10-05
- **Objetivos de la sesión:**
  - Completar el **Paquete 23: Frontend — Gestión de Modelos y Auditoría de Aprendizaje**.
  - Implementar `ModelManagementView.tsx` con lista de versiones, panel de entrenamiento configurable, métricas científicas detalladas, importancia de características y matriz de confusión interactiva.
  - Integrar la nueva pestaña "Modelos IA" en el encabezado de navegación (`Header.tsx`) y en `App.tsx`.
  - Extender `api.ts` con métodos tipados de gestión de modelos y actualizar `types/index.ts` con las interfaces de Fase 2.0.
  - Actualizar TASKS.md reflejando el 100% de Fase 2.0 completada.
- **Tareas completadas:**
  - `TASK-23.1`: [ModelManagementView.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/ModelManagementView.tsx) — Vista completa de gestión de modelos con tarjetas de versión, insignias de rendimiento y selector de detalle.
  - `TASK-23.2`: Visualización de métricas ($F_1$, Precisión, Recall, Exactitud), importancia de características con barras y matriz de confusión con codificación por color (verde diagonal / rojo errores).
  - `TASK-23.3`: Panel de entrenamiento configurable (algoritmo, tamaño de evaluación, bootstrap, activación automática) y botones de activación por versión.
  - `TASK-23.4`: Pestaña "Modelos IA" integrada en navegación principal de [Header.tsx](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/components/Header.tsx).
  - Extensión de [api.ts](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/services/api.ts): `listModels()`, `getActiveModel()`, `trainModel()`, `activateModel()`, `getModelEvaluation()`, `getDatasetExportFormatUrl()`.
  - Extensión de [types/index.ts](file:///d:/DESARROLLO_APLICACIONES/Python/conv_comp/frontend/src/types/index.ts): `ModelVersion`, `ModelMetrics`, `BaselineComparison`, `TrainModelRequest`, `DatasetStats`.
- **Resultados de Validación:**
  - Suite de **51 pruebas automatizadas pasando al 100%** en `pytest`.
  - Compilación frontend de producción (`npm run build`) limpia en 1.50 s con 0 errores de TypeScript.
  - **Fase 2.0 completada al 100%** — 85/85 tareas globales del proyecto implementadas.

---

### Sesión 19 — 2026-10-15
- **Objetivos de la sesión:**
  - Integrar las tareas de consolidación posteriores a Fase 2.0 y comenzar su ejecución con validación reproducible.
- **Tareas completadas:**
  - `TASK-25.1` a `TASK-25.6`: versión 2.1.0 coherente en API, salud y manifiesto; README actualizado; dependencias RapidOCR, NumPy y joblib declaradas.
  - Configuración de almacenamiento con `CONVCOMP_DATA_DIR` y `CONVCOMP_REPORTS_DIR`; colección y ejecución de pruebas aisladas, incluyendo modelos y activaciones.
  - Dataset con IDs de contenidos reales y procedencia académica persistida mediante migración aditiva; recuperación de metadatos históricos por consulta y exportación JSON/CSV.
  - Separación determinista por componentes conectados de universidad/asignatura, sílabo y contenido; calibración por grupos cuando existen datos suficientes; rechazo explícito de procedencia incompleta o particiones sin las clases necesarias.
  - Bootstrap únicamente en entrenamiento cuando existen revisiones reales. Métricas sintéticas identificadas en API/UI y excluidas de activación automática.
  - Visor PDF y gestión de modelos con carga bajo demanda. JavaScript inicial reducido de 785.47 kB a 309.19 kB; visor separado de 457.63 kB.
- **Resultados de validación:**
  - Suite completa: **60 pruebas aprobadas**, 2 advertencias de deprecación de dependencias, en 57.08 s. Ejecución offline de modelos para evitar descargas durante validación.
  - `npm.cmd run build`: correcto, sin advertencia de paquetes JavaScript mayores de 500 kB.
  - `npm.cmd run lint`: sin errores; conserva 8 advertencias existentes, registradas en `TASK-25.8`.
  - `python -m pip check`: sin dependencias incompatibles en el entorno instalado. No se realizó una instalación desde cero.
  - `git diff --check`: correcto. Hash SHA-256 de la base de desarrollo idéntico antes y después de las pruebas: `b48369496afb629f2c5abea79d09f77c748a96d6f0aed2567e36f72178ae8b76`.
- **Decisiones técnicas adoptadas:**
  - Mantener las fuentes conectadas en la misma partición aun si cambian de rol objetivo/comparado; conservar trazabilidad mediante IDs de ejemplos y grupos en las métricas.
  - No activar ni reentrenar el modelo de desarrollo durante las pruebas. La migración de la base local se aplicará al arrancar la aplicación actualizada.
- **Bloqueadores / Riesgos identificados:**
  - El benchmark previo del entrenador utiliza una aproximación heurística que debe alinearse con el scoring adaptativo; los valores fijos anunciados por la API para el baseline requieren revisión (`TASK-25.7`).
  - Versiones de modelos previas no registran procedencia de evaluación; la UI lo informa y recomienda reentrenar. La validación por grupos puede requerir ampliar o completar las revisiones académicas existentes.
- **Próximas tareas para la siguiente sesión:**
  - `TASK-25.7`: alinear benchmarking y representación del baseline.
  - `TASK-25.8`: resolver advertencias de lint en componentes React.

---

### Sesión 20 — 2026-10-15
- **Objetivos de la sesión:**
  - Completar las dos tareas pendientes del Paquete 25 y cerrar la consolidación de Fase 2.1.
- **Tareas completadas:**
  - `TASK-25.7`: extraer reglas puras de scoring adaptativo, umbrales y afinidad de contenido a `domain/scoring.py`; comparador y benchmark reutilizan esas reglas.
  - Retirar el doble conteo de contención en el benchmark, conservar la correspondencia `UNCERTAIN` → clase parcial y registrar el alcance por pares sin atribuir resultados a la asignación global.
  - Eliminar métricas estáticas del descriptor del baseline y unificar las respuestas de listado y modelo activo. Mantener visible el baseline activo cuando solo existen candidatos sin activar.
  - Conservar precisión float64 en la matriz de características para respetar los valores persistidos en límites adaptativos como 0.70.
  - `TASK-25.8`: eliminar las ocho advertencias de lint con carga asíncrona, dependencias estables y navegación de evidencias mediante eventos; tipar las vistas afectadas y PDF.js sin `any`.
  - Corregir Auditoría para mostrar `by_ground_truth`, que sí devuelve la API, en lugar de tasas y distribuciones inexistentes; actualizar el modelo seleccionado tras entrenar o activar sin disparar ciclos de recarga.
- **Resultados de validación:**
  - Suite completa: **67 pruebas aprobadas**, 2 advertencias de deprecación de dependencias, en 57.02 s.
  - Tras añadir el caso de precisión en el umbral, **25 pruebas específicas de scoring, ML, separación académica y endpoints de modelos aprobadas** en 2.23 s. La cobertura conjunta comprende los 68 casos actuales.
  - `npm.cmd run lint`: sin errores ni advertencias. `npm.cmd run build`: correcto, sin advertencias de tamaño de paquetes JavaScript. No se realizó validación interactiva en navegador.
  - `git diff --check`: correcto. Base de desarrollo con el mismo SHA-256 de la sesión anterior; sin entrenamiento ni activación de modelos locales durante las pruebas.
- **Decisiones técnicas adoptadas:**
  - Reutilizar reglas del dominio para impedir divergencias entre el comparador y el benchmark; mantener la evaluación por pares explícita en métricas, UI y documentación.
  - No modificar métricas históricas de modelos ya registrados; la UI indica cuándo una versión antigua no declara alcance de evaluación.
- **Bloqueadores / Riesgos identificados:**
  - Ningún bloqueador para las tareas 25.7 y 25.8. La comparación global entre sílabos y el rendimiento con revisiones humanas independientes requieren experimentos propios; no se infieren del benchmark por pares.
  - Persisten dos advertencias de deprecación del entorno Python ajenas al lint de frontend.
- **Próximas tareas para la siguiente sesión:**
  - Definir el paquete de Fase 3 a partir del roadmap: ground truth ampliado, evaluación interevaluador y aprendizaje activo, con criterios de aceptación y datos revisados independientes.
  - Las fases 3 y 4 no forman parte del 100% de alcance cerrado hasta Fase 2.1.

---

### Sesión 21 — 2026-10-15
- **Objetivos de la sesión:**
  - Definir los Paquetes 26–28 de Fase 3 e implementar el primer incremento de ground truth y acuerdo interevaluador.
- **Tareas completadas:**
  - `TASK-26.1` a `TASK-26.7`: eventos de revisión inmutables y validación de contenidos/autores; consolidación por par y voto vigente por revisor; acuerdo observado y kappa nominal por pareja.
  - API paginada de ground truth, resumen, filtros de comparación/estado y exportación JSON/CSV con votos, características, procedencia y páginas de evidencia. Revisión única y desacuerdo permanecen explícitos.
  - Entrenamiento con política `consensus`, una muestra por par acordado y trazabilidad de revisiones fuente; política `individual` conservada por compatibilidad. Sin consenso no se sustituye silenciosamente un conjunto revisado por sintéticos.
  - Panel de Auditoría con filtros, paginación, acuerdo interevaluador y acceso al informe; identificación del revisor en el visor. Cambiar de par reinicia decisión y justificación, manteniendo la identidad declarada del revisor.
  - Versión de aplicación y manifiesto sincronizados a **3.0.0**, fase 3. README y `FLUJO_FASE_3.md` describen el alcance parcial; aprendizaje activo y experimentos siguen pendientes.
- **Resultados de validación:**
  - Suite completa: **82 pruebas aprobadas**, 2 advertencias de deprecación de dependencias, en 34.72 s.
  - Tras incorporar páginas de evidencia a la consulta, **17 pruebas específicas de ground truth, endpoints y persistencia aprobadas** en 2.10 s.
  - Cobertura nueva: deduplicación de autor, correcciones sin sobrescritura, desacuerdos sin resolución por mayoría, kappa conocido/indeterminado, autores sin pares comunes, paginación superior a 500 eventos, exportaciones y entrenamiento consensuado real por grupos.
  - `npm.cmd run lint`: sin errores ni advertencias. `npm.cmd run build`: correcto, sin advertencias de tamaño de paquetes JavaScript. No se realizó validación interactiva en navegador.
  - `git diff --check`: correcto. Base local con SHA-256 idéntico al de las sesiones 19 y 20; no se activó ni entrenó el modelo local de desarrollo.
- **Decisiones técnicas adoptadas:**
  - La unidad de consenso es comparación + contenidos objetivo/comparado, incluyendo enlaces manuales válidos. Corregir una anotación agrega un evento; solo su último voto por autor interviene en consenso y acuerdo.
  - Mantener las cuatro etiquetas en la evaluación interevaluador; el mapeo de `UNCERTAIN` a clase parcial se aplica únicamente al entrenamiento supervisado y su benchmark.
  - El consenso se calcula por unanimidad entre al menos dos identificadores distintos; no equivale a adjudicación oficial ni demuestra independencia de personas sin autenticación.
  - Recuperar características y páginas de una correspondencia existente cuando el mismo par también tiene revisiones manuales. Un par manual sin características requiere procesamiento antes de entrenar.
- **Bloqueadores / Riesgos identificados:**
  - Sin bloqueadores para Paquete 26. La autenticación de autores permanece en Fase 4; los identificadores de revisión son declarados.
  - Snapshots reproducibles y evaluación completa están pendientes en Paquete 28. La funcionalidad implementada no sustituye la adquisición de anotaciones académicas reales.
- **Próximas tareas para la siguiente sesión:**
  - `TASK-27.1` a `TASK-27.3`: priorización y cola de casos para aprendizaje activo, revisión y cobertura de anotación.

---

### Sesión 22 — 2026-10-15
- **Objetivos de la sesión:**
  - Implementar el Paquete 27: cola priorizada, lotes persistidos y revisión con medición de cobertura de anotación.
- **Tareas completadas:**
  - `TASK-27.1`: reglas puras y deterministas de selección por desacuerdo, segunda revisión y ausencia de revisión; clasificación incierta y distancia a umbrales de referencia dentro de cada grupo, con desempate por IDs.
  - `TASK-27.2`: cola paginada y filtrable por comparación, motivo y revisor; exclusión de consenso y del voto único del propio autor. Incluye pares manuales propuestos sin inventar scores.
  - `TASK-27.3`: selección fija de lotes de hasta 100 casos, persistencia de autor, estrategia, umbrales y cobertura inicial; cierre idempotente con medición final independiente. Recuperación de lotes y consulta separada del estado actual.
  - Auditoría permite consultar la cola, crear o recuperar lotes, abrir evidencias, registrar decisiones y comparar cobertura antes/después. Los paneles de estadísticas y consenso se actualizan al registrar votos.
  - Nuevas tablas aditivas `annotation_batches` y `annotation_batch_completions`, repositorio y puertos de dominio; versión de aplicación y manifiesto **3.1.0**, manteniendo fase 3.
- **Resultados de validación:**
  - Suite completa: **90 pruebas aprobadas**, 2 advertencias de deprecación de dependencias, en 51.94 s.
  - Tras completar la persistencia de umbrales, **8 pruebas específicas de prioridad y endpoints/lotes aprobadas** en 2.05 s.
  - Casos cubiertos: orden estable, deduplicación de pares, consenso excluido, voto único por autor, pares manuales sin puntuación, denominador de cobertura, paginación, recuperación y cierre inmutable/idempotente, errores de validación y pérdida de fuentes.
  - `npm.cmd run lint`: sin errores ni advertencias. `npm.cmd run build`: correcto, sin advertencias de tamaño de paquetes JavaScript. No se realizó validación interactiva en navegador.
  - `git diff --check`: correcto. Base de desarrollo con SHA-256 idéntico al de las sesiones previas; ningún entrenamiento ni activación de modelos locales.
- **Decisiones técnicas adoptadas:**
  - Los umbrales de prioridad son referencias declaradas y versionadas; el score no se presenta como probabilidad ni como confianza calibrada.
  - Medir cobertura de anotación sobre pares propuestos, sin confundirla con cobertura curricular. Los lotes conservan su selección aunque la cola cambie.
  - Mantener separadas selección inicial, cierre persistido y estado actual. Un cierre posterior repetido no sobrescribe la medición original; si una fuente desaparece, el progreso informa conflicto.
  - Registrar votos mediante el endpoint existente para conservar la predicción original. Cerrar un lote no exige consenso ni dispara entrenamiento: un solo voto puede requerir otro autor.
- **Bloqueadores / Riesgos identificados:**
  - Ningún bloqueador para Paquete 27. La autenticación sigue pendiente en Fase 4; el autor del lote es declarado.
  - Los cambios antes/después pueden incluir anotaciones concurrentes de otros revisores. La mejora del modelo no se infiere de cobertura de anotación; requiere los experimentos del Paquete 28.
- **Próximas tareas para la siguiente sesión:**
  - `TASK-28.1` y `TASK-28.2`: snapshots de ground truth, evaluación de comparaciones completas y comparación controlada de versiones sobre conjuntos reservados.

---

### Sesión 23 — 2026-10-15
- **Objetivos de la sesión:**
  - Completar el Paquete 28 con conjuntos reservados reproducibles y comparación controlada de versiones sobre sílabos completos.
- **Tareas completadas:**
  - `TASK-28.1`: snapshots append-only de contenidos, fuentes, matriz completa de consenso definitivo, revisiones y traza NLP; hash de contenido y huella de código/dependencias. Evaluación del comparador completo con precisión, recall, F1 y errores de cobertura en ambos sentidos.
  - `TASK-28.2`: experimentos persistidos con referencia y candidato sobre el mismo conjunto, criterios explícitos, regresiones por comparación y recomendación sin activación automática. Exportación JSON de snapshots e informes.
  - Exclusión transitiva de fuentes reservadas antes de entrenamiento y calibración; procedencia verificable de todas las fuentes humanas expuestas. Rechazo de modelos contaminados, antiguos sin procedencia verificable o con artefactos ausentes/alterados.
  - Panel de evaluación en Gestión de modelos para reservar comparaciones, seleccionar versiones, configurar límites de F1 y consultar métricas y comprobaciones.
  - Corrección del comparador: aplica la inferencia supervisada que antes recibía sin utilizarla. Carga fallida limpia la caché y la activación comprueba el artefacto antes de cambiar el modelo activo. Versiones nuevas con identificadores únicos y ruta de artefacto persistida.
  - Aplicación y manifiesto en **3.2.0**. README, flujo y protocolo de experimentos actualizados. Alcance de desarrollo de Fase 3 completado: **12/12**, total planificado **105/105**.
- **Resultados de validación:**
  - Suite completa: **99 pruebas aprobadas**, 2 advertencias de deprecación de dependencias, en 56.09 s.
  - Tras completar las anotaciones de tipos del motor, **9 pruebas específicas de evaluación aprobadas** en 2.81 s.
  - Cobertura nueva: inferencia efectiva, replay repetible, matriz incompleta, reserva y grupos transitivos, entrenamiento independiente, contaminación, pérdida/cambio de artefactos, cambio de entorno, mejoras y regresiones, muestras insuficientes, persistencia inmutable y activación fallida sin alterar el modelo activo.
  - `npm.cmd run lint`: correcto. `npm.cmd run build`: correcto, sin advertencias de tamaño de paquetes JavaScript. Sin prueba interactiva en navegador.
  - `git diff --check`: correcto. SHA-256 de la base local conservado: `b48369496afb629f2c5abea79d09f77c748a96d6f0aed2567e36f72178ae8b76`. No se entrenaron ni activaron modelos en la base de desarrollo.
- **Decisiones técnicas adoptadas:**
  - Exigir consenso definitivo para cada par objetivo × comparado; un par desconocido no constituye un negativo. Congelar las salidas NLP y repetir selección global y coberturas sin crear comparaciones nuevas ni releer PDFs.
  - Usar `MATCH` y `PARTIAL_MATCH` como positivos para las métricas de correspondencia; expresar errores de cobertura en puntos porcentuales. No inventar un score humano continuo ni inferir rendimiento institucional desde fixtures sintéticos.
  - Bloquear fuentes reservadas por identidad académica, documento, contenidos y pares normalizados. Un ID de versión evaluado conserva el mismo manifiesto y artefacto; cualquier sustitución requiere otra versión.
- **Bloqueadores / Riesgos identificados:**
  - Sin bloqueadores de implementación para Paquete 28. La validación institucional requiere matrices exhaustivas de revisiones y modelos entrenados con fuentes humanas independientes. Las versiones antiguas sin procedencia deben reentrenarse.
  - Los autores siguen siendo identificadores declarados. La reserva es permanente en esta versión; no se incorpora importación ni liberación de snapshots.
- **Próximas tareas para la siguiente sesión:**
  - Validar el flujo en navegador y preparar anotaciones institucionales independientes para ejecutar experimentos reales.
  - Definir el alcance de Fase 4 antes de incorporar usuarios, PostgreSQL o gestión documental; quedan fuera de los paquetes cerrados de Fase 3.

---

### Sesión 24 — 2026-10-15
- **Objetivos de la sesión:**
  - Integrar las tareas de validación en navegador y comprobar el flujo científico con frontend y API reales sobre almacenamiento aislado.
- **Tareas completadas:**
  - `TASK-29.1`: Playwright y configuración reproducible de Chromium, API temporal con fuentes y vectores controlados y arranque/cierre automático de procesos propios. Sin endpoints de preparación en producción ni uso de la base de desarrollo.
  - Cuatro escenarios: reserva y experimento exitoso con descarga y recuperación; versiones iguales deshabilitadas; matriz incompleta rechazada sin guardar; recuperación de consulta fallida y estados vacíos. El primer escenario también verifica que no se activa el candidato ni aparecen excepciones JavaScript.
  - `TASK-29.2`: al reintentar una consulta fallida, seleccionar el conjunto disponible cuando no hay selección válida; presentar los pesos y umbrales anidados del baseline con sus valores, evitando `[object Object]`.
  - Documentación de preparación, ejecución, evidencias y límites en `VALIDACION_NAVEGADOR.md`. README y protocolo vinculados. Aplicación y manifiesto actualizados a **3.2.1**, fase 3.
- **Resultados de validación:**
  - Ejecución integrada final: **4 pruebas de Chromium aprobadas en 43.4 s**, comando terminado con código 0 y servidores temporales cerrados. Informe HTML y captura completa del resultado generados; captura inspeccionada visualmente.
  - `npm.cmd run lint` y `npm.cmd run build`: correctos, incluyendo configuración y pruebas TypeScript. Sin advertencias de tamaño de paquetes JavaScript.
  - **12 pruebas de backend aprobadas en 14.73 s**: salud/OpenAPI, endpoints y evaluación científica. Persisten dos deprecaciones de dependencias. La suite completa de 99 pruebas estaba aprobada en la sesión 23; no se modificó la lógica de backend en esta sesión.
  - `git diff --check`: correcto. SHA-256 de la base de desarrollo conservado: `b48369496afb629f2c5abea79d09f77c748a96d6f0aed2567e36f72178ae8b76`. No hubo entrenamiento ni activación sobre datos locales de desarrollo.
- **Decisiones técnicas adoptadas:**
  - Reutilizar fixtures controlados de integración para anotar y registrar el candidato, conservando API y persistencia reales durante el flujo. Simular únicamente respuestas de consulta fallida y estado vacío.
  - Fijar Playwright en el lockfile y permitir un ejecutable Chromium local mediante `CONVCOMP_BROWSER_EXECUTABLE`. Dependencias obtenidas de caché sin descargar modelos ni paquetes por red.
  - Iniciar procesos directamente para evitar el bloqueo de cierre de árboles de procesos observado con el arranque estándar en este entorno Windows. Reservar puertos exclusivos y rechazar reutilizar servidores activos.
- **Bloqueadores / Riesgos identificados:**
  - Sin bloqueadores para el Paquete 29. La cobertura se limita al panel científico en Chromium de escritorio; no se acredita compatibilidad móvil ni otros navegadores.
  - Siguen pendientes aceptación manual institucional, anotaciones reales e identidad autenticada de revisores. Los datos controlados no demuestran rendimiento científico institucional.
- **Próximas tareas para la siguiente sesión:**
  - Definir el alcance y criterios de aceptación del siguiente incremento de Fase 4 según el roadmap.
  - Ejecutar experimentos institucionales cuando se disponga de matrices exhaustivas y fuentes de entrenamiento independientes.

### Sesión 25 — 2026-10-15
- **Objetivos de la sesión:** Preparar los archivos de despliegue Docker y el análisis SonarQube solicitados.
- **Tareas completadas:**
  - `TASK-30.1`: Dockerfiles de API y frontend, Compose con volúmenes persistentes, usuarios sin privilegios, proxy Nginx para `/api/` y comprobaciones de salud. Contexto de construcción sin datos locales ni secretos.
  - `TASK-30.2`: Compose independiente de SonarQube y PostgreSQL 17, servicio de pruebas Python con pytest-cov, escáner con espera de Quality Gate, configuración de alcance Python/TypeScript y reportes relativos. Variables de ejemplo, README y guía `DOCKER_SONARQUBE.md`.
- **Resultados de validación:**
  - Ambos archivos Compose aceptados por `docker compose config --quiet`, incluido el perfil de herramientas; contraseña ficticia usada solo en el proceso de validación.
  - Suite de backend en almacenamiento temporal y modo offline: **99 pruebas aprobadas en 48.38 s**, dos advertencias de deprecación de dependencias existentes.
  - `npm.cmd run build` y `npm.cmd run lint`: correctos. No se modificó la lógica de aplicación ni se añadieron pruebas que repliquen la configuración.
  - `git diff --check`: correcto. No se ejecutaron contenedores ni se generaron resultados de SonarQube.
- **Decisiones técnicas adoptadas:**
  - Mantener SQLite para la aplicación y reservar PostgreSQL para SonarQube. Uvicorn con un trabajador, frontend compilado con Node 24 y ruta relativa `/api`.
  - Persistir base, PDF, modelos supervisados, reportes y caché de embeddings en volúmenes Docker. Instancias nuevas sin importación automática de los datos de desarrollo.
  - Importar cobertura Python real cuando se genere; incluir el frontend en el análisis sin atribuirle cobertura inexistente. Escáner con fuentes de solo lectura y directorio temporal escribible.
- **Bloqueadores / Riesgos identificados:**
  - `TASK-30.3` pendiente: el motor Docker no responde en su tubería local. No se acreditan construcción, arranque, persistencia ni análisis real.
  - La instalación local de pytest-cov se quedó detenida descargando metadatos y se canceló; no se generó el XML de cobertura. Dependencia declarada y comandos de generación documentados para el entorno de ejecución.
  - SonarQube requiere una contraseña propia de PostgreSQL, inicialización del administrador y token de proyecto. Las etiquetas de imágenes predeterminadas son actualizables; fijar versiones o digest revisados para despliegues repetibles.
- **Próximas tareas para la siguiente sesión:**
  - Iniciar Docker Desktop con contenedores Linux, construir y arrancar la aplicación y verificar persistencia mediante recreación.
  - Inicializar SonarQube, ejecutar pruebas con cobertura, analizar el proyecto y revisar los hallazgos y el Quality Gate reales antes de cerrar `TASK-30.3`.

### Sesión 26 — 2026-10-15
- **Objetivos de la sesión:** Continuar con Docker disponible, validar el despliegue y ejecutar el análisis SonarQube real.
- **Tareas completadas:**
  - `TASK-30.3`: imágenes construidas, cuatro servicios saludables, comprobación HTTP de frontend y API, carga y descarga de PDF sintético y persistencia de SQLite y del archivo tras recrear ambos contenedores.
  - Creación de `.env` local con contraseña aleatoria de PostgreSQL, inicialización de SonarQube, reemplazo de la clave inicial de administrador y generación del token del proyecto; secretos guardados únicamente en `.env`, excluido de Git.
  - Corrección de `.dockerignore`: `.coverage*` también excluía `.coveragerc`; sustituido por los patrones específicos de archivos de datos de cobertura.
  - Preparación del modelo real de embeddings en la etapa Docker `test`; la prueba de paráfrasis fallaba en la primera ejecución por ausencia de ese modelo en modo offline. Se conserva la lógica de aplicación y las aserciones de pruebas.
- **Resultados de validación:**
  - **99 pruebas aprobadas en Docker en 45.63 s**, sin fallos ni omisiones, dos advertencias de deprecación de dependencias. Cobertura de líneas del backend: **90.03%**; ramas: **72.68%**; combinada: **86.67%**. Reportes XML generados e importados por SonarQube.
  - SonarQube **26.10.0.133078** y escáner **8.1.0.6389**: ejecución exitosa con código 0, Quality Gate `PASSED`, 4 incidencias BUG, 43 CODE_SMELL, 0 vulnerabilidades detectadas y 1.1% de duplicación. Cobertura global: **75.0%**, incluyendo frontend sin reporte de cobertura.
  - Primer análisis con `conditions: []`: el gate no evaluó condiciones. Los 47 hallazgos requieren revisión; no se acredita su resolución. Informe y prioridades en `RESULTADO_SONARQUBE.md`.
  - Frontend en `http://localhost:18080`, API 3.2.1 saludable, navegación SPA y PDF verificados antes y después de recreación. `pip check` en la API: correcto.
- **Decisiones técnicas adoptadas:**
  - Cambiar únicamente el puerto de esta instancia mediante `APP_PORT=18080` porque Windows rechazó publicar 8080; conservar el puerto predeterminado del archivo de ejemplo.
  - Precargar embeddings solo en la imagen de pruebas y ejecutarlos offline; producción conserva su caché persistente independiente. No rebajar umbrales ni reemplazar la prueba de paráfrasis por datos simulados.
  - Conservar logs, XML, métricas JSON y prueba de persistencia en `.reports/`, excluido de Git. Dejar aplicación y SonarQube en ejecución para revisión del usuario.
- **Bloqueadores / Riesgos identificados:**
  - Sin bloqueadores para el Paquete 30. Los hallazgos del análisis quedan pendientes de revisión; las 26 incidencias CRITICAL señalan campos Optional sin valor predeterminado en modelos de respuesta y requieren decidir el contrato antes de modificarlos.
  - No se ejecutó Playwright ni análisis de dependencias SCA en esta sesión. La cobertura de frontend requiere instrumentación adicional.
- **Próximas tareas para la siguiente sesión:**
  - Revisar las cuatro incidencias de fiabilidad y los contratos de respuesta señalados por SonarQube.
  - Definir una referencia de código nuevo y condiciones efectivas de Quality Gate para análisis posteriores.

### Sesión 27 — 2026-10-15
- **Objetivos de la sesión:** Resolver el acceso al frontend Docker desde la dirección localhost:5173 indicada por el usuario y dejar el proyecto en ejecución.
- **Tareas completadas:**
  - `TASK-30.4`: publicar el frontend en 5173, actualizar `.env`, `.env.example`, el valor predeterminado de Compose y las direcciones de README y guías.
  - Documentar el comando de arranque completo y conservar el archivo `.env` existente al repetir las instrucciones de preparación.
- **Resultados de validación:**
  - Diagnóstico: los dos contenedores estaban saludables y respondían en 18080; la dirección utilizada por el usuario era 5173. Se recreó el frontend con el nuevo puerto mediante `docker compose up -d --build --wait --wait-timeout 180`.
  - Verificación real en Chromium sobre `http://localhost:5173`: interfaz React visible, navegación al registro y al panel de modelos y retorno a la pantalla de evaluación con dos controles de PDF.
  - Siete respuestas HTTP 200 de la API, incluida la carga de modelos, snapshots, experimentos, estadísticas, comparaciones y sílabos. Salud 3.2.1 correcta. Sin errores JavaScript ni solicitudes fallidas.
  - Captura y resultado en `.reports/frontend-docker-5173.png` y `.reports/frontend-docker-5173.json`. No se repitió la suite científica por tratarse de un cambio de puerto y documentación.
- **Decisiones técnicas adoptadas:** Mantener Nginx en 8080 dentro del contenedor y publicar 5173 en el host; conservar los volúmenes y las rutas `/api` existentes.
- **Bloqueadores / Riesgos identificados:** Sin bloqueadores. Docker ocupa 5173; una instancia Vite simultánea debe utilizar otro puerto.
- **Próximas tareas para la siguiente sesión:** Revisar los hallazgos de SonarQube documentados cuando se solicite su corrección.

### Sesión 28 — 2026-10-17
- **Objetivos de la sesión:** Adecuar la Fase 3 al 100% de la rúbrica del manual de evaluación de calidad proporcionado por el usuario.
- **Tareas completadas:**
  - `TASK-31.1`: lectura del manual, normalización del curso y estructura de metadatos académicos, inclusión del pipeline oficial, eliminación de exclusiones de carpetas y excepciones Git para reportes reales de cobertura.
  - `TASK-31.2`: corrección de los 47 hallazgos históricos. Endpoint de PDF en grupo de hilos, respuesta 400 para PDF vacío, campos obligatorios anulables con `Tipo | None`, promesa de render gestionada, botones y etiquetas accesibles y limpieza de expresiones regulares.
  - `TASK-31.3`: Vitest con cobertura V8 de todo el frontend, pruebas de comportamiento HTTP/UI, normalización de rutas LCOV y verificación estricta de tipos. XML Python/JUnit y LCOV importados por SonarQube.
  - `TASK-31.4`: gate local con condiciones globales, verificador reproducible de la rúbrica, análisis final y documentación de métricas y entrega institucional.
- **Resultados de validación:**
  - **113 pruebas Python aprobadas** en Docker en **43,86 s**, dos advertencias de deprecación. Coverage.py: **90,22%** de líneas, **72,95%** de ramas y **86,87%** combinado.
  - **100 pruebas Vitest aprobadas**; frontend completo con **77,01%** de líneas y **65,10%** de ramas. **4 pruebas Playwright aprobadas** en Chromium en **14,2 s**.
  - Compilación, tipado estricto de aplicación/pruebas, lint y `git diff --check` correctos. Auditoría npm sin vulnerabilidades tras corregir `source-map-js`.
  - SonarQube: **Quality Gate PASSED**, **20/20 estimado según el manual**, **82,4%** de cobertura global, **1,1%** de duplicación, A/A/A y **0 bugs, vulnerabilidades, code smells y hotspots**. Once condiciones efectivamente evaluadas y aprobadas, incluidas las globales.
  - Análisis `0e0ec603-3f87-4a75-92af-5d2a8def4e54`, 18:13:55–18:16:23 America/Lima. Verificador con salida 0 y `cumple: true`; evidencias y comandos en `RESULTADO_SONARQUBE.md` y `EVALUACION_CALIDAD.md`.
- **Decisiones técnicas adoptadas:**
  - Interpretar cumplimiento total como 20/20 en los seis criterios del manual; exigir cobertura global ≥80% y mantener todo el código de aplicación en el alcance.
  - Preservar los contratos obligatorios que aceptan `null`; no convertirlos en campos omitibles. La regla S8396 acepta expresamente las uniones anulables `Tipo | None`.
  - El gate exige adicionalmente cero incidencias abiertas. La regla del manual otorga todos los puntos de hotspots cuando no existen.
  - Versionar únicamente los reportes de cobertura/resultados que necesita el pipeline académico; conservar logs, historial y JSON de comprobación local ignorados.
- **Bloqueadores / Riesgos identificados:**
  - Sin bloqueadores para el cumplimiento local. La nota de 20/20 es una estimación reproducible, no una calificación institucional emitida.
  - No se ejecutó el pipeline institucional. El historial de análisis requiere permisos distintos de los del token de proyecto; se consultó por separado con el administrador local sin exportar credenciales.
  - El perfil/versión institucional puede diferir del local. Se conservan dos advertencias de deprecación de dependencias Python; no afectan la aprobación de pruebas ni del gate.
- **Próximas tareas para la siguiente sesión:**
  - Registrar/subir los cambios al GitLab institucional y comprobar `detect`, `quality`, `notify` y la calificación oficial, incluyendo los tres reportes de entrega.
  - Regenerar cobertura y repetir el verificador después de cualquier cambio de código posterior.


### Intervención de entorno de la sesión 29 — 2026-10-28
- **Objetivos de la sesión:** Atender la solicitud de restaurar la virtualización necesaria para Docker Desktop antes de continuar la implementación.
- **Tareas completadas:** Diagnóstico y restauración parcial de `TASK-32.8`. Se confirmó que `VirtualMachinePlatform` estaba deshabilitada y se habilitó con privilegios de administrador, sin reiniciar automáticamente. WSL ya estaba habilitado y el arranque del hipervisor ya figuraba en `Auto`.
- **Resultados de validación:** La reparación finalizó con `Success: true` y `RestartRequired: true`; se verificaron los estados de los componentes y la configuración de arranque. Evidencias locales en `.reports/docker-virtualization/`: estados previos/posteriores, transcripción y `result.json`. Docker no respondió correctamente antes de la reparación; su funcionamiento posterior aún no se ha validado.
- **Decisiones técnicas adoptadas:** Restaurar la Plataforma de máquina virtual requerida por WSL 2; conservar las distribuciones, los datos y la configuración restante. El resumen incorpora una tarea de recuperación de entorno; no se marcaron nuevos avances funcionales.
- **Bloqueadores / Riesgos identificados:** Windows exige reiniciar para aplicar el componente. `TASK-32.8` permanece en progreso hasta comprobar Docker después del reinicio.
- **Próximas tareas para la siguiente sesión:** Reiniciar Windows, abrir Docker Desktop y comprobar `docker version` y `docker compose ps` antes de retomar la implementación y SonarQube.

### Sesión 29 — 2026-10-28
- **Objetivos de la sesión:** Continuar implementación y obtener la máxima puntuación local de la rúbrica de SonarQube, conforme a la confirmación del usuario. Plan en [PLAN_SESION_29.md](PLAN_SESION_29.md).
- **Tareas completadas:**
  - `TASK-32.1`: auditoría de documentos, manual PDF, estado real y evidencias históricas; alcance delimitado y criterios de aceptación registrados.
  - `TASK-32.2`: verificador estricto de condiciones globales, comparadores, umbrales, incidencias y métricas válidas; errores de consulta reemplazan éxitos históricos por `cumple: false`. 34 pruebas de rúbrica/verificador aprobadas.
  - `TASK-32.3`: seis pruebas del visor doble para selección, navegación sincronizada, cierre, conservación del autor y revisión inmutable.
  - `TASK-32.4`: corrección de la actualización del dictamen humano en resultados tras guardar desde el visor; cuatro pruebas de aplicación y seis de gestión de modelos, incluidos conflictos y recuperación.
  - `TASK-32.5`: mínimos Vitest de 80% de líneas y 70% de ramas, con todo el frontend incluido; LCOV regenerado y rutas relativas verificadas.
  - `TASK-32.6`: suite completa en Docker, frontend y navegador, tipos, lint, build y nuevo análisis SonarQube con gate efectivo.
  - `TASK-32.7`: informes de calidad, plan, resumen y reportes de entrega actualizados; pipeline YAML y metadatos verificados localmente.
  - `TASK-32.8`: verificación posterior a la intervención de virtualización y al reinicio del usuario: Docker 29.7.2 operativo y servicios de calidad saludables.
- **Resultados de validación:**
  - **137 pruebas Python aprobadas** en Docker en **110,78 s**, sin omisiones, dos deprecaciones de dependencias. Backend: **90,22%** de líneas, **72,95%** de ramas, **86,87%** combinado.
  - **116 pruebas Vitest aprobadas**. Frontend completo: **86,57%** de líneas y **73,65%** de ramas; visor doble 100% de líneas, aplicación 81,13%, modelos 96,8%.
  - **4 pruebas de navegador aprobadas** en **45,8 s** con Chrome local. Tipado estricto, lint, build y `git diff --check` correctos.
  - SonarQube **Quality Gate PASSED**, **20/20 estimado localmente**, **85,0%** de cobertura global, **1,1%** de duplicación, A/A/A y **0 bugs, vulnerabilidades, code smells y hotspots**. Once condiciones evaluadas y aprobadas; ninguna ignorada.
  - Análisis `167bc699-6ae2-47fe-9a44-3975bfc14ee1`, fechado a las **20:58:23 America/Lima**; escáner finalizado a las **21:02:09**. Verificador: código 0, `cumple: true`, sin incumplimientos.
  - Reportes entregables: `.reports/coverage.xml`, `.reports/pytest.xml` y `frontend/coverage/lcov.info`. Evidencias locales detalladas en [RESULTADO_SONARQUBE.md](RESULTADO_SONARQUBE.md).
- **Decisiones técnicas adoptadas:**
  - Mantener 20/20 de la rúbrica como objetivo de nota; los mínimos adicionales de frontend detectan regresiones y no equivalen a exigir 100% de cobertura.
  - Propagar ID de correspondencia y decisión por callbacks tipados, preservando los contratos REST y la predicción original.
  - Reutilizar la imagen de pruebas con embeddings reales y ejecutar el escáner después de regenerar ambos reportes de cobertura; fuentes estables durante el análisis.
  - Usar Chrome mediante la opción ya existente `CONVCOMP_BROWSER_EXECUTABLE`, sin instalar navegadores ni modificar su configuración global.
- **Bloqueadores / Riesgos identificados:**
  - Sin bloqueadores para el cierre local. La nota oficial de Quantum permanece pendiente: el único remoto configurado es GitHub y se requiere destino/acceso al GitLab institucional. No se ejecutó su pipeline.
  - El escáner advierte de información SCM ausente en cambios sin commit; sí completó el análisis y las condiciones globales. No se alteraron commits ni se subieron cambios.
  - La validación científica con anotaciones institucionales reales y la autenticación de revisores siguen fuera de este cierre de calidad.
- **Próximas tareas para la siguiente sesión:**
  - Completar la entrega institucional cuando se facilite el repositorio GitLab y verificar sus métricas oficiales, etapas y notificación.
  - Delimitar el siguiente incremento de Fase 4 antes de implementar usuarios, autenticación, PostgreSQL o gestión documental.
  - Repetir cobertura y análisis tras cambios posteriores de código.

### Sesión 30 — 2026-10-28
- **Objetivos de la sesión:** Rediseñar la aplicación con la composición SaaS de las capturas proporcionadas por el usuario, trasladando los azules a la paleta violeta académica adjunta, y conservar la máxima puntuación local de calidad.
- **Tareas completadas:**
  - `TASK-33.1`: identidad violeta/lavanda, navegación blanca, tipografía, controles y tarjetas compartidos, favicon propio y metadatos HTML en español.
  - `TASK-33.2`: inicio con presentación del producto y panel real de evaluación. Componente reutilizable por sílabo con catálogo, metadatos, carga, estados y recuperación, conservando la API.
  - `TASK-33.3`: catálogo, resultados, auditoría, modelos y guía adaptados; vista móvil de modelos en una columna; guía con foco contenido, Escape y restauración del foco. Capturas de escritorio y móvil inspeccionadas; contraste de textos secundarios corregido.
  - `TASK-33.4`: cobertura regenerada, pruebas/tipos/lint/build aprobados, análisis SonarQube final, publicación Docker y documentación actualizada en [DISENO_WEB.md](DISENO_WEB.md) y [RESULTADO_SONARQUBE.md](RESULTADO_SONARQUBE.md).
- **Resultados de validación:**
  - **120 pruebas Vitest aprobadas**. Frontend completo: **88,86%** de líneas, **75,77%** de ramas, **87,26%** de sentencias y **78,93%** de funciones. LCOV relativo verificado.
  - **6 pruebas de navegador aprobadas en 42,7 s** con Chrome local: dos del rediseño y cuatro científicas existentes. Escritorio 1440 × 1050 y móvil 390 × 844, sin desbordamiento horizontal en las vistas comprobadas.
  - Tipado de aplicación/pruebas/navegador, lint, build y `git diff --check` correctos. Las pruebas de navegador cuentan con tipos DOM en su proyecto TypeScript.
  - SonarQube **Quality Gate PASSED**, **20/20 estimado localmente**, **85,6%** de cobertura global, **0,8%** de duplicación, A/A/A y **0 bugs, vulnerabilidades, code smells y hotspots**. Verificador con código 0, `cumple: true` y sin incumplimientos.
  - Análisis final `18cb74aa-78aa-4cac-ae4b-93d7dd9793a1`, fechado a las **23:01:22 America/Lima**; escáner finalizado a las **23:04:09**. Cobertura global de líneas **90,0%**, ramas **74,4%**; 12 524 líneas de código.
  - Web y API saludables en `http://localhost:5173`. API 3.2.1/fase 3 y catálogo HTTP 200; sin excepciones JavaScript en la comprobación de publicación.
  - Todas las fuentes Python de la API en Docker coinciden por SHA-256 con el repositorio; `pip check` sin incompatibilidades. Se preservan los volúmenes.
- **Decisiones técnicas adoptadas:**
  - Usar como referencia directa las tres imágenes adjuntas. El enlace de Dribbble devolvió HTTP 202 sin contenido en este entorno; no se atribuye su imagen a una consulta que no pudo completarse.
  - Representar capacidades reales y acciones operativas, sin añadir precios, testimonios o métricas ficticias. Mantener el descargo institucional y la geometría de las evidencias PDF.
  - Conservar estados académicos diferenciados de la marca violeta. Identificar un documento seleccionado como «Listo», sin implicar acreditación oficial.
  - No modificar el backend ni repetir su suite por un cambio de interfaz; se reutilizan XML/JUnit de las 137 pruebas de la sesión 29 sobre las mismas fuentes.
  - Actualizar las cuatro fuentes antiguas detectadas en la imagen de API mediante una capa de código sobre sus dependencias locales ya instaladas. Base anterior conservada como `convcomp-backend:runtime-session30`; procedimiento y Dockerfile temporal en `.reports/`.
- **Bloqueadores / Riesgos identificados:**
  - Sin bloqueadores locales. Se conservan las limitaciones de evaluación oficial de Quantum/GitLab y validación científica institucional.
  - Las comprobaciones visuales cubren Chrome y los tamaños indicados; no constituyen una auditoría exhaustiva de WCAG ni de todos los dispositivos.
  - El código permanece sin commit; las advertencias SCM del escáner no impidieron evaluar las condiciones globales.
- **Próximas tareas para la siguiente sesión:**
  - Recoger observaciones del usuario sobre el rediseño ya disponible en localhost:5173.
  - Completar la entrega institucional cuando se facilite su repositorio y acceso.
  - Delimitar el siguiente incremento funcional de Fase 4 y repetir los controles de calidad tras cambios posteriores.

### Sesión 31 — 2026-10-28 a 2026-10-29
- **Objetivos de la sesión:** Ampliar las funciones de comparación, prioridad elegida por el usuario, manteniendo la interfaz violeta y la máxima puntuación local de calidad.
- **Tareas completadas:**
  - `TASK-34.1`: dominio puro y contratos de lotes; de uno a cinco candidatos y presupuesto de 20 000 pares de contenidos. Ranking determinista por cobertura del objetivo, afinidad global e ID, sin sumar coberturas entre candidatos.
  - `TASK-34.2`: tres tablas SQLite aditivas, solicitud UUID idempotente, resultados insertados por candidato y cierre independiente. Relectura sin duplicados y conservación de avances ante interrupción verificadas.
  - `TASK-34.3`: API de creación, historial, consulta y exportación; versión del modelo fija por ejecución, instancia de inferencia propia y error explícito si no carga el modelo activo. Los fallos de un candidato no descartan a los demás ni reciben puntuaciones ficticias.
  - `TASK-34.4`: pestaña Por lotes, acceso desde Evaluar, selección/búsqueda, estados, ranking, informes, recuperación de solicitudes e historial. Errores al abrir un análisis visibles. Versión de aplicación/manifiestos actualizada a 3.3.0, fase 3.
  - `TASK-34.5`: suites, cobertura, tipado, lint, build, inspección visual, publicación Docker, nuevo análisis SonarQube y documentación en [COMPARACION_POR_LOTES.md](COMPARACION_POR_LOTES.md), [VALIDACION_NAVEGADOR.md](VALIDACION_NAVEGADOR.md) y [RESULTADO_SONARQUBE.md](RESULTADO_SONARQUBE.md).
- **Resultados de validación:**
  - **172 pruebas Python aprobadas en Docker en 58,59 s**, 35 nuevas, sin omisiones y con dos deprecaciones de dependencias. Backend: **90,86%** de líneas y **73,97%** de ramas; XML y JUnit regenerados.
  - **134 pruebas Vitest aprobadas**; frontend completo: **89,69%** de líneas, **76,17%** de ramas, **88,41%** de sentencias y **81,48%** de funciones. LCOV relativo regenerado, mínimos 80/70 aprobados.
  - **8 pruebas Chrome aprobadas en 1,2 min** en la ejecución final, incluidas dos de lotes con API real y datos temporales: comparación/exportación/recarga sin duplicados y resultado parcial móvil. Capturas 1440 × 1050 y 390 × 844 inspeccionadas.
  - Tipado estricto de aplicación/pruebas/navegador, lint, build y `git diff --check` correctos. El único hallazgo del primer análisis fue texto accesible explícito en etiquetas de candidatos: corregido y verificado en la ejecución final.
  - SonarQube **Quality Gate PASSED**, **20/20 estimado localmente**, **86,4%** de cobertura global, **0,7%** de duplicación, A/A/A y **0 bugs, vulnerabilidades, code smells y hotspots**. Verificador con código 0, `cumple: true` y sin incumplimientos.
  - Análisis `baa7f940-1d0e-497d-b968-9465156d0a9b`, **2026-10-29 00:01:49 America/Lima**; escáner finalizado a las **00:04:31**. Líneas **90,7%**, ramas **75,1%**, 13 206 líneas de código.
  - Web saludable en `http://localhost:5173`, API **3.3.0/fase 3**, catálogo y lotes HTTP 200. Chrome sin errores JavaScript ni desbordamiento horizontal móvil. Las 70 fuentes Python desplegadas coinciden por SHA-256 y `pip check` no encontró incompatibilidades.
- **Decisiones técnicas adoptadas:**
  - Extender la comparación existente antes de iniciar autenticación o migraciones de Fase 4. Cada resultado conserva su evidencia, informe y revisión independientes; los contadores del lote son operativos.
  - Ejecutar secuencialmente, fijar modelo/pesos/umbrales y reclamar el UUID atómicamente. Un reintento devuelve lo persistido; una solicitud cambiada con la misma clave se rechaza con 409.
  - Guardar cada avance y distinguir RUNNING/COMPLETED/PARTIAL/FAILED. RUNNING puede corresponder a una interrupción; no se promete reanudación automática. La interfaz conserva la clave en reintentos y ofrece consulta explícita.
  - Probar los flujos con bases temporales; consultar el despliegue real sin crear lotes de prueba sobre datos del usuario. La actualización de esquema es aditiva.
  - Reutilizar las dependencias locales de la imagen API mediante una capa de código, conservar la base como `convcomp-backend:runtime-session31`, reconstruir frontend y mantener los volúmenes.
- **Bloqueadores / Riesgos identificados:**
  - Sin bloqueadores locales. Las comparaciones individuales y su inclusión en el lote no son una sola transacción: una interrupción entre guardados puede dejar el análisis en el historial individual. Antes de repetir pendientes debe consultarse ese registro.
  - Ejecución síncrona sin cancelación ni reanudación automática; el límite de candidatos/pares acota el trabajo. Autenticación y validación científica con datos institucionales siguen pendientes.
  - La nota oficial de Quantum/GitLab permanece pendiente. Los cambios están sin commit y las advertencias SCM no impidieron las condiciones globales. No se subieron cambios ni se ejecutó el pipeline institucional.
- **Próximas tareas para la siguiente sesión:**
  - Recoger observaciones del usuario sobre el flujo de lotes y contrastarlo con sus documentos reales.
  - Priorizar el siguiente incremento según su uso: reanudación de trabajo pendiente, comparaciones adicionales o acceso de revisores.
  - Completar entrega institucional cuando se disponga de destino y acceso; regenerar cobertura y repetir análisis tras cualquier cambio de código.
