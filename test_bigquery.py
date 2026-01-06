import os
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Cargar credenciales desde el archivo JSON
# Mejor práctica: usar variable de entorno GOOGLE_APPLICATION_CREDENTIALS
# o definir CREDENTIALS_PATH en .env
path_credenciales = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    os.getenv("CREDENTIALS_PATH", "key.json")  # Fallback a key.json si no está definido
)
credentials = service_account.Credentials.from_service_account_file(path_credenciales)

# Crear cliente de BigQuery con las credenciales
client = bigquery.Client(project="bunge-de-poc-insumos", credentials=credentials)

# Hacer una query simple de test
query = "SELECT 1 AS ok, 'BigQuery funciona!' AS mensaje"
rows = list(client.query(query).result())

print("✅ Respuesta de BigQuery:")
for row in rows:
    print(f"  ok: {row.ok}, mensaje: {row.mensaje}")
