"""
Módulo para interactuar con Vertex AI Gemini
Responsable de convertir lenguaje natural a SQL
"""
import os
import re
import time
import vertexai
from vertexai.generative_models import GenerativeModel
from typing import Optional, Dict, Any
from google.api_core import exceptions as google_exceptions
from app.logger import log_info, log_error, log_warning


def init_vertex_ai():
    """Inicializa Vertex AI con las credenciales del proyecto"""
    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("VERTEX_LOCATION", "us-central1")
    
    if not project_id:
        raise ValueError("PROJECT_ID no está configurado en las variables de entorno")
    
    log_info(f"Inicializando Vertex AI - Project: {project_id}, Location: {location}")
    vertexai.init(project=project_id, location=location)


def nl_to_sql(prompt: str, model_name: Optional[str] = None, max_retries: int = 3) -> Dict[str, Any]:
    """
    Convierte una pregunta en lenguaje natural a SQL usando Gemini
    
    Args:
        prompt: Prompt completo con contexto y pregunta
        model_name: Nombre del modelo (por defecto usa GEMINI_MODEL del .env)
        max_retries: Número máximo de reintentos en caso de error 429
        
    Returns:
        Dict con SQL generado y metadata (tiempo, tokens, etc.)
        
    Raises:
        Exception: Si hay error en la llamada al modelo
    """
    if model_name is None:
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    start_time = time.time()
    log_info(f"Generando SQL con modelo: {model_name}")
    
    # Retry logic con backoff exponencial
    retry_count = 0
    last_error = None
    
    while retry_count <= max_retries:
        try:
            # ⚡ Configuración ultra-optimizada para velocidad máxima
            model = GenerativeModel(
                model_name,
                generation_config={
                    "temperature": 0,           # Determinista
                    "top_p": 0.8,              # Muy enfocado
                    "top_k": 10,               # Pocas opciones = más rápido
                    "max_output_tokens": 256,  # SQL es corto
                    "candidate_count": 1,      # Solo una respuesta
                }
            )
            
            # Generar el SQL
            if retry_count > 0:
                log_warning(f"Reintento {retry_count}/{max_retries} - Llamando a Gemini...")
            else:
                log_info("⏳ Llamando a Gemini para generar SQL...")
            
            # Medir tiempo de llamada a la API
            api_start = time.time()
            response = model.generate_content(prompt)
            api_duration = (time.time() - api_start) * 1000
            log_info(f"⚡ Respuesta recibida de Gemini en {api_duration/1000:.2f}s")
        
            # Extraer solo el SQL de la respuesta
            sql = extract_sql_from_response(response.text)
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Intentar extraer metadata de uso (si está disponible)
            tokens_used = None
            try:
                if hasattr(response, 'usage_metadata'):
                    tokens_used = {
                        'prompt_tokens': getattr(response.usage_metadata, 'prompt_token_count', None),
                        'candidates_tokens': getattr(response.usage_metadata, 'candidates_token_count', None),
                        'total_tokens': getattr(response.usage_metadata, 'total_token_count', None)
                    }
                    log_info(f"Tokens usados: {tokens_used}")
            except:
                pass
            
            if retry_count > 0:
                log_info(f"✅ Éxito después de {retry_count} reintento(s) en {duration_ms/1000:.2f}s")
            else:
                log_info(f"SQL generado exitosamente en {duration_ms/1000:.2f}s")
            
            log_info(f"SQL: {sql[:100]}..." if len(sql) > 100 else f"SQL: {sql}")
            
            return {
                'sql': sql,
                'model_used': model_name,
                'duration_ms': duration_ms,
                'tokens_used': tokens_used,
                'prompt_length': len(prompt),
                'sql_length': len(sql),
                'retry_count': retry_count
            }
            
        except google_exceptions.ResourceExhausted as e:
            # Error 429 - Rate limit excedido
            retry_count += 1
            last_error = e
            
            if retry_count <= max_retries:
                # Backoff exponencial: 2^retry_count segundos
                wait_time = 2 ** retry_count
                log_warning(f"⚠️  Error 429 (Rate Limit) - Esperando {wait_time}s antes de reintentar...")
                time.sleep(wait_time)
            else:
                duration_ms = (time.time() - start_time) * 1000
                log_error(f"❌ Error 429 después de {max_retries} reintentos ({duration_ms/1000:.2f}s)", e)
                raise Exception(
                    f"Límite de cuota de Gemini excedido. "
                    f"Has alcanzado el límite de requests por minuto. "
                    f"Por favor espera unos segundos y vuelve a intentar."
                )
        
        except Exception as e:
            # Otros errores no reintentar
            duration_ms = (time.time() - start_time) * 1000
            log_error(f"Error generando SQL después de {duration_ms/1000:.2f}s", e)
            raise Exception(f"Error al generar SQL con Gemini: {str(e)}")


def extract_sql_from_response(response_text: str) -> str:
    """
    Extrae el SQL limpio de la respuesta del modelo
    Elimina markdown, explicaciones, etc.
    
    Args:
        response_text: Texto completo de la respuesta del modelo
        
    Returns:
        SQL limpio y ejecutable
    """
    # Eliminar bloques de código markdown ```sql ... ```
    sql = re.sub(r'```sql\s*', '', response_text)
    sql = re.sub(r'```\s*', '', sql)
    
    # Eliminar comentarios de una línea
    sql = re.sub(r'--[^\n]*', '', sql)
    
    # Limpiar espacios en blanco excesivos
    sql = ' '.join(sql.split())
    
    # Verificar que sea un SELECT
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith('SELECT'):
        raise ValueError("El modelo no generó una consulta SELECT válida")
    
    return sql.strip()

