"""
Script de inicio para el backend de ConvComp.
"""

import sys
import os

# Asegurar que el directorio backend esté en sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print(" ConvComp Backend API - Fase 1")
    print(" Documentación Swagger: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, app_dir=backend_dir)