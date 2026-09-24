# ConvComp — Sistema de Comparación Inteligente y Pre-Evaluación de Sílabos (Fase 1)

Sistema de análisis computacional de correspondencia temática entre sílabos universitarios basado en Arquitectura Limpia (Clean Architecture), procesamiento de lenguaje natural (NLP) híbrido auditable y supervisión humana con inmutabilidad de predicciones.

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

## 🔬 2. Algoritmo de Correspondencia Explicable (Fase 1)

El motor de comparación no utiliza modelos generativos de "caja negra" como evaluadores. Emplea un pipeline reproducible y auditable:

1. **Ingestión Digital Segura:** PyMuPDF extrae texto digital con tracking estricto de números de página física (1-indexed) y hash SHA-256. Rechaza documentos escaneados sin texto informando que OCR es alcance de Fase 2.
2. **Normalización Técnica Especializada:** Preserva símbolos técnicos de programación y bases de datos (`c++` $\rightarrow$ `cpp`, `b+` $\rightarrow$ `bplus`, `.net` $\rightarrow$ `dotnet`, `3fn`).
3. **Representación Vectorial Híbrida:**
   - **Léxica:** TF-IDF con unigramas y bigramas ($w_{lex} = 0.30$).
   - **Semántica:** Sentence Transformers con embeddings densos multilingües y fallback determinista ($w_{sem} = 0.40$).
   - **Solapamiento Clave:** Coeficiente de Jaccard sobre términos técnicos extraídos ($w_{key} = 0.15$).
   - **Estructural:** Proximidad de orden y tipología de sección ($w_{est} = 0.15$).
4. **Fórmula de Scoring Compuesto:**
   $$\text{Score} = 0.40 \cdot S_{sem} + 0.30 \cdot S_{lex} + 0.15 \cdot S_{key} + 0.15 \cdot S_{est}$$
5. **Umbrales Categoriales:**
   - $\ge 0.85$: `MATCH` (Verde)
   - $0.70 - 0.84$: `PARTIAL_MATCH` (Ámbar)
   - $0.50 - 0.69$: `UNCERTAIN` (Azul)
   - $< 0.50$: `NO_MATCH` (Rojo / Brecha)
6. **Métricas Bidireccionales:**
   - $S_{obj} \rightarrow S_{cmp}$: Cobertura de las exigencias del curso requerido.
   - $S_{cmp} \rightarrow S_{obj}$: Cobertura de los temas cursados por el postulante.

---

## 🛡️ 3. Principio de Inmutabilidad y Aprendizaje Continuo

- **Inmutabilidad Absoluta:** Las revisiones académicas humanas (`reviews`) **NUNCA** sobrescriben las puntuaciones ni las clasificaciones generadas por la máquina en `content_matches`. Coexisten en tablas separadas.
- **Dataset Staging:** Cada revisión genera automáticamente un registro en `dataset_examples` con los textos originales, los vectores de características y la etiqueta de decisión humana para calibración y entrenamiento supervisado en Fase 2.

---

## 🚀 4. Guía de Ejecución Local

### Prerrequisitos
- Python 3.12+
- Node.js 18+ y npm

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

---

## 🧪 5. Ejecución de la Suite de Pruebas

Para ejecutar las 28 pruebas automatizadas (unitarias, integración y end-to-end):

```bash
# Desde la raíz del repositorio con el venv activado:
.venv\Scripts\python -m pytest tests/ -v
```

Cobertura verificada:
- **Unitarias:** Dominio puro, invariantes de páginas, normalización de acentos y símbolos (`c++`, `b+`), segmentación heurística de sílabos, cálculo de similitud híbrida.
- **Integración:** Repositorios SQLite, inmutabilidad de reviews, endpoints REST, generador de informes HTML y PDF (ReportLab).
- **End-to-End:** Ciclo de vida completo: Subida $\rightarrow$ Segmentación $\rightarrow$ Comparación $\rightarrow$ Reportes $\rightarrow$ Auditoría Humana $\rightarrow$ Dataset exportable.