# PoC NL → SQL con Google Cloud

## 🔧 Stack Tecnológico (100% Google)

- **Backend**: FastAPI + Python
- **LLM**: Vertex AI Gemini (gemini-2.0-flash-exp)
  - Conversión de lenguaje natural a SQL
  - Recomendación inteligente de tipos de gráficos
- **Agente**: LangGraph + LangChain
  - Sistema agéntico con herramientas estructuradas
  - Orquestación de flujo multi-paso (schema → SQL → ejecución → visualización)
- **Base de Datos**: BigQuery
- **Hosting**: Cloud Run
- **CI/CD**: Cloud Build
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
  - Interfaz de chat moderna
  - Visualización automática de datos con gráficos (Recharts)
  - Diseño responsive y temático

## ✨ Características Principales

- **Sistema Agéntico con LangGraph**: Orquestación inteligente del flujo NL→SQL usando herramientas estructuradas
- **Conversión NL→SQL**: Pregunta en lenguaje natural, obtén SQL ejecutable
- **JOINs Automáticos**: Detecta y genera automáticamente JOINs con tablas de dimensiones (DimProducts, DimProvince, DimTime)
- **Visualización Inteligente**: El LLM analiza los datos y recomienda el tipo de gráfico más apropiado
- **Gráficos Automáticos**: Bar, Line, Pie y Area charts generados automáticamente
- **Interfaz Moderna**: Chat UI con React, TypeScript y Tailwind CSS
- **Memoria Conversacional**: Mantiene contexto de las últimas 5 interacciones para mejor comprensión
- **Gestión de Memoria**: Límites automáticos en cachés y métricas para prevenir crecimiento indefinido
- **Logging y Métricas**: Sistema completo de logging con tiempos, tokens y estadísticas (Google Cloud Logging con fallback local)

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

#### 1. Variables de entorno
```bash
# Copiar variables de entorno
cp .env.example .env

# Editar con tus valores reales
nano .env
```

#### 2. Credenciales de Service Account (Recomendado)

**⚠️ IMPORTANTE: NUNCA commitees archivos de credenciales al repositorio**

1. Descargar el archivo JSON de credenciales desde Google Cloud Console:
   - Ir a IAM & Admin > Service Accounts
   - Crear o seleccionar una service account
   - Generar una nueva clave JSON

2. Guardar el archivo como `key.json` en la raíz del proyecto (o en una ubicación segura fuera del repo)

3. Configurar la variable de entorno (recomendado):
   ```bash
   # En .env
   CREDENTIALS_PATH=/ruta/segura/a/tu/key.json
   
   # O usar la variable estándar de Google
   export GOOGLE_APPLICATION_CREDENTIALS=/ruta/segura/a/tu/key.json
   ```

4. Alternativamente, copiar el archivo a `key.json` en la raíz del proyecto:
   ```bash
   cp /ruta/a/tu/credenciales.json key.json
   ```

**Nota**: El archivo `key.json` está en `.gitignore` y NO será commiteado al repositorio.

### Desarrollo local

#### Backend
```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

#### Frontend
```bash
# Instalar dependencias
cd frontend
npm install

# Modo desarrollo (con hot reload)
# Corre en http://localhost:5173 y hace proxy de las APIs al backend en :8080
npm run dev

# Construir para producción
npm run build
```

**Nota**: 
- En desarrollo: El frontend corre en `http://localhost:5173` y hace proxy de las llamadas API al backend en `http://localhost:8080`
- En producción: El frontend construido se genera en `frontend/dist/` y es servido automáticamente por el backend en el puerto 8080
- **Dependencias principales del frontend**:
  - `react` + `react-dom`: Framework React
  - `recharts`: Librería de gráficos
  - `tailwindcss`: Framework CSS utility-first
  - `@radix-ui/*`: Componentes UI accesibles
  - `lucide-react`: Iconos

### Deploy a Cloud Run
```bash
./deploy.sh
```

## 🗂️ Estructura del proyecto

```
poc/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, endpoints principales
│   │   ├── agent.py         # Agente LangGraph con herramientas estructuradas
│   │   ├── llm.py           # Integración con Vertex AI Gemini (NL→SQL + recomendación de gráficos)
│   │   ├── db.py            # Conexión y ejecución de queries en BigQuery
│   │   ├── prompts.py       # Prompts para el LLM
│   │   ├── models.py        # Modelos Pydantic (request/response)
│   │   └── logger.py        # Sistema de logging y métricas
│   ├── Dockerfile           # Container para Cloud Run
│   ├── chatbot.log          # Logs de la aplicación
│   ├── test_memory.py       # Script para probar gestión de memoria
│   └── check_logging_api.py  # Script para verificar Google Cloud Logging
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── Index.tsx   # Página principal del chat
│   │   ├── components/
│   │   │   └── chat/       # Componentes del chat
│   │   │       ├── ChatMessage.tsx    # Mensaje individual (con gráficos)
│   │   │       ├── ChatArea.tsx       # Área de mensajes
│   │   │       ├── ChatInputArea.tsx  # Input del usuario
│   │   │       ├── ChatSidebar.tsx    # Sidebar con conversaciones
│   │   │       ├── WelcomeScreen.tsx  # Pantalla de bienvenida
│   │   │       └── DataChart.tsx      # Componente de gráficos
│   │   └── lib/
│   │       └── utils.ts     # Utilidades (formateo de columnas y números)
│   ├── dist/                # Build de producción
│   └── package.json         # Dependencias del frontend
├── requirements.txt         # Dependencias de Python
├── .env.example            # Template de variables de entorno
├── QUESTIONS_SET.md        # Conjunto de preguntas de prueba
├── MODELO_DATOS.md         # Documentación del modelo de datos (Star Schema)
├── TEST_MEMORY.md          # Guía de pruebas de gestión de memoria
├── GOOGLE_CLOUD_LOGGING.md # Documentación de Google Cloud Logging
└── README.md               # Este archivo
```

