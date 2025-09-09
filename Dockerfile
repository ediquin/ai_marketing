FROM python:3.10-slim

# Evita que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Evita el buffering de stdout/stderr
ENV PYTHONUNBUFFERED=1

# Configuración de Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar solo los archivos necesarios
COPY requirements-lite.txt .
COPY src/ ./src/
COPY streamlit_cloud.py .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements-lite.txt

# Crear directorio .streamlit y configurar
RUN mkdir -p .streamlit
RUN echo '[global]\n\
[server]\nport = 8501\nheadless = true\n\n[browser]\ngatherUsageStats = false\n' > .streamlit/config.toml

# Puerto expuesto
EXPOSE 8501

# Comando de inicio
CMD ["streamlit", "run", "streamlit_cloud.py"]
