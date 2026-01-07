"""
Módulo de logging centralizado con métricas
"""
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import json


# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('chatbot.log')
    ]
)

logger = logging.getLogger('nl2sql_chatbot')


class MetricsCollector:
    """Colector de métricas para requests"""
    
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

