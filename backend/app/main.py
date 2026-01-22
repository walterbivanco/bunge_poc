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
from app.llm import init_vertex_ai, nl_to_sql, recommend_chart_type
from app.db import get_table_schema, get_dimensions_info, execute_query, test_connection, clear_all_caches, get_cache_stats
from app.logger import metrics_collector, log_info, log_error, log_warning
from app.agent import run_agent

# Cargar variables de entorno
load_dotenv()

# Inicializar Vertex AI al arrancar la aplicación
log_info("Iniciando aplicación NL → SQL Chatbot")
try:
    init_vertex_ai()
    log_info("Vertex AI inicializado correctamente")
except Exception as e:
    log_warning(f"No se pudo inicializar Vertex AI: {e}")

# Verificar tablas de dimensiones al inicio (silenciosamente)
try:
    from app.db import get_dimensions_info
    # Usar cache si está disponible para evitar logs verbosos
    dimensions_info = get_dimensions_info(use_cache=True, force_refresh=False)
    if dimensions_info.get("dimensions") and len(dimensions_info["dimensions"]) > 0:
        dim_names = list(dimensions_info["dimensions"].keys())
        log_info(f"✅ Tablas de dimensiones disponibles: {', '.join(dim_names)}")
        log_info("✅ El sistema puede generar JOINs con estas tablas")
    else:
        # Solo mostrar warning si realmente no hay tablas (no si están en cache como "no encontradas")
        log_info("ℹ️  Sin tablas de dimensiones - el sistema funcionará solo con la tabla principal")
        log_info("   Para forzar recarga de dimensiones: POST /dimensions/refresh")
