#!/bin/bash
# Script de deployment a Google Cloud Run

set -e

echo "🚀 Iniciando deployment a Google Cloud Run..."

# Cargar variables de entorno
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ Error: Archivo .env no encontrado. Copia .env.example a .env y configura tus variables."
    exit 1
fi

# Verificar que PROJECT_ID esté configurado
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: PROJECT_ID no está configurado en .env"
    exit 1
fi

echo "📦 Proyecto: $PROJECT_ID"
echo "🌎 Región: ${VERTEX_LOCATION:-us-central1}"

# Build de la imagen Docker
echo "🔨 Construyendo imagen Docker..."
docker build -t gcr.io/$PROJECT_ID/nl2sql-poc:latest ./backend

# Push a Google Container Registry
echo "📤 Subiendo imagen a GCR..."
docker push gcr.io/$PROJECT_ID/nl2sql-poc:latest

# Deploy a Cloud Run
echo "🚢 Desplegando a Cloud Run..."
gcloud run deploy nl2sql-poc \
    --image gcr.io/$PROJECT_ID/nl2sql-poc:latest \
    --region ${VERTEX_LOCATION:-us-central1} \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "PROJECT_ID=$PROJECT_ID,BQ_DATASET=$BQ_DATASET,BQ_TABLE=$BQ_TABLE,VERTEX_LOCATION=$VERTEX_LOCATION,GEMINI_MODEL=$GEMINI_MODEL"

echo "✅ Deployment completado!"
echo "🌐 Tu aplicación está disponible en la URL proporcionada por Cloud Run"

