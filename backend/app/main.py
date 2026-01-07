"""
FastAPI Application - NL to SQL Chatbot
Orquesta todo el flujo: recibe pregunta → genera SQL → ejecuta → retorna resultados
"""
import os
import time
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from app.models import AskRequest, AskResponse, ErrorResponse, HealthResponse
from app.prompts import get_prompt
from app.llm import init_vertex_ai, nl_to_sql
from app.db import get_table_schema, execute_query, test_connection
from app.logger import metrics_collector, log_info, log_error, log_warning

# Cargar variables de entorno
load_dotenv()

# Inicializar Vertex AI al arrancar la aplicación
log_info("Iniciando aplicación NL → SQL Chatbot")
try:
    init_vertex_ai()
    log_info("Vertex AI inicializado correctamente")
except Exception as e:
    log_warning(f"No se pudo inicializar Vertex AI: {e}")

# Crear aplicación FastAPI
app = FastAPI(
    title="NL to SQL Chatbot",
    description="Chatbot que convierte lenguaje natural a SQL usando Gemini y BigQuery",
    version="1.0.0"
)

# Configurar CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def root():
    """Servir el frontend"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "index.html")
    return FileResponse(frontend_path)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Endpoint de health check
    Verifica que BigQuery y Vertex AI estén funcionando
    """
    bigquery_ok = test_connection()
    vertex_ai_ok = os.getenv("PROJECT_ID") is not None
    
    status = "healthy" if (bigquery_ok and vertex_ai_ok) else "degraded"
    
    return HealthResponse(
        status=status,
        bigquery=bigquery_ok,
        vertex_ai=vertex_ai_ok
    )


@app.post("/ask", response_model=AskResponse, responses={500: {"model": ErrorResponse}})
async def ask_question(request: AskRequest):
    """
    Endpoint principal: recibe pregunta en lenguaje natural y retorna resultados
    
    Flujo:
    1. Obtiene el schema de la tabla BigQuery
    2. Construye el prompt con contexto
    3. Llama a Gemini para generar SQL
    4. Ejecuta el SQL en BigQuery
    5. Retorna resultados formateados
    """
    # Generar ID único para este request
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    steps = []
    
    log_info(f"🔵 Nuevo request [{request_id}]: {request.question}")
    
    try:
        # 1. Obtener schema de la tabla
        step_start = time.time()
        log_info(f"[{request_id}] Paso 1: Obteniendo schema de BigQuery")
        
        project_id = os.getenv("PROJECT_ID")
        dataset = os.getenv("BQ_DATASET")
        table = os.getenv("BQ_TABLE")
        
        if not all([project_id, dataset, table]):
            raise HTTPException(
                status_code=500,
                detail="Configuración incompleta: faltan PROJECT_ID, BQ_DATASET o BQ_TABLE"
            )
        
        schema_text, table_full_id = get_table_schema()
        step_duration = (time.time() - step_start) * 1000
        steps.append({"name": "Get Schema", "duration_ms": step_duration})
        log_info(f"[{request_id}] Schema obtenido ({step_duration/1000:.2f}s)")
        
        # 2. Construir prompt
        step_start = time.time()
        log_info(f"[{request_id}] Paso 2: Construyendo prompt")
        
        prompt = get_prompt(
            question=request.question,
            schema=schema_text,
            project_id=project_id,
            dataset=dataset,
            table=table
        )
        step_duration = (time.time() - step_start) * 1000
        steps.append({"name": "Build Prompt", "duration_ms": step_duration})
        log_info(f"[{request_id}] Prompt construido ({step_duration/1000:.3f}s, {len(prompt)} chars)")
        
        # 3. Generar SQL con Gemini
        log_info(f"[{request_id}] Paso 3: Generando SQL con Gemini")
        llm_result = nl_to_sql(prompt)
        sql = llm_result['sql']
        steps.append({"name": "Generate SQL (Gemini)", "duration_ms": llm_result['duration_ms']})
        
        # 4. Ejecutar SQL en BigQuery
        step_start = time.time()
        log_info(f"[{request_id}] Paso 4: Ejecutando SQL en BigQuery")
        bq_result = execute_query(sql)
        step_duration = (time.time() - step_start) * 1000
        steps.append({"name": "Execute SQL (BigQuery)", "duration_ms": step_duration})
        log_info(f"[{request_id}] BigQuery completado ({step_duration/1000:.2f}s)")
        
        # Calcular tiempo total
        total_time_ms = (time.time() - start_time) * 1000
        
        # Log de métricas
        metrics_collector.log_request({
            "request_id": request_id,
            "question": request.question,
            "steps": steps,
            "total_time_ms": total_time_ms,
            "sql": sql,
            "rows_returned": bq_result["total_rows"],
            "tokens_used": llm_result.get('tokens_used'),
            "model_used": llm_result.get('model_used'),
            "bytes_processed": bq_result.get('bytes_processed'),
            "success": True
        })
        
        # 5. Retornar respuesta
        log_info(f"✅ Request [{request_id}] completado exitosamente en {total_time_ms/1000:.2f}s")
        
        return AskResponse(
            question=request.question,
            sql=sql,
            columns=bq_result["columns"],
            rows=bq_result["rows"],
            total_rows=bq_result["total_rows"]
        )
        
    except ValueError as e:
        total_time_ms = (time.time() - start_time) * 1000
        log_error(f"[{request_id}] Error de validación", e)
        
        metrics_collector.log_request({
            "request_id": request_id,
            "question": request.question,
            "steps": steps,
            "total_time_ms": total_time_ms,
            "success": False,
            "error": str(e)
        })
        
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        total_time_ms = (time.time() - start_time) * 1000
        log_error(f"[{request_id}] Error procesando pregunta", e)
        
        metrics_collector.log_request({
            "request_id": request_id,
            "question": request.question,
            "steps": steps,
            "total_time_ms": total_time_ms,
            "success": False,
            "error": str(e)
        })
        
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando la pregunta: {str(e)}"
        )


@app.get("/schema")
async def get_schema(refresh: bool = False):
    """
    Endpoint para obtener el schema de la tabla configurada
    
    Query params:
        - refresh: Si es True, fuerza recarga del schema (ignora caché)
    """
    try:
        schema_text, table_id = get_table_schema(use_cache=not refresh)
        cached_str = " (sin caché)" if refresh else " (caché)"
        log_info(f"Schema solicitado para tabla: {table_id}{cached_str}")
        return {
            "table": table_id,
            "schema": schema_text
        }
    except Exception as e:
        log_error("Error obteniendo schema", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """
    Endpoint para obtener métricas y estadísticas del sistema
    """
    log_info("Métricas solicitadas")
    try:
        stats = metrics_collector.get_stats()
        recent = metrics_collector.get_recent_metrics(limit=10)
        
        return {
            "stats": stats,
            "recent_requests": recent
        }
    except Exception as e:
        log_error("Error obteniendo métricas", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs")
async def get_logs(lines: int = 50):
    """
    Endpoint para obtener los últimos logs
    """
    log_info(f"Logs solicitados (últimas {lines} líneas)")
    try:
        import os
        log_file = "chatbot.log"
        
        if not os.path.exists(log_file):
            return {"logs": [], "message": "No hay logs disponibles aún"}
        
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
        return {
            "logs": [line.strip() for line in recent_lines],
            "total_lines": len(all_lines),
            "showing": len(recent_lines)
        }
    except Exception as e:
        log_error("Error obteniendo logs", e)
        raise HTTPException(status_code=500, detail=str(e))


# Montar archivos estáticos del frontend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    log_info(f"Iniciando servidor en puerto {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

