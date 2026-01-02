#!/bin/bash
# Script para configurar el proyecto en Google Cloud Platform

set -e

echo "🔧 Configuración inicial de Google Cloud Platform"
echo ""

# Verificar que gcloud esté instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI no está instalado."
    echo "Instálalo desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Solicitar PROJECT_ID si no está configurado
read -p "📦 Ingresa tu PROJECT_ID de GCP: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo "❌ PROJECT_ID es requerido"
    exit 1
fi

echo ""
echo "🔐 Configurando proyecto: $PROJECT_ID"
gcloud config set project $PROJECT_ID

echo ""
echo "🔌 Habilitando APIs necesarias..."
gcloud services enable \
    aiplatform.googleapis.com \
    bigquery.googleapis.com \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com

echo ""
echo "✅ APIs habilitadas correctamente"

echo ""
echo "📝 Creando archivo .env..."
cat > .env << EOF
# Variables de entorno - Google Cloud
PROJECT_ID=$PROJECT_ID
BQ_DATASET=demo
BQ_TABLE=ventas
VERTEX_LOCATION=us-central1
GEMINI_MODEL=gemini-1.5-flash
EOF

echo "✅ Archivo .env creado"
echo ""
echo "🎉 Configuración completada!"
echo ""
echo "Próximos pasos:"
echo "1. Edita el archivo .env con tus valores específicos"
echo "2. Crea tu tabla en BigQuery"
echo "3. Ejecuta ./deploy.sh para deployar la aplicación"

