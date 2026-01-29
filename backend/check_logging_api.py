#!/usr/bin/env python3
"""
Script to verify if Google Cloud Logging API is enabled.
"""
import os
import sys

def check_logging_api():
    """Verifica si Cloud Logging API está habilitado"""
    project_id = os.getenv("PROJECT_ID")
    
    if not project_id:
        print("❌ PROJECT_ID is not configured in environment variables")
        return False
    
    print(f"🔍 Checking Cloud Logging API for project: {project_id}")
    print("=" * 60)
    
    # Verificar si el módulo está instalado
    try:
        import google.cloud.logging as cloud_logging
        from google.api_core import exceptions
    except ImportError:
        print("❌ google-cloud-logging is not installed")
        print("   Run: pip install google-cloud-logging")
        print("\n📋 Information for RSE:")
        print("   Service name: Cloud Logging API")
        print("   API name: logging.googleapis.com")
        return False
    
    try:
        # Intentar crear un cliente de Cloud Logging
        print("✅ Attempting to initialize Cloud Logging client...")
        client = cloud_logging.Client(project=project_id)
        
        # Intentar configurar logging (esto requiere API habilitada)
        try:
            client.setup_logging()
            print("✅ Cloud Logging API is ENABLED")
            print("✅ Client initialized successfully")
            print("✅ Logs will be automatically sent to Google Cloud Logging")
            return True
        except exceptions.PermissionDenied as e:
            print("❌ Cloud Logging API is NOT enabled or you don't have permissions")
            print(f"   Error: {str(e)}")
            print("\n📋 To enable the API, RSE must run:")
            print(f"   gcloud services enable logging.googleapis.com --project={project_id}")
            return False
        except Exception as e:
            # Otros errores pueden ser de permisos o configuración
            error_str = str(e).lower()
            if "not enabled" in error_str or "not found" in error_str or "403" in error_str:
                print("❌ Cloud Logging API is NOT enabled")
                print(f"   Error: {str(e)}")
                print("\n📋 To enable the API, RSE must run:")
                print(f"   gcloud services enable logging.googleapis.com --project={project_id}")
            else:
                print(f"⚠️  Unexpected error: {str(e)}")
                print("   This could indicate that the API is not enabled or there are permission issues")
            return False
            
    except Exception as e:
        print(f"❌ Error checking API: {str(e)}")
        return False

if __name__ == "__main__":
    # Cargar variables de entorno
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv is not installed, using system environment variables")
    
    result = check_logging_api()
    
    print("\n" + "=" * 60)
    print("📝 Information for RSE:")
    print("   Service name: Cloud Logging API")
    print("   API name: logging.googleapis.com")
    project_id = os.getenv("PROJECT_ID", "<PROJECT_ID>")
    print(f"   Command to enable:")
    print(f"   gcloud services enable logging.googleapis.com --project={project_id}")
    print("\n📄 See more details in: GOOGLE_CLOUD_LOGGING.md")
    
    sys.exit(0 if result else 1)
