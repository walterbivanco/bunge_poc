#!/bin/bash
# Script mejorado para iniciar el chatbot

echo "🚀 Iniciando Chatbot NL → SQL"
echo "=============================="
echo ""

# Activar virtualenv
source env/bin/activate

# Corregir VIRTUAL_ENV si tiene ruta incorrecta
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export VIRTUAL_ENV="$SCRIPT_DIR/env"

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

# Verificar tablas de dimensiones (silenciosamente)
echo "🔍 Verificando tablas de dimensiones..."
cd backend
# Redirigir stderr a /dev/null para silenciar warnings y logs
python3 << 'PYTHON_EOF' 2>/dev/null
import os
import sys
import logging
import warnings

# Silenciar warnings y logs
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'
logging.basicConfig(level=logging.CRITICAL)

sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv('../.env')

try:
    from app.db import get_dimensions_info, clear_dimensions_cache
    
    # Temporalmente silenciar el logger
    import app.logger
    app.logger.logger.setLevel(logging.CRITICAL)
    
    # Limpiar cache para verificación fresca
    clear_dimensions_cache()
    dimensions_info = get_dimensions_info(force_refresh=True)
    
    if dimensions_info.get('dimensions') and len(dimensions_info['dimensions']) > 0:
        dim_names = list(dimensions_info['dimensions'].keys())
        print(f"  ✅ Tablas disponibles: {', '.join(dim_names)}")
        print("  ✅ El sistema puede generar JOINs con estas tablas")
    else:
        print("  ⚠️  No se encontraron tablas de dimensiones")
        print("     El sistema funcionará solo con la tabla principal (sin JOINs)")
except Exception as e:
    error_msg = str(e)[:60]
    print(f"  ⚠️  Error verificando: {error_msg}...")
PYTHON_EOF
cd ..
echo ""

# Iniciar servidor
echo "🌐 Servidor iniciando en http://localhost:8080"
echo ""
echo "💡 Ejemplos de preguntas que puedes hacer:"
echo "   - List contracts grouped by province name"
echo "   - Show me contracts with product names"
echo "   - Contracts grouped by month and year"
echo "   - Total quantity by product name"
echo "   - Contracts by province and product category"
echo ""
echo "⏹  Para detener: Ctrl+C"
echo ""
echo "=============================="
echo ""

cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

