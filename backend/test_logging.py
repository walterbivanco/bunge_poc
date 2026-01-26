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
print("🧪 Logging Test")
print("=" * 60)

# Importar el módulo de logging (esto es lo que hace la app al iniciar)
try:
    from app.logger import logger, log_info, log_warning, log_error
    print("✅ Logger module imported successfully")
except Exception as e:
    print(f"❌ Error importing logger: {e}")
    sys.exit(1)

print("\n📝 Testing different log levels:")
print("-" * 60)

# Probar diferentes tipos de logs
log_info("This is an info message")
log_warning("This is a warning message")
log_error("This is an error message (simulated)")

# Probar logger directamente
logger.info("Direct log with logger.info()")
logger.debug("Debug log (should not appear if level=INFO)")

print("\n" + "=" * 60)
print("✅ Test completed")
print("=" * 60)
print("\n📋 Verification:")
print("   1. ✅ If you see the messages above → Local logging works")
print("   2. ✅ If there are no errors → Code correctly handles absence of Cloud Logging")
print("   3. 📄 Check chatbot.log to see logs saved to file")
print("\n💡 If Cloud Logging API is enabled, you will also see:")
print("   '✅ Google Cloud Logging enabled - Logs will be sent to GCP'")