except Exception as e:
    log_warning(f"⚠️  Error verificando dimensiones al inicio: {e}")

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
    """Servir el frontend construido"""
    # Intentar servir desde dist (build de producción)
    dist_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist", "index.html")
    if os.path.exists(dist_path):
        return FileResponse(dist_path)
    # Fallback a index.html del frontend (desarrollo)
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
    
    Flujo (usando agente LangGraph):
    1. El agente obtiene el schema de la tabla BigQuery
    2. El agente obtiene información de dimensiones (si está disponible)
    3. El agente genera SQL usando Gemini
    4. El agente ejecuta el SQL en BigQuery
    5. El agente recomienda tipo de gráfico (si aplica)
    6. Retorna resultados formateados
    
    La misma API externa se mantiene, pero internamente usa LangGraph con herramientas estructuradas.
    """
    # Generar ID único para este request
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    log_info(f"🔵 Nuevo request [{request_id}]: {request.question}")
    
    try:
        # Verificar configuración
        project_id = os.getenv("PROJECT_ID")
        dataset = os.getenv("BQ_DATASET")
        table = os.getenv("BQ_TABLE")
        
        if not all([project_id, dataset, table]):
            raise HTTPException(
                status_code=500,
                detail="Configuración incompleta: faltan PROJECT_ID, BQ_DATASET o BQ_TABLE"
            )
        
        # Preparar historial de conversación si está disponible
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "sql": msg.sql
                }
                for msg in request.conversation_history
            ]
            log_info(f"[{request_id}] Incluyendo {len(conversation_history)} mensajes anteriores en el contexto")
        
        # Ejecutar el agente LangGraph
        agent_result = run_agent(
            question=request.question,
            conversation_history=conversation_history,
            request_id=request_id
        )
        
        # Calcular tiempo total
        total_time_ms = (time.time() - start_time) * 1000
        
        # Log de métricas
        metrics_collector.log_request({
            "request_id": request_id,
            "question": request.question,
            "steps": agent_result.get("steps", []),
            "total_time_ms": total_time_ms,
            "sql": agent_result.get("sql"),
            "rows_returned": agent_result.get("total_rows", 0),
            "success": True
        })
        
        # Retornar respuesta
        log_info(f"✅ Request [{request_id}] completado exitosamente en {total_time_ms/1000:.2f}s")
        
        return AskResponse(
            question=request.question,
            sql=agent_result["sql"],
            columns=agent_result["columns"],
            rows=agent_result["rows"],
            total_rows=agent_result["total_rows"],
            chart_type=agent_result.get("chart_type"),
            chart_config=agent_result.get("chart_config")
        )
        
    except ValueError as e:
        total_time_ms = (time.time() - start_time) * 1000
        log_error(f"[{request_id}] Error de validación", e)
        
        metrics_collector.log_request({
            "request_id": request_id,
            "question": request.question,
            "steps": [],
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
            "steps": [],
            "total_time_ms": total_time_ms,
            "success": False,
            "error": str(e)
        })
        
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando la pregunta: {str(e)}"
        )


@app.post("/dimensions/refresh")
async def refresh_dimensions():
    """
    Endpoint para forzar la recarga de tablas de dimensiones
    Útil cuando se crean nuevas tablas de dimensiones o se corrigen problemas de permisos
    """
    try:
        from app.db import clear_dimensions_cache
        log_info("🔄 Forzando recarga de tablas de dimensiones...")
        clear_dimensions_cache()
        dimensions_info = get_dimensions_info(force_refresh=True)
        
        if dimensions_info.get("dimensions") and len(dimensions_info["dimensions"]) > 0:
            return {
                "success": True,
                "message": f"Dimensiones recargadas: {len(dimensions_info['dimensions'])} tablas disponibles",
                "tables": list(dimensions_info["dimensions"].keys()),
                "dimensions": dimensions_info
            }
        else:
            return {
                "success": False,
                "message": "No se encontraron tablas de dimensiones",
                "tables": [],
                "dimensions": dimensions_info
            }
    except Exception as e:
        log_error("Error recargando dimensiones", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/schema")
async def get_schema(refresh: bool = False):
    """
    Endpoint para obtener el schema de la tabla configurada y tablas de dimensiones
    
    Query params:
        - refresh: Si es True, fuerza recarga del schema (ignora caché)
    """
    try:
        schema_text, table_id = get_table_schema(use_cache=not refresh)
        cached_str = " (sin caché)" if refresh else " (caché)"
        log_info(f"Schema solicitado para tabla: {table_id}{cached_str}")
        
        # Intentar obtener información de dimensiones
        dimensions_info = None
        try:
            dimensions_info = get_dimensions_info(use_cache=not refresh)
        except Exception as e:
            log_warning(f"No se pudieron cargar dimensiones: {e}")
        
        result = {
            "table": table_id,
            "schema": schema_text
        }
        
        if dimensions_info:
            result["dimensions"] = dimensions_info
        
        return result
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


@app.post("/cache/clear")
async def clear_cache(clear_metrics: bool = False):
    """
    Endpoint para limpiar todos los cachés y liberar memoria
    
    Query params:
        - clear_metrics: Si es True, también limpia las métricas almacenadas
    """
    log_info("🧹 Solicitud de limpieza de cachés")
    try:
        clear_all_caches()
        cache_stats = get_cache_stats()
        
        metrics_cleared = False
        if clear_metrics:
            metrics_collector.clear_metrics()
            metrics_cleared = True
            log_info("🧹 Métricas también limpiadas")
        
        metrics_stats = {
            "total_metrics": len(metrics_collector.metrics),
            "max_metrics": metrics_collector.MAX_METRICS,
            "cleared": metrics_cleared
        }
        
        return {
            "status": "success",
            "message": "Todos los cachés han sido limpiados" + (" (incluyendo métricas)" if metrics_cleared else ""),
            "cache_stats": cache_stats,
            "metrics_stats": metrics_stats
        }
    except Exception as e:
        log_error("Error limpiando cachés", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cache/stats")
async def get_cache_statistics():
    """
    Endpoint para obtener estadísticas de los cachés (monitoreo de memoria)
    """
    try:
        cache_stats = get_cache_stats()
        metrics_stats = {
            "total_metrics": len(metrics_collector.metrics),
            "max_metrics": metrics_collector.MAX_METRICS
        }
        return {
            "cache_stats": cache_stats,
            "metrics_stats": metrics_stats
        }
    except Exception as e:
        log_error("Error obteniendo estadísticas de caché", e)
        raise HTTPException(status_code=500, detail=str(e))


# Montar archivos estáticos del frontend construido
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
frontend_src = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")

# Rutas de API que no deben ser capturadas por el SPA
API_ROUTES = ["/ask", "/health", "/schema", "/metrics", "/logs", "/docs", "/openapi.json", "/redoc"]

# Priorizar dist (build de producción) si existe
if os.path.exists(frontend_dist):
    # Montar assets estáticos
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    
    # Servir otros archivos estáticos del build y manejar routing de React
    @app.get("/{path:path}", include_in_schema=False)
    async def serve_spa(path: str):
        """Servir archivos del SPA o redirigir a index.html para routing de React"""
        # No interceptar rutas de API
        if path in API_ROUTES or path.startswith(tuple(API_ROUTES)):
            raise HTTPException(status_code=404, detail="Not found")
        
        full_path = os.path.join(frontend_dist, path)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            return FileResponse(full_path)
        # Si no existe, servir index.html para que React Router maneje la ruta
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    # Fallback: servir desde el directorio fuente (desarrollo)
    app.mount("/static", StaticFiles(directory=frontend_src), name="static")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    log_info(f"Iniciando servidor en puerto {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

