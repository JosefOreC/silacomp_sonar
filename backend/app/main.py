"""
Punto de entrada principal de la aplicación FastAPI (ConvComp).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.comparison_router import router as comparison_router
from app.api.dataset_router import router as dataset_router
from app.api.model_router import router as model_router
from app.api.review_router import router as review_router
from app.api.syllabus_router import router as syllabus_router
from app.infrastructure.persistence.database import DatabaseManager

app = FastAPI(
    title="ConvComp API — Sistema Inteligente de Comparación de Sílabos",
    version="2.0.0",
    description="Motor de pre-evaluación computacional explicable de correspondencia académica entre sílabos universitarios con soporte OCR y Aprendizaje Supervisado.",
)

# Configuración de CORS para desarrollo web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar esquema de persistencia al arrancar
DatabaseManager()

# Registrar Routers
app.include_router(syllabus_router, prefix="/api")
app.include_router(comparison_router, prefix="/api")
app.include_router(review_router, prefix="/api")
app.include_router(dataset_router, prefix="/api")
app.include_router(model_router, prefix="/api")


@app.get("/api/health")
def health_check():
    """Endpoint de estado del servicio."""
    return {
        "status": "healthy",
        "service": "ConvComp API",
        "version": "1.0.0",
        "phase": 1,
    }
