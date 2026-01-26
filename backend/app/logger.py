"""
Módulo de logging centralizado con métricas
Soporta logging local y Google Cloud Logging (si está habilitado)
"""
import logging
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import json

# Intentar importar Google Cloud Logging (opcional)
try:
    import google.cloud.logging as cloud_logging
    GCP_LOGGING_AVAILABLE = True
except ImportError:
    GCP_LOGGING_AVAILABLE = False
    cloud_logging = None

# Configurar handlers base
handlers = [
    logging.StreamHandler(),
    logging.FileHandler('chatbot.log')
]

# Intentar configurar Google Cloud Logging si está disponible
gcp_logging_enabled = False
if GCP_LOGGING_AVAILABLE:
    try:
        project_id = os.getenv("PROJECT_ID")
        if project_id:
            # Inicializar cliente de Cloud Logging
            client = cloud_logging.Client(project=project_id)
            # Configurar logging estándar para redirigir a GCP
            # Esto puede fallar si la API no está habilitada o no hay permisos
            client.setup_logging()
            gcp_logging_enabled = True
            # Solo loguear si se configuró exitosamente (evitar spam en cada import)
            import sys
            if not hasattr(sys, '_gcp_logging_initialized'):
                print("✅ Google Cloud Logging enabled - Logs will be sent to GCP")
                sys._gcp_logging_initialized = True
    except Exception as e:
        # Si falla (API no habilitada, permisos, etc.), continuar con logging local
        # No mostrar warning en cada import, solo la primera vez
        import sys
        if not hasattr(sys, '_gcp_logging_failed'):
            error_msg = str(e).lower()
            # Solo mostrar warning si es un error de API no habilitada, no errores de importación
            if "403" in error_msg or "not enabled" in error_msg or "permission" in error_msg:
                print("⚠️  Google Cloud Logging not available (API not enabled or no permissions)")
                print("   Continuing with local logging only")
                print(f"   Error: {str(e)[:100]}...")
                print("   To enable: gcloud services enable logging.googleapis.com --project=<PROJECT_ID>")
            # Para otros errores (conexión, etc.), ser más silencioso
            sys._gcp_logging_failed = True

# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers,
    force=True  # Forzar reconfiguración si ya estaba configurado
)

logger = logging.getLogger('nl2sql_chatbot')


class MetricsCollector:
    """Colector de métricas para requests"""
    
    # Límite de memoria: máximo 1000 métricas en memoria
    MAX_METRICS = 1000
    
    def __init__(self):
        self.metrics = []
    
    def log_request(self, request_data: Dict[str, Any]):
        """Log de request completo con métricas"""
        metric = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_data.get("request_id"),
            "question": request_data.get("question"),
            "steps": request_data.get("steps", []),
            "total_time_ms": request_data.get("total_time_ms"),
            "sql_generated": request_data.get("sql"),
            "rows_returned": request_data.get("rows_returned"),
            "tokens_used": request_data.get("tokens_used"),
            "model_used": request_data.get("model_used"),
            "success": request_data.get("success", True),
            "error": request_data.get("error")
        }
        
        # Limitar tamaño de métricas en memoria (FIFO)
        if len(self.metrics) >= self.MAX_METRICS:
            # Eliminar las métricas más antiguas (primeras 100)
            self.metrics = self.metrics[100:]
            logger.debug(f"🧹 Memory cleanup: removed 100 old metrics")
        
        self.metrics.append(metric)
        
        # Log detallado
        logger.info("=" * 80)
        logger.info(f"📊 REQUEST SUMMARY - ID: {metric['request_id']}")
        logger.info(f"❓ Question: {metric['question']}")
        logger.info(f"⏱️  Total Time: {metric['total_time_ms']/1000:.2f}s")
        
        if metric.get('steps'):
            logger.info("📝 Steps:")
            for step in metric['steps']:
                logger.info(f"  - {step['name']}: {step['duration_ms']/1000:.2f}s")
        
        if metric.get('sql_generated'):
            logger.info(f"🔍 SQL: {metric['sql_generated']}")
        
        if metric.get('rows_returned') is not None:
            logger.info(f"📊 Rows: {metric['rows_returned']}")
        
        if metric.get('tokens_used'):
            logger.info(f"🎯 Tokens: {metric['tokens_used']}")
        
        if metric.get('model_used'):
            logger.info(f"🤖 Model: {metric['model_used']}")
        
        if not metric['success']:
            logger.error(f"❌ Error: {metric['error']}")
        else:
            logger.info("✅ Success")
        
        logger.info("=" * 80)
        
        return metric
    
    def get_recent_metrics(self, limit: int = 10) -> list:
        """Obtiene las últimas N métricas"""
        return self.metrics[-limit:]
    
    def clear_metrics(self, keep_recent: int = 0):
        """Limpia las métricas almacenadas
        
        Args:
            keep_recent: Número de métricas recientes a mantener (0 = limpiar todas)
        """
        if keep_recent > 0 and len(self.metrics) > keep_recent:
            self.metrics = self.metrics[-keep_recent:]
            logger.info(f"🧹 Metrics cleanup: kept {keep_recent} most recent")
        else:
            count = len(self.metrics)
            self.metrics.clear()
            logger.info(f"🧹 Metrics cleanup: removed {count} metrics")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales"""
        if not self.metrics:
            return {}
        
        successful = [m for m in self.metrics if m['success']]
        failed = [m for m in self.metrics if not m['success']]
        
        times = [m['total_time_ms'] for m in successful if m.get('total_time_ms')]
        
        return {
            "total_requests": len(self.metrics),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(self.metrics) * 100 if self.metrics else 0,
            "avg_response_time_ms": sum(times) / len(times) if times else 0,
            "min_response_time_ms": min(times) if times else 0,
            "max_response_time_ms": max(times) if times else 0,
        }


# Instancia global del collector
metrics_collector = MetricsCollector()


def log_step(step_name: str):
    """Decorador para loguear pasos individuales con timing"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"▶️  Starting: {step_name}")
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"✅ Completed: {step_name} ({duration_ms:.2f}ms)")
                
                # Guardar timing en kwargs si existe request_steps
                if 'request_steps' in kwargs:
                    kwargs['request_steps'].append({
                        'name': step_name,
                        'duration_ms': duration_ms,
                        'success': True
                    })
                
                return result, duration_ms
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(f"❌ Failed: {step_name} ({duration_ms:.2f}ms) - {str(e)}")
                
                if 'request_steps' in kwargs:
                    kwargs['request_steps'].append({
                        'name': step_name,
                        'duration_ms': duration_ms,
                        'success': False,
                        'error': str(e)
                    })
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"▶️  Starting: {step_name}")
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"✅ Completed: {step_name} ({duration_ms:.2f}ms)")
                
                return result, duration_ms
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                logger.error(f"❌ Failed: {step_name} ({duration_ms:.2f}ms) - {str(e)}")
                raise
        
        # Detectar si la función es async o sync
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def log_info(message: str):
    """Log info con formato"""
    logger.info(f"ℹ️  {message}")


def log_warning(message: str):
    """Log warning con formato"""
    logger.warning(f"⚠️  {message}")


def log_error(message: str, error: Optional[Exception] = None):
    """Log error con formato"""
    if error:
        logger.error(f"❌ {message}: {str(error)}", exc_info=True)
    else:
        logger.error(f"❌ {message}")

