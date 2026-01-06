import os
import vertexai
from vertexai.generative_models import GenerativeModel
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

# Inicializar Vertex AI con las credenciales
vertexai.init(
    project="bunge-de-poc-insumos",
    location="us-central1",
    credentials=credentials
)

# Usar Gemini 2.0 (los modelos 1.5 fueron descontinuados en sept 2025)
# Modelo actual: gemini-2.0-flash-exp
model = GenerativeModel("gemini-2.0-flash-exp")

# Generar contenido
response = model.generate_content("Respondé solo OK si funcionás")
print("✅ Respuesta de Gemini:")
print(response.text)
