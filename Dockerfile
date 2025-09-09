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

# Ensure Python can import /app/src as package 'src'
ENV PYTHONPATH=/app

WORKDIR /app

# Install only lite requirements
COPY requirements-lite.txt ./
RUN pip install --upgrade pip && pip install -r requirements-lite.txt

# Copy setup.py first and install package in editable mode
COPY setup.py ./setup.py
COPY src ./src
RUN pip install -e . --verbose

# Verify package installation
RUN python -c "import sys; print('Python path:', sys.path)"
RUN python -c "import src; print('src module found at:', src.__file__)"

# Copy remaining files
COPY streamlit_config.toml ./.streamlit/config.toml
COPY run_streamlit_optimized.py ./run_streamlit_optimized.py

# Ensure .streamlit directory exists
RUN mkdir -p .streamlit

EXPOSE 8080

# Debug startup - verify module availability before starting Streamlit
CMD ["sh", "-c", "echo 'Starting Streamlit on port:' $PORT && echo 'Python path:' && python -c 'import sys; print(sys.path)' && echo 'Testing src import:' && python -c 'import src; print(\"src imported successfully from:\", src.__file__)' && echo 'Checking src/models directory:' && ls -la /app/src/models/ && echo 'Testing src.models import:' && python -c 'import src.models; print(\"src.models imported successfully\")' && streamlit run src/streamlit_app.py --server.port=$PORT"]
