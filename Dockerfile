# Lightweight Dockerfile for Railway (<4GB) without RAG
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps kept minimal
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install only lite requirements
COPY requirements-lite.txt ./
RUN pip install --upgrade pip && pip install -r requirements-lite.txt

# Copy src as a package and install as module
COPY src ./src
COPY setup.py ./setup.py
COPY run_streamlit_optimized.py ./run_streamlit_optimized.py
COPY README.md ./README.md

# Install the package to fix import issues
RUN pip install -e .

# Default Streamlit config for cloud
ENV STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false \
    PORT=8080

EXPOSE $PORT

# Debug startup and run Streamlit
CMD ["sh", "-c", "echo 'Starting on port:' $PORT && echo 'Python path:' && python -c 'import sys; print(sys.path)' && echo 'Testing streamlit import...' && python -c 'import streamlit; print(\"Streamlit OK\")' && echo 'Starting Streamlit...' && streamlit run src/streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true --logger.level=debug"]