## 🤖 Sistema Agéntico con LangGraph

El sistema utiliza **LangGraph** para orquestar el flujo NL→SQL de forma estructurada:

1. **Herramientas del Agente**:
   - `get_schema_tool`: Obtiene el schema de la tabla principal
   - `get_dimensions_tool`: Obtiene información de tablas de dimensiones
   - `generate_sql_tool`: Genera SQL usando el LLM
   - `execute_query_tool`: Ejecuta la consulta en BigQuery
   - `recommend_chart_tool`: Recomienda el tipo de gráfico

2. **Flujo del Agente**:
   - El agente decide qué herramientas usar según la pregunta
   - Ejecuta las herramientas en secuencia
   - Mantiene estado entre pasos
   - Maneja errores y reintentos automáticamente

3. **Ventajas**:
   - Flujo estructurado y predecible
   - Fácil de extender con nuevas herramientas
   - Mejor manejo de errores
   - Logging detallado de cada paso

## 📊 Sistema de Visualización de Datos

El sistema utiliza **Gemini (LLM)** para analizar los resultados de las consultas y recomendar automáticamente el tipo de gráfico más apropiado:

1. **Análisis Inteligente**: Después de ejecutar una consulta SQL, el LLM analiza:
   - La pregunta original del usuario
   - La estructura de los datos (columnas, tipos)
   - Una muestra de los resultados

2. **Recomendación de Gráfico**: El LLM determina si los datos deben visualizarse y qué tipo de gráfico usar:
   - **Bar Chart**: Para datos categóricos vs numéricos
   - **Line Chart**: Para series temporales o datos secuenciales
   - **Pie Chart**: Para distribuciones de categorías (máx 10 categorías)
   - **Area Chart**: Para datos acumulativos en el tiempo
   - **null**: Si los datos no son adecuados para visualización

3. **Renderizado Automático**: El frontend renderiza el gráfico recomendado usando Recharts

## 🗄️ Modelo de Datos: Star Schema

El sistema soporta un modelo de estrella (star schema) con:
- **Fact Table**: `contracts_gold_2` (en dataset `Gold`)
- **Dimension Tables**: `DimProducts`, `DimProvince`, `DimTime` (en dataset `Dim`)

El agente detecta automáticamente cuándo necesita hacer JOINs con las tablas de dimensiones. Ver `MODELO_DATOS.md` para más detalles.

## 💾 Gestión de Memoria

El sistema implementa límites automáticos para prevenir crecimiento indefinido:
- **Caché de Schemas**: Máximo 50 schemas (FIFO)
- **Caché de Dimensiones**: Sin límite (pero con caché de "no encontradas" limitado a 100)
- **Métricas**: Máximo 1000 métricas (FIFO, elimina 100 más antiguas cuando se alcanza el límite)
- **Conversaciones Frontend**: Máximo 50 conversaciones, 100 mensajes por conversación

Ver `TEST_MEMORY.md` para guía de pruebas.

### Ejemplos de Consultas que Generan Gráficos

- "How many contracts are there by status?" → Pie Chart
- "Show me sales over time" → Line Chart
- "Average price per product" → Bar Chart
- "Total revenue by region" → Bar Chart

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

## 📦 Dependencias

### Backend (Python)

Las dependencias están en `requirements.txt`. Para instalar:

```bash
pip install -r requirements.txt
```

**Principales dependencias**:
- `google-cloud-aiplatform`: Integración con Vertex AI Gemini
- `google-cloud-bigquery`: Cliente de BigQuery
- `google-cloud-logging`: Sistema de logging centralizado en GCP
- `langgraph`: Framework para construir agentes con estado
- `langchain`: Framework para aplicaciones LLM
- `langchain-google-vertexai`: Integración de LangChain con Vertex AI
- `fastapi`: Framework web
- `uvicorn`: Servidor ASGI
- `pydantic`: Validación de datos

### Frontend (Node.js)

Las dependencias están en `frontend/package.json`. Para instalar:

```bash
cd frontend
npm install
```

**Principales dependencias**:
- `react` + `react-dom`: Framework React
- `recharts`: Librería de gráficos (Bar, Line, Pie, Area)
- `tailwindcss`: Framework CSS utility-first
- `@radix-ui/*`: Componentes UI accesibles y modulares
- `lucide-react`: Iconos SVG
- `@tanstack/react-query`: Manejo de estado del servidor
- `react-router-dom`: Routing del frontend
- `typescript`: Tipado estático

## 🔍 Endpoints de la API

- `POST /ask`: Endpoint principal para hacer preguntas en lenguaje natural
  - Request: `{ "question": "tu pregunta aquí", "conversation_history": [...] }` (opcional)
  - Response: `{ "sql": "...", "columns": [...], "rows": [...], "total_rows": N, "chart_type": "bar|line|pie|area|null", "chart_config": {...} }`
  - **Nota**: Ahora usa LangGraph con sistema agéntico para orquestar el flujo
- `GET /health`: Health check del servicio
- `GET /schema`: Obtener el schema de la tabla (con caché)
- `GET /metrics`: Métricas y estadísticas del sistema
- `GET /logs`: Últimos logs del sistema
- `GET /cache/stats`: Estadísticas de cachés (schemas, dimensiones, métricas)
- `POST /cache/clear`: Limpiar cachés (opción `clear_metrics` para limpiar también métricas)