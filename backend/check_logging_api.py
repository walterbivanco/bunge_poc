#!/usr/bin/env python3
"""
Script para verificar si Google Cloud Logging API está habilitado
"""
import os
import sys

def check_logging_api():
    """Verifica si Cloud Logging API está habilitado"""
    project_id = os.getenv("PROJECT_ID")
    
    if not project_id:
        print("❌ PROJECT_ID no está configurado en las variables de entorno")
        return False
    
    print(f"🔍 Verificando Cloud Logging API para proyecto: {project_id}")
    print("=" * 60)
    
    # Verificar si el módulo está instalado
    try:
        import google.cloud.logging as cloud_logging
        from google.api_core import exceptions
    except ImportError:
        print("❌ google-cloud-logging no está instalado")
        print("   Ejecuta: pip install google-cloud-logging")
        print("\n📋 Información para RSE:")
        print("   Nombre del servicio: Cloud Logging API")
        print("   Nombre de la API: logging.googleapis.com")
        return False
    
    try:
        # Intentar crear un cliente de Cloud Logging
        print("✅ Intentando inicializar cliente de Cloud Logging...")
        client = cloud_logging.Client(project=project_id)
        
        # Intentar configurar logging (esto requiere API habilitada)
        try:
            client.setup_logging()
            print("✅ Cloud Logging API está HABILITADA")
            print("✅ Cliente inicializado correctamente")
            print("✅ Los logs se enviarán automáticamente a Google Cloud Logging")
            return True
        except exceptions.PermissionDenied as e:
            print("❌ Cloud Logging API NO está habilitada o no tienes permisos")
            print(f"   Error: {str(e)}")
            print("\n📋 Para habilitar la API, RSE debe ejecutar:")
            print(f"   gcloud services enable logging.googleapis.com --project={project_id}")
            return False
        except Exception as e:
            # Otros errores pueden ser de permisos o configuración
            error_str = str(e).lower()
            if "not enabled" in error_str or "not found" in error_str or "403" in error_str:
                print("❌ Cloud Logging API NO está habilitada")
                print(f"   Error: {str(e)}")
                print("\n📋 Para habilitar la API, RSE debe ejecutar:")
                print(f"   gcloud services enable logging.googleapis.com --project={project_id}")
            else:
                print(f"⚠️  Error inesperado: {str(e)}")
                print("   Esto podría indicar que la API no está habilitada o hay problemas de permisos")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando API: {str(e)}")
        return False

if __name__ == "__main__":
    # Cargar variables de entorno
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv no está instalado, usando variables de entorno del sistema")
    
    result = check_logging_api()
    
    print("\n" + "=" * 60)
    print("📝 Información para RSE:")
    print("   Nombre del servicio: Cloud Logging API")
    print("   Nombre de la API: logging.googleapis.com")
    project_id = os.getenv("PROJECT_ID", "<PROJECT_ID>")
    print(f"   Comando para habilitar:")
    print(f"   gcloud services enable logging.googleapis.com --project={project_id}")
    print("\n📄 Ver más detalles en: GOOGLE_CLOUD_LOGGING.md")
    
    sys.exit(0 if result else 1)
