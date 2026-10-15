# ConvComp — Sistema de Comparación Inteligente y Pre-Evaluación de Sílabos (Fase 3)

Sistema de análisis computacional de correspondencia temática entre sílabos universitarios basado en Arquitectura Limpia (Clean Architecture), procesamiento de lenguaje natural (NLP) híbrido auditable y supervisión humana con inmutabilidad de predicciones.

Versión de aplicación: **3.2.1**. Incluye comparación explicable (1.0), visor doble con evidencias (1.5), OCR y aprendizaje supervisado (2.0), consolidación de evaluación por grupos académicos (2.1), ground truth y acuerdo interevaluador (3.0), cola de revisión con lotes de aprendizaje activo (3.1) y experimentos reproducibles sobre comparaciones completas reservadas (3.2). El alcance de desarrollo planificado de Fase 3 está implementado; la validación con anotaciones institucionales reales sigue pendiente. El avance se registra en [docs/TASKS.md](docs/TASKS.md).

---

> ### ⚠️ NOTA FORMAL Y EXENCIÓN DE RESPONSABILIDAD INSTITUCIONAL
> El presente software es una **herramienta de pre-evaluación y apoyo técnico** para comisiones y evaluadores académicos. **No sustituye, invalida ni constituye la decisión final de convalidación académica**, la cual compete de forma exclusiva y soberana a las autoridades universitarias competentes.

---

## 🏛️ 1. Arquitectura del Sistema

El proyecto sigue un enfoque de **Monolito Modular con Clean Architecture**:

```
conv_comp/
├── backend/
│   ├── app/
│   │   ├── domain/               # Entidades puras y puertos (Syllabus, Comparison, Review)
│   │   ├── application/          # Casos de uso (ProcessSyllabus, CompareSyllabi)
│   │   ├── infrastructure/       # PyMuPDF, Normalizador, TF-IDF + SentenceTransformers, SQLite, ReportLab
│   │   └── api/                  # FastAPI routers, esquemas Pydantic y CORS
│   └── requirements.txt
├── frontend/                     # React + TypeScript + Vite + Dark Academic Design System
│   ├── src/
│   │   ├── components/           # Header, SyllabusUploader, ComparisonScore, MatchTable, EvidencePanel, UnmatchedPanel, ReviewModal, AuditDatasetView, Dashboard
│   │   ├── services/api.ts       # Cliente API REST tipado
│   │   └── types/                # Contratos estrictos sincronizados con el backend
├── tests/
│   ├── unit/                     # Pruebas unitarias de dominio, NLP, extracción y normalización
│   └── integration/              # Pruebas de repositorios SQLite, endpoints REST, reportes y flujo E2E
└── docs/
    ├── FLUJO_FASE_1.md           # Especificación arquitectónica y contratos REST
    ├── REGLAS_IMPLEMENTACION.md  # Reglas de desarrollo, inmutabilidad y auditoría
    └── TASKS.md                  # Registro granular de tareas y bitácora de sesiones
```

---

## 🔬 2. Algoritmo de Correspondencia Explicable

El motor de comparación no utiliza modelos generativos de "caja negra" como evaluadores. Emplea un pipeline reproducible y auditable:

1. **Ingestión Digital y OCR:** PyMuPDF extrae texto digital con números de página física (1-indexed) y hash SHA-256. RapidOCR/ONNX procesa documentos escaneados y conserva coordenadas para el visor de evidencias. Los documentos ilegibles o vacíos se rechazan.
2. **Normalización Técnica Especializada:** Preserva símbolos técnicos de programación y bases de datos (`c++` $\rightarrow$ `cpp`, `b+` $\rightarrow$ `bplus`, `.net` $\rightarrow$ `dotnet`, `3fn`).
3. **Representación Vectorial Híbrida:**
   - **Léxica:** TF-IDF con unigramas y bigramas ($w_{lex} = 0.30$).
   - **Semántica:** Sentence Transformers con embeddings densos multilingües y fallback determinista ($w_{sem} = 0.45$).
   - **Solapamiento Clave:** Coeficiente de Jaccard sobre términos técnicos extraídos ($w_{key} = 0.15$).
   - **Estructural:** Proximidad de orden y tipología de sección ($w_{est} = 0.10$).
