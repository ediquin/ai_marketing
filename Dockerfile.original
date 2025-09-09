# Dockerfile para deployment en plataformas cloud gratuitas
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements específicos para cloud
COPY requirements-cloud.txt .
RUN pip install --no-cache-dir -r requirements-cloud.txt

# Copiar código fuente
COPY src/ ./src/
COPY streamlit_cloud.py .

# Crear directorio .streamlit y configuración
RUN mkdir -p .streamlit
RUN echo '[global]\ndevelopmentMode = false\n\n[server]\nport = 8501\nenableCORS = false\nenableXsrfProtection = false\nmaxUploadSize = 200\n\n[browser]\ngatherUsageStats = false\n\n[theme]\nprimaryColor = "#1f77b4"\nbackgroundColor = "#ffffff"\nsecondaryBackgroundColor = "#f0f2f6"\ntextColor = "#262730"' > .streamlit/config.toml

# Crear directorio para logs
RUN mkdir -p logs

# Variables de entorno por defecto
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Exponer puerto
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando de inicio
CMD ["streamlit", "run", "streamlit_cloud.py", "--server.port=8501", "--server.address=0.0.0.0"]
