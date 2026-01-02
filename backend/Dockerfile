# Dockerfile optimizado para Cloud Run

FROM python:3.11-slim

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY ./app ./app

# Copiar frontend (servido desde el backend)
COPY ../frontend ./frontend

# Puerto por defecto de Cloud Run
ENV PORT=8080

# Exponer puerto
EXPOSE 8080

# Usuario no-root para seguridad
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Comando para iniciar la aplicación
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
