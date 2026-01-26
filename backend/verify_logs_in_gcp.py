#!/usr/bin/env python3
"""
Script to verify if logs are actually being sent to Google Cloud Logging
This script sends a test log and then searches for it in GCP
"""
import os
import sys
import time
import uuid
from datetime import datetime, timedelta

def verify_logs_in_gcp():
    """Verifies if logs are actually being sent to GCP by sending a test log and searching for it"""
    project_id = os.getenv("PROJECT_ID")
    
    if not project_id:
        print("❌ PROJECT_ID is not configured in environment variables")
        return False
    
    print(f"🔍 Verifying if logs are being sent to GCP for project: {project_id}")
    print("=" * 60)
    
    # Verificar si el módulo está instalado
    try:
        import google.cloud.logging as cloud_logging
        from google.api_core import exceptions
    except ImportError:
        print("❌ google-cloud-logging is not installed")
        print("   Run: pip install google-cloud-logging")
        return False
    
    try:
        # Crear cliente de Cloud Logging
        print("✅ Initializing Cloud Logging client...")
        client = cloud_logging.Client(project=project_id)
        
        # Generar un identificador único para el log de prueba
        test_id = str(uuid.uuid4())[:8]
        test_message = f"🧪 TEST LOG - ID: {test_id} - Timestamp: {datetime.now().isoformat()}"
        
        print(f"\n📝 Sending test log with ID: {test_id}")
        print(f"   Message: {test_message}")
        
        # Configurar logging y enviar un log de prueba
        try:
            import logging
            client.setup_logging()
            logger = logging.getLogger('nl2sql_chatbot')
            logger.info(test_message)
            
            # Forzar el envío inmediato (flush)
            import logging.handlers
            for handler in logger.handlers:
                if hasattr(handler, 'flush'):
                    handler.flush()
            
            print("✅ Test log sent successfully")
            print("⏳ Waiting 5 seconds for log to be indexed in GCP...")
            time.sleep(5)
            
        except exceptions.PermissionDenied as e:
            error_str = str(e)
            print(f"\n❌ PERMISSION DENIED when sending log")
            print(f"   Error: {error_str[:200]}")
            print("\n🔑 Missing Permission: logging.logEntries.create")
            print("\n📋 Solution:")
            print("   You need the 'roles/logging.logWriter' role to write logs.")
            print("   Ask RSE to grant this role to your account or service account:")
            print(f"   gcloud projects add-iam-policy-binding {project_id} \\")
            print(f"     --member='user:YOUR_EMAIL@domain.com' \\")
            print(f"     --role='roles/logging.logWriter'")
            print("\n   Or for a service account:")
            print(f"   gcloud projects add-iam-policy-binding {project_id} \\")
            print(f"     --member='serviceAccount:SERVICE_ACCOUNT@project.iam.gserviceaccount.com' \\")
            print(f"     --role='roles/logging.logWriter'")
            return False
        except Exception as e:
            error_str = str(e)
            print(f"\n❌ Error sending test log")
            print(f"   Error: {error_str[:300]}")
            if "Permission" in error_str or "403" in error_str:
                print("\n💡 This looks like a permissions issue.")
                print("   Check that you have 'roles/logging.logWriter' role")
            return False
        
        # Buscar el log en Cloud Logging
        print("\n🔍 Searching for test log in Cloud Logging...")
        try:
            # Buscar logs en los últimos 2 minutos
            # Formato del filtro: usar comillas simples y formato correcto
            from datetime import timezone
            time_limit = (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat()
            
            filter_str = f'resource.type="global" AND logName="projects/{project_id}/logs/nl2sql_chatbot" AND textPayload=~"{test_id}" AND timestamp>="{time_limit}"'
            
            entries = list(client.list_entries(
                filter_=filter_str,
                page_size=10,
                order_by=cloud_logging.DESCENDING
            ))
            
            # Verificar si encontramos el log
            found = False
            entry_count = 0
            for entry in entries:
                entry_count += 1
                payload_str = str(entry.payload) if hasattr(entry, 'payload') else str(entry)
                if test_id in payload_str:
                    found = True
                    print(f"✅ SUCCESS! Test log found in Cloud Logging!")
                    print(f"   Log ID: {getattr(entry, 'log_id', 'N/A')}")
                    print(f"   Timestamp: {getattr(entry, 'timestamp', 'N/A')}")
                    print(f"   Severity: {getattr(entry, 'severity', 'N/A')}")
                    print(f"   Payload: {payload_str[:200]}...")
                    break
            
            if entry_count == 0:
                print(f"⚠️  No entries found with filter (searched last 2 minutes)")
            
            if not found:
                print("⚠️  Test log NOT found in Cloud Logging")
                print("   This could mean:")
                print("   1. Logs are not being sent (check API status)")
                print("   2. There's a delay in indexing (wait a few more seconds)")
                print("   3. Permissions issue (check logWriter role)")
                print("\n   Try checking manually in GCP Console:")
                print(f"   https://console.cloud.google.com/logs/query?project={project_id}")
                print(f"   Filter: logName=\"projects/{project_id}/logs/nl2sql_chatbot\"")
                return False
            
            return True
            
        except exceptions.PermissionDenied as e:
            print("❌ Permission denied when searching logs")
            print(f"   Error: {str(e)}")
            print("   You need 'roles/logging.viewer' or 'roles/logging.privateLogViewer' to search logs")
            return False
        except Exception as e:
            print(f"❌ Error searching for logs: {str(e)}")
            print("   The log might still be sent, but we couldn't verify it")
            print("   Check manually in GCP Console")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    # Cargar variables de entorno primero
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv is not installed, using system environment variables")
    
    result = verify_logs_in_gcp()
    
    print("\n" + "=" * 60)
    if result:
        print("✅ VERIFICATION SUCCESSFUL")
        print("   Logs are being sent to Google Cloud Logging")
        print("\n💡 Your application logs should now appear in GCP Console")
    else:
        print("❌ VERIFICATION FAILED")
        print("   Logs are NOT being sent to Google Cloud Logging")
        print("\n📋 Troubleshooting steps:")
        print("   1. Check API status: python check_logging_api.py")
        print("   2. Verify permissions: You need 'roles/logging.logWriter'")
        print("   3. Check if using service account: Verify it has the role")
        print("   4. Check GCP Console manually for any logs")
        print("\n🔑 Common issue: Missing 'logging.logEntries.create' permission")
        print("   This means you need the 'roles/logging.logWriter' role")
    
    print("\n📄 See more details in: GOOGLE_CLOUD_LOGGING.md")
    
    sys.exit(0 if result else 1)
