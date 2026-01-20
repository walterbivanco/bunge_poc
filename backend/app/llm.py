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
            
            # Validar y corregir el nombre de la tabla si es necesario
            sql = validate_and_fix_table_name(sql, prompt)
            
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


def recommend_chart_type(
    question: str,
    columns: list,
    rows: list,
    max_rows_sample: int = 20
) -> Dict[str, Any]:
    """
    Usa Gemini para analizar los datos y recomendar el tipo de gráfico más apropiado
    
    Args:
        question: Pregunta original del usuario
        columns: Lista de nombres de columnas
        rows: Lista de filas de datos (muestra limitada)
        max_rows_sample: Número máximo de filas a enviar al LLM
        
    Returns:
        Dict con chart_type y chart_config, o None si no se recomienda gráfico
    """
    if not columns or not rows or len(rows) == 0:
        return {"chart_type": None, "chart_config": None}
    
    # Limitar filas para no exceder tokens
    sample_rows = rows[:max_rows_sample]
    
    # Preparar datos en formato legible
    data_sample = []
    for row in sample_rows:
        row_dict = {}
        for i, col in enumerate(columns):
            row_dict[col] = row[i] if i < len(row) else None
        data_sample.append(row_dict)
    
    prompt = f"""Analyze the following query results and determine if a chart would be helpful for visualization.

User Question: "{question}"

Columns: {', '.join(columns)}
Total Rows: {len(rows)}
Sample Data (first {len(sample_rows)} rows):
{str(data_sample)}

Based on the question, data structure, and sample values, determine:
1. Should this data be visualized? (yes/no)
2. If yes, what chart type is most appropriate? Options: "bar", "line", "pie", "area", or null
3. Which column should be on the X-axis? (column name)
4. Which column should be on the Y-axis? (column name, or "value" for pie charts)

Consider:
- Bar charts for categorical X with numeric Y
- Line charts for time series or sequential data
- Pie charts for distribution of a single categorical variable (max 10 categories)
- Area charts for cumulative data over time
- null if data is not suitable for visualization (too many rows, no clear pattern, etc.)

Respond ONLY with valid JSON in this exact format:
{{
    "should_visualize": true/false,
    "chart_type": "bar"|"line"|"pie"|"area"|null,
    "xKey": "column_name"|null,
    "yKey": "column_name"|"value"|null
}}
"""
    
    try:
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        model = GenerativeModel(
            model_name,
            generation_config={
                "temperature": 0.3,
                "top_p": 0.8,
                "top_k": 10,
                "max_output_tokens": 256,
                "candidate_count": 1,
            }
        )
        
        log_info("📊 Analizando datos con Gemini para recomendar tipo de gráfico...")
        response = model.generate_content(prompt)
        
        # Extraer JSON de la respuesta
        import json
        response_text = response.text.strip()
        
        # Limpiar markdown si existe
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        
        if result.get("should_visualize") and result.get("chart_type"):
            log_info(f"✅ Gráfico recomendado: {result['chart_type']}")
            return {
                "chart_type": result["chart_type"],
                "chart_config": {
                    "xKey": result.get("xKey"),
                    "yKey": result.get("yKey"),
                }
            }
        else:
            log_info("ℹ️ No se recomienda visualización para estos datos")
            return {"chart_type": None, "chart_config": None}
            
    except Exception as e:
        log_warning(f"Error al analizar datos para gráfico: {e}")
        return {"chart_type": None, "chart_config": None}


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


def validate_and_fix_table_name(sql: str, prompt: str) -> str:
    """
    Valida y corrige el nombre de la tabla en el SQL generado.
    Extrae el nombre correcto del prompt y lo reemplaza si es necesario.
    
    Args:
        sql: SQL generado por el LLM
        prompt: Prompt original que contiene el nombre correcto de la tabla
        
    Returns:
        SQL con el nombre de tabla corregido si era necesario
    """
    import os
    import re
    
    # Extraer el nombre correcto de la tabla del prompt
    # Buscar el patrón: TABLA PRINCIPAL (FACT TABLE): `project.dataset.table`
    table_match = re.search(r'TABLA PRINCIPAL.*?: `([^`]+)`', prompt)
    if not table_match:
        # Fallback: construir desde variables de entorno
        project_id = os.getenv("PROJECT_ID")
        dataset = os.getenv("BQ_DATASET")
        table = os.getenv("BQ_TABLE")
        if all([project_id, dataset, table]):
            correct_table = f"{project_id}.{dataset}.{table}"
        else:
            log_warning("⚠️ No se pudo extraer el nombre correcto de la tabla del prompt")
            return sql
    else:
        correct_table = table_match.group(1)
    
    # Buscar cualquier referencia a la tabla en el SQL
    # Patrón: `project.dataset.table` o project.dataset.table (con o sin backticks)
    # Buscar variaciones comunes del nombre de tabla
    table_patterns = [
        # Con backticks completos
        r'`([^`]+\.(?:Gold|Dim)\.[^`]+)`',
        # Sin backticks
        r'([a-zA-Z0-9\-]+\.[a-zA-Z0-9\-]+\.[a-zA-Z0-9_\-]+)',
    ]
    
    corrected_sql = sql
    for pattern in table_patterns:
        matches = re.finditer(pattern, sql, re.IGNORECASE)
        for match in matches:
            found_table = match.group(1)
            # Si el nombre encontrado no coincide exactamente con el correcto
            if found_table.lower() != correct_table.lower():
                # Verificar si es una variación del nombre correcto (ej: contracts_gold vs contracts_gold_2)
                correct_parts = correct_table.split('.')
                found_parts = found_table.split('.')
                
                # Si el proyecto y dataset coinciden pero la tabla no
                if len(correct_parts) == 3 and len(found_parts) == 3:
                    if correct_parts[0].lower() == found_parts[0].lower() and \
                       correct_parts[1].lower() == found_parts[1].lower() and \
                       correct_parts[2].lower() != found_parts[2].lower():
                        # Reemplazar el nombre incorrecto con el correcto
                        if match.group(0).startswith('`'):
                            replacement = f"`{correct_table}`"
                        else:
                            replacement = correct_table
                        corrected_sql = corrected_sql.replace(match.group(0), replacement)
                        log_warning(f"⚠️ Corregido nombre de tabla en SQL: '{found_table}' → '{correct_table}'")
    
    return corrected_sql

