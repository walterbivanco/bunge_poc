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

## Instalación de herramientas de Google

1. Instalar SDk de Google

brew install --cask google-cloud-sdk (para Mac)

2. Verificar versión

gcloud version

3. Agregar al PATH (ni es que es necesario, si ya esta y se lo agragega no pasa nada)

echo 'export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"' >> ~/.zshrc

4. Verificar si faltaba lo del PATH

gcloud version

5. Iniciar logia ADC

gcloud auth application-default login --no-browser

A este código copiarlo y pegarlo en una consola, y queda esperando

6. En otra consola, copiar el comando que se genero en la consola anterior(es único por cada corrida) abre el navegador, seguir los pasos y luego regresar a la consola:

Ej:
gcloud auth application-default login --remote-bootstrap="https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com&scope=openid+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fsqlservice.login&state=2l53ceB1eINLXvGHOds8RhgdkIVDYI&access_type=offline&code_challenge=p9iuSJu0vVfwVumQb2CdHdbSqee5mR6Z7pCA96eCcJg&code_challenge_method=S256&token_usage=remote"

La salida de este comando, luego de terminar el proceso web, genera algo como:

https://localhost:8085/?state=2l53ceB1eINLXvGHOds8RhgdkIVDYI&code=4/0ATX87lPpF71p2CcI8t1Qugf5vqutTgWYYury3XE-heUGBOnjmI3Ar1SuXY8VJTqkRSwOYQ&scope=email%20https://www.googleapis.com/auth/cloud-platform%20https://www.googleapis.com/auth/sqlservice.login%20https://www.googleapis.com/auth/userinfo.email%20openid&authuser=0&hd=taligent.com.ar&prompt=consent

7. A la salida de la segunda consola(paso 6) copiar y pegar en la consola uno que quedo esperando, si todo esta bien genera algo como:

These credentials will be used by any library that requests Application Default Credentials (ADC).
WARNING:
Cannot add the project "bunge-de-poc-insumos" to ADC as the quota project because the account in ADC does not have the "serviceusage.services.use" permission on this project. You might receive a "quota_exceeded" or "API not enabled" error. Run $ gcloud auth application-default set-quota-project to add a quota project.

8.  Para verificar que todo este bien

gcloud auth application-default print-access-token