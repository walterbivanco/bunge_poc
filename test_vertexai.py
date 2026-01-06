import vertexai
from vertexai.generative_models import GenerativeModel

# Inicializar Vertex AI
vertexai.init(
    project="bunge-de-poc-insumos",
    location="us-central1"
)

# Usar Gemini 2.0 (los modelos 1.5 fueron descontinuados en sept 2025)
# Modelo actual: gemini-2.0-flash-exp
model = GenerativeModel("gemini-2.0-flash-exp")

# Generar contenido
response = model.generate_content("Respondé solo OK si funcionás")
print("✅ Respuesta de Gemini:")
print(response.text)
