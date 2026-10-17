# syntax=docker/dockerfile:1
FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    CONVCOMP_DATA_DIR=/var/lib/convcomp/data \
    CONVCOMP_REPORTS_DIR=/var/lib/convcomp/reports \
    HF_HOME=/var/cache/convcomp/huggingface

# OpenCV/RapidOCR necesitan estas bibliotecas incluso sin interfaz gráfica.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
# La aplicación usa inferencia CPU; evitar descargar bibliotecas CUDA.
RUN python -m pip install torch --index-url https://download.pytorch.org/whl/cpu \
    && python -m pip install -r requirements.txt

RUN groupadd --gid 10001 convcomp \
    && useradd --uid 10001 --gid convcomp --create-home convcomp \
    && mkdir -p /var/lib/convcomp/data /var/lib/convcomp/reports "$HF_HOME" \
    && chown -R convcomp:convcomp /var/lib/convcomp /var/cache/convcomp

COPY --chown=convcomp:convcomp backend/app ./app
USER convcomp
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)" || exit 1
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

FROM runtime AS test
USER root
COPY backend/requirements-dev.txt ./requirements-dev.txt
RUN python -m pip install -r requirements-dev.txt
# La prueba de paráfrasis requiere embeddings reales, incluso al ejecutar offline.
# Descargar solo en esta etapa; la imagen de producción conserva su caché propia.
ENV HF_HOME=/opt/huggingface
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"
WORKDIR /workspace
COPY --chown=convcomp:convcomp backend/app ./backend/app
COPY --chown=convcomp:convcomp tests ./tests
COPY --chown=convcomp:convcomp .coveragerc ./.coveragerc
RUN chown convcomp:convcomp /workspace
ENV PYTHONPATH=/workspace/backend \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1
USER convcomp
HEALTHCHECK NONE
CMD ["python", "-m", "pytest", "tests", "--cov", "--cov-report=term-missing", "--cov-report=xml:.reports/coverage.xml", "--junitxml=.reports/pytest.xml"]

# La construcción sin --target produce siempre la imagen de la API.
FROM runtime AS production

