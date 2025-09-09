# Lightweight Dockerfile for Railway (<4GB) without RAG - Force rebuild v2
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
COPY streamlit_config.toml ./.streamlit/config.toml
COPY run_streamlit_optimized.py ./run_streamlit_optimized.py
COPY README.md ./README.md

# Create .streamlit directory and install package
RUN mkdir -p .streamlit && pip install -e .

EXPOSE 8080

# Simple startup with config file
CMD ["sh", "-c", "echo 'Starting Streamlit on port:' $PORT && streamlit run src/streamlit_app.py --server.port=$PORT"]
