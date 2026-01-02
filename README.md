# PoC NL → SQL con Google Cloud

## 🔧 Stack Tecnológico (100% Google)

- **Backend**: FastAPI + Python
- **LLM**: Vertex AI Gemini (gemini-1.5-flash)
- **Base de Datos**: BigQuery
- **Hosting**: Cloud Run
- **CI/CD**: Cloud Build
- **Frontend**: HTML/CSS/JS vanilla (servido desde Cloud Run)

## 📋 Pre-requisitos

1. Proyecto de Google Cloud creado
2. APIs habilitadas:
   - Vertex AI API
   - BigQuery API
   - Cloud Run API
   - Cloud Build API
3. `gcloud` CLI instalado y autenticado
4. Credenciales configuradas:
   ```bash
   gcloud auth application-default login
   gcloud config set project TU_PROJECT_ID
   ```

## 🚀 Cómo levantar la PoC

### Configuración inicial
```bash
# Copiar variables de entorno
cp .env.example .env

# Editar con tus valores reales
nano .env
```

### Desarrollo local
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Deploy a Cloud Run
```bash
./deploy.sh
```

## 🗂️ Estructura del proyecto
Ver estructura de directorios en el código.

