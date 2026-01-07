#!/bin/bash
# Script mejorado para iniciar el chatbot

echo "🚀 Iniciando Chatbot NL → SQL"
echo "=============================="
echo ""

# Activar virtualenv
source env/bin/activate

# Verificar .env
if [ ! -f .env ]; then
    echo "❌ Error: No existe archivo .env"
    exit 1
fi

# Mostrar configuración
echo "📋 Configuración:"
source .env
echo "  PROJECT_ID: $PROJECT_ID"
echo "  BQ_DATASET: $BQ_DATASET"
echo "  BQ_TABLE: $BQ_TABLE"
echo "  GEMINI_MODEL: $GEMINI_MODEL"
echo ""

# Iniciar servidor
echo "🌐 Servidor iniciando en http://localhost:8080"
echo ""
echo "💡 Ejemplos de preguntas que puedes hacer:"
echo "   - ¿Cuántos contratos hay por estado?"
echo "   - Muéstrame los últimos 10 contratos"
echo "   - Contratos de SOJA en 2025"
echo "   - ¿Cuál es el precio promedio por producto?"
echo ""
echo "⏹  Para detener: Ctrl+C"
echo ""
echo "=============================="
echo ""

cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

