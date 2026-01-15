"""
Módulo para ejecutar queries SQL en BigQuery
"""
import os
import time
from google.cloud import bigquery
from typing import Dict, List, Any, Tuple
from app.logger import log_info, log_error, log_warning

# ⚡ Caché del schema para evitar consultas repetidas a BigQuery
_SCHEMA_CACHE: Dict[str, str] = {}
_DIMENSIONS_CACHE: Dict[str, Dict[str, str]] = {}


def get_bigquery_client() -> bigquery.Client:
    """
    Crea y retorna un cliente de BigQuery
    
    Returns:
        Cliente configurado de BigQuery
    """
    project_id = os.getenv("PROJECT_ID")
    if not project_id:
        raise ValueError("PROJECT_ID no está configurado")
    
    return bigquery.Client(project=project_id)


def _get_single_table_schema(table_id: str, use_cache: bool = True) -> str:
    """
    Obtiene el schema de una tabla específica en formato texto
    
    Args:
        table_id: ID completo de la tabla (project.dataset.table)
        use_cache: Si True, usa el caché del schema
    
    Returns:
        Schema en formato texto compacto
    """
    # ⚡ Verificar caché primero
    if use_cache and table_id in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[table_id]
    
    # Si no está en caché, consultar BigQuery
    client = get_bigquery_client()
    
    try:
        bq_table = client.get_table(table_id)
        
        # ⚡ Formatear schema de forma ultra-compacta para Gemini
        schema_parts = []
        for field in bq_table.schema:
            # Formato compacto: nombre:tipo (sin mode info extra)
            schema_parts.append(f"{field.name}:{field.field_type}")
        
        # Unir todo en una sola línea separado por comas
        schema_text = ", ".join(schema_parts)
        
        # ⚡ Guardar en caché
        _SCHEMA_CACHE[table_id] = schema_text
        
        return schema_text
        
    except Exception as e:
        raise Exception(f"Error obteniendo schema de {table_id}: {str(e)}")


def get_table_schema(use_cache: bool = True) -> Tuple[str, str]:
    """
    Obtiene el schema de la tabla configurada en formato texto con caché
    
    Args:
        use_cache: Si True, usa el caché del schema (por defecto). Si False, fuerza recarga.
    
    Returns:
        Tupla con (schema_texto, table_full_id)
    """
    project_id = os.getenv("PROJECT_ID")
    dataset = os.getenv("BQ_DATASET")
    table = os.getenv("BQ_TABLE")
    
    if not all([project_id, dataset, table]):
        raise ValueError("Faltan configurar variables: PROJECT_ID, BQ_DATASET, BQ_TABLE")
    
    table_id = f"{project_id}.{dataset}.{table}"
    
    start_time = time.time()
    log_info(f"📋 Obteniendo schema de BigQuery...")
    
    schema_text = _get_single_table_schema(table_id, use_cache)
    
    duration_ms = (time.time() - start_time) * 1000
    log_info(f"Schema obtenido en {duration_ms/1000:.2f}s")
    
    return schema_text, table_id


def get_dimensions_info(use_cache: bool = True) -> Dict[str, Any]:
    """
    Obtiene información de las tablas de dimensiones y sus relaciones
    
    Args:
        use_cache: Si True, usa el caché (por defecto). Si False, fuerza recarga.
    
    Returns:
        Dict con información de dimensiones:
        {
            "dimensions": {
                "DimProducts": {"table_id": "...", "schema": "..."},
                "DimProvince": {"table_id": "...", "schema": "..."},
                "DimTime": {"table_id": "...", "schema": "..."}
            },
            "relationships": [
                {"fact_column": "product_id", "dim_table": "DimProducts", "dim_column": "product_id"},
                {"fact_column": "province_id", "dim_table": "DimProvince", "dim_column": "province_id"},
                {"fact_column": "agreement_date", "dim_table": "DimTime", "dim_column": "date_id"}
            ]
        }
    """
    project_id = os.getenv("PROJECT_ID")
    dataset = os.getenv("BQ_DATASET")
    
    if not all([project_id, dataset]):
        raise ValueError("Faltan configurar variables: PROJECT_ID, BQ_DATASET")
    
    cache_key = f"{project_id}.{dataset}"
    
    # ⚡ Verificar caché primero
    if use_cache and cache_key in _DIMENSIONS_CACHE:
        log_info(f"✨ Dimensiones obtenidas desde caché (instantáneo)")
        return _DIMENSIONS_CACHE[cache_key]
    
    start_time = time.time()
    log_info(f"📋 Obteniendo schemas de tablas de dimensiones...")
    
    # Definir tablas de dimensiones (pueden ser configuradas por env vars en el futuro)
    dim_tables = {
        "DimProducts": os.getenv("BQ_DIM_PRODUCTS", "DimProducts"),
        "DimProvince": os.getenv("BQ_DIM_PROVINCE", "DimProvince"),
        "DimTime": os.getenv("BQ_DIM_TIME", "DimTime")
    }
    
    dimensions = {}
    client = get_bigquery_client()
    
    for dim_name, dim_table in dim_tables.items():
        table_id = f"{project_id}.{dataset}.{dim_table}"
        try:
            schema_text = _get_single_table_schema(table_id, use_cache)
            dimensions[dim_name] = {
                "table_id": table_id,
                "table_name": dim_table,
                "schema": schema_text
            }
            log_info(f"✅ Schema de {dim_name} obtenido")
        except Exception as e:
            log_warning(f"⚠️ No se pudo obtener schema de {dim_name} ({table_id}): {e}")
            # Continuar con las otras dimensiones aunque una falle
    
    # Definir relaciones (hardcodeadas según la especificación)
    relationships = [
        {
            "fact_column": "product_id",
            "dim_table": "DimProducts",
            "dim_column": "product_id"
        },
        {
            "fact_column": "province_id",
            "dim_table": "DimProvince",
            "dim_column": "province_id"
        },
        {
            "fact_column": "agreement_date",
            "dim_table": "DimTime",
            "dim_column": "date_id"
        }
    ]
    
    result = {
        "dimensions": dimensions,
        "relationships": relationships
    }
    
    # ⚡ Guardar en caché
    _DIMENSIONS_CACHE[cache_key] = result
    
    duration_ms = (time.time() - start_time) * 1000
    log_info(f"Dimensiones cargadas en {duration_ms/1000:.2f}s ({len(dimensions)} tablas)")
    
    return result