4. **Fórmula de Scoring Compuesto:**
   $$\text{Score}_{base} = 0.45 \cdot S_{sem} + 0.30 \cdot S_{lex} + 0.15 \cdot S_{key} + 0.10 \cdot S_{est}$$
   Los pesos se ajustan según la afinidad conceptual y se aplican pisos de correspondencia ante similitud alta. El motor incorpora contención direccional, descomposición por frases y asignación bipartita; cada resultado conserva su desglose.
5. **Umbrales Categoriales:**
   - $\ge 0.75$: `MATCH` (Verde)
   - $0.58 \le S < 0.75$: `PARTIAL_MATCH` (Ámbar)
   - $0.45 \le S < 0.58$: `UNCERTAIN` (Azul)
   - $< 0.45$: `NO_MATCH` (Rojo / Brecha)
   `MATCH` y `PARTIAL_MATCH` requieren además afinidad de contenido.
6. **Métricas Bidireccionales:**
   - $S_{obj} \rightarrow S_{cmp}$: Cobertura de las exigencias del curso requerido.
   - $S_{cmp} \rightarrow S_{obj}$: Cobertura de los temas cursados por el postulante.

---

## 🛡️ 3. Principio de Inmutabilidad y Aprendizaje Continuo

- **Inmutabilidad Absoluta:** Las revisiones académicas humanas (`reviews`) **NUNCA** sobrescriben las puntuaciones ni las clasificaciones generadas por la máquina en `content_matches`. Coexisten en tablas separadas.
- **Dataset Staging:** Cada revisión genera un registro con textos, características, decisión humana y procedencia académica; se exporta en JSON/CSV.
- **Aprendizaje supervisado:** Regresión logística calibrada o Random Forest, versionado y activación desde la pestaña Modelos IA.
- **Evaluación por grupos:** Las fuentes relacionadas por sílabo, contenido o universidad/asignatura permanecen juntas. La evaluación reserva grupos (25% solicitado por defecto); la proporción efectiva depende del tamaño de los grupos. La calibración también respeta los grupos cuando hay suficientes datos.
- **Bootstrap:** Con menos de 20 revisiones se pueden añadir ejemplos sintéticos al entrenamiento. Si hay revisiones reales, el conjunto de evaluación contiene únicamente datos humanos. Sin grupos o clases suficientes se rechaza el entrenamiento con un mensaje explicativo. Una evaluación exclusivamente sintética se identifica como tal y no permite activación automática.
- **Benchmark:** El modelo y el scoring adaptativo comparten muestras de evaluación y reglas del dominio. La comparativa mide clasificación de pares de contenidos; la selección de candidatos, la asignación global y las coberturas completas requieren experimentos independientes. `UNCERTAIN` se agrupa con `PARTIAL_MATCH` para compararse con las tres clases del modelo supervisado. El baseline disponible en la API no anuncia métricas hasta que exista una evaluación registrada.
- **Ground truth y acuerdo:** Auditoría muestra pares con revisión única, acuerdo o desacuerdo. Se conserva un voto vigente por identificador de revisor y el historial completo de eventos. El acuerdo entre cada pareja de revisores incluye muestra, acuerdo observado y kappa nominal de Cohen; los casos indeterminados se muestran como no calculables. La autenticación de autores pertenece a Fase 4.
- **Entrenamiento consensuado:** El panel propone usar solo pares acordados por al menos dos revisores. Las revisiones individuales siguen disponibles como política explícita; la API conserva esa política por defecto para clientes existentes. Las métricas guardan la política y los IDs de revisiones fuente. Si hay revisiones sin consenso, esta política rechaza el entrenamiento en lugar de reemplazarlas silenciosamente por sintéticos. Los enlaces manuales sin características requieren procesamiento antes de entrenar. Ver [FLUJO_FASE_3.md](docs/FLUJO_FASE_3.md).
- **Aprendizaje activo:** Auditoría prioriza desacuerdos, segundas revisiones y pares sin revisar; usa clasificación incierta y cercanía a umbrales de referencia para ordenar cada grupo. Los lotes conservan su selección, autor, estrategia, umbrales y cobertura inicial; su cierre guarda una medición independiente e inmutable. La cobertura mide anotación de pares propuestos, no cobertura curricular ni mejora demostrada del modelo. Revisar casos no reentrena ni activa modelos.

