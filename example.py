from google.cloud import aiplatform
from google.oauth2 import service_account

# 1. Cargas la "clave" (el JSON que te mencionaron)
path_a_mi_llave = "key.json"
credentials = service_account.Credentials.from_service_account_file(path_a_mi_llave)

# 2. Inicializas Vertex AI con esas credenciales
aiplatform.init(
    project="tu-proyecto-id",
    location="us-central1", # o tu región
    credentials=credentials
)