def execute_query(sql: str, max_rows: int = 100) -> Dict[str, Any]:
    """
    Ejecuta una query SQL en BigQuery y retorna los resultados
    
    Args:
        sql: Query SQL a ejecutar
        max_rows: Máximo número de filas a retornar
        
    Returns:
        Dict con:
            - columns: lista de nombres de columnas
            - rows: lista de listas con los valores
            - total_rows: número total de filas retornadas
            - duration_ms: tiempo de ejecución
            - bytes_processed: bytes procesados por BigQuery
            
    Raises:
        Exception: Si hay error en la ejecución
    """
    start_time = time.time()
    log_info(f"🔵 [BQ] Inicio execute_query")
    
    client_start = time.time()
    client = get_bigquery_client()
    log_info(f"🔵 [BQ] Cliente obtenido en {(time.time()-client_start):.3f}s")
    
    log_info(f"Ejecutando query en BigQuery (max {max_rows} rows)")
    log_info(f"Query: {sql[:100]}..." if len(sql) > 100 else f"Query: {sql}")
    
    try:
        # Ejecutar la query
        query_start = time.time()
        log_info(f"🔵 [BQ] Enviando query a BigQuery...")
        query_job = client.query(sql)
        log_info(f"🔵 [BQ] Query enviada, esperando resultados...")
        results = query_job.result(max_results=max_rows)
        log_info(f"🔵 [BQ] Resultados recibidos en {(time.time()-query_start):.3f}s")
        
        # Extraer columnas
        columns = [field.name for field in results.schema]
        
        # Extraer filas
        rows = []
        for row in results:
            # Convertir cada fila a lista (manejando tipos especiales)
            row_list = []
            for value in row.values():
                # Convertir tipos especiales a strings
                if hasattr(value, 'isoformat'):  # Fechas/timestamps
                    row_list.append(value.isoformat())
                elif value is None:
                    row_list.append(None)
                else:
                    row_list.append(str(value) if not isinstance(value, (int, float, bool)) else value)
            rows.append(row_list)
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Obtener estadísticas del job
        bytes_processed = None
        if query_job.done():
            bytes_processed = query_job.total_bytes_processed
            if bytes_processed:
                log_info(f"Bytes procesados: {bytes_processed:,} ({bytes_processed / 1024 / 1024:.2f} MB)")
        
        log_info(f"Query ejecutada exitosamente en {duration_ms/1000:.2f}s")
        log_info(f"Filas retornadas: {len(rows)}")
        
        return {
            "columns": columns,
            "rows": rows,
            "total_rows": len(rows),
            "duration_ms": duration_ms,
            "bytes_processed": bytes_processed
        }
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        log_error(f"Error ejecutando query después de {duration_ms/1000:.2f}s", e)
        raise Exception(f"Error ejecutando query en BigQuery: {str(e)}")


def test_connection() -> bool:
    """
    Prueba la conexión a BigQuery con una query simple
    
    Returns:
        True si la conexión funciona
    """
    try:
        client = get_bigquery_client()
        query = "SELECT 1 as test"
        results = list(client.query(query).result())
        return len(results) > 0
    except Exception:
        return False