---

## 🚀 4. Guía de Ejecución Local

### Prerrequisitos
- Python 3.11+
- Node.js 20.19+ (rama 20) o 22.12+ y npm, según los requisitos de Vite

### A. Backend (FastAPI)
```bash
# 1. Crear entorno virtual (si no existe) y activar
python -m venv .venv
.venv\Scripts\activate      # En Windows

# 2. Instalar dependencias
pip install -r backend/requirements.txt

# 3. Iniciar servidor FastAPI
python backend/run.py
# O alternativamente:
# uvicorn app.main:app --app-dir backend --reload --port 8000
```
La API estará disponible en `http://localhost:8000`. Documentación interactiva Swagger: `http://localhost:8000/docs`.

### B. Frontend (React + Vite)
```bash
# 1. Ingresar al directorio del frontend
cd frontend

# 2. Instalar dependencias
npm install

# 3. Iniciar servidor de desarrollo
npm run dev
```
La aplicación web estará disponible en `http://localhost:5173`.

En PowerShell, si la política de scripts impide ejecutar `npm`, use `npm.cmd`.

### C. Almacenamiento independiente

`CONVCOMP_DATA_DIR` cambia el directorio del backend que contiene `convcomp.db`, `uploads/` y `models/` (por defecto `backend/data`). `CONVCOMP_REPORTS_DIR` cambia el directorio de reportes (por defecto `data/reports`, relativo al directorio de ejecución).

`GET /api/health` devuelve versión `3.2.1` y fase `3`; OpenAPI informa la misma versión. El protocolo de experimentos se describe en [docs/EXPERIMENTOS_FASE_3.md](docs/EXPERIMENTOS_FASE_3.md). Las pruebas integradas de Chromium se ejecutan desde `frontend` con `npm.cmd run test:browser`; consulte [docs/VALIDACION_NAVEGADOR.md](docs/VALIDACION_NAVEGADOR.md).

---

## 🧪 5. Ejecución de la Suite de Pruebas

Para ejecutar la suite de pruebas unitarias, integración y end-to-end:

```bash
# Desde la raíz del repositorio con el venv activado:
.venv\Scripts\python -m pytest tests/ -v
```

Las pruebas configuran almacenamiento temporal antes de importar la API y usan una base nueva por prueba. Las cargas, los reportes y los modelos de prueba se guardan en directorios temporales.

Cobertura:
- **Unitarias:** Dominio puro, invariantes de páginas, normalización de acentos y símbolos (`c++`, `b+`), segmentación heurística de sílabos, cálculo de similitud híbrida.
- **Integración:** Repositorios SQLite, inmutabilidad de reviews, endpoints REST, generador de informes HTML y PDF (ReportLab).
- **End-to-End:** Ciclo de vida completo: Subida $\rightarrow$ Segmentación $\rightarrow$ Comparación $\rightarrow$ Reportes $\rightarrow$ Auditoría Humana $\rightarrow$ Dataset exportable.
- **OCR y ML:** Texto y coordenadas OCR, entrenamiento e inferencia, ciclo de modelos, aislamiento y separación de grupos académicos sin bootstrap en la evaluación real.
