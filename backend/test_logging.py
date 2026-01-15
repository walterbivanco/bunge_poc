#!/usr/bin/env python3
"""
Script de prueba para verificar que el logging funciona correctamente
incluso si Google Cloud Logging API no está habilitada
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("=" * 60)
print("🧪 Prueba de Logging")
print("=" * 60)

# Importar el módulo de logging (esto es lo que hace la app al iniciar)
try:
    from app.logger import logger, log_info, log_warning, log_error
    print("✅ Módulo logger importado correctamente")
except Exception as e:
    print(f"❌ Error importando logger: {e}")
    sys.exit(1)

print("\n📝 Probando diferentes niveles de log:")
print("-" * 60)

# Probar diferentes tipos de logs
log_info("Este es un mensaje de información")
log_warning("Este es un mensaje de advertencia")
log_error("Este es un mensaje de error (simulado)")

# Probar logger directamente
logger.info("Log directo con logger.info()")
logger.debug("Log de debug (no debería aparecer si level=INFO)")

print("\n" + "=" * 60)
print("✅ Prueba completada")
print("=" * 60)
print("\n📋 Verificación:")
print("   1. ✅ Si ves los mensajes arriba → Logging local funciona")
print("   2. ✅ Si no hay errores → El código maneja correctamente la ausencia de Cloud Logging")
print("   3. 📄 Revisa chatbot.log para ver los logs guardados en archivo")
print("\n💡 Si la API de Cloud Logging está habilitada, también verás:")
print("   '✅ Google Cloud Logging habilitado - Los logs se enviarán a GCP'")
