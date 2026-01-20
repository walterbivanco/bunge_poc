"""
Módulo para ejecutar queries SQL en BigQuery
"""
import os
import time
from google.cloud import bigquery
from typing import Dict, List, Any, Tuple
from app.logger import log_info, log_error, log_warning

# ⚡ Caché del schema para evitar consultas repetidas a BigQuery
# Límites de memoria: máximo 50 schemas en caché
_MAX_SCHEMA_CACHE_SIZE = 50
_SCHEMA_CACHE: Dict[str, str] = {}
_DIMENSIONS_CACHE: Dict[str, Dict[str, str]] = {}
_DIMENSIONS_NOT_FOUND_CACHE: set = set()  # Cachear tablas que no existen para no intentar cargarlas repetidamente
_MAX_DIMENSIONS_NOT_FOUND_CACHE_SIZE = 100  # Máximo 100 tablas "no encontradas" en caché


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
        
        # ⚡ Guardar en caché con límite de memoria
        # Si el caché está lleno, eliminar el más antiguo (FIFO)
        if len(_SCHEMA_CACHE) >= _MAX_SCHEMA_CACHE_SIZE:
            # Eliminar el primer elemento (más antiguo)
            oldest_key = next(iter(_SCHEMA_CACHE))
            del _SCHEMA_CACHE[oldest_key]
            log_info(f"🧹 Cache de schemas lleno, eliminado: {oldest_key}")
        
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


def get_dimensions_info(use_cache: bool = True, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Obtiene información de las tablas de dimensiones y sus relaciones
    
    Args:
        use_cache: Si True, usa el caché (por defecto). Si False, fuerza recarga.
        force_refresh: Si True, fuerza recarga ignorando cache de "no encontradas"
    
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
    # Dataset de dimensiones puede ser diferente al dataset de la fact table
    dim_dataset = os.getenv("BQ_DIM_DATASET", "Dim")  # Por defecto "Dim"
    fact_dataset = os.getenv("BQ_DATASET")  # Dataset de la fact table
    
    if not all([project_id, fact_dataset]):
        raise ValueError("Faltan configurar variables: PROJECT_ID, BQ_DATASET")
    
    cache_key = f"{project_id}.{dim_dataset}"
    
    # Si se fuerza refresh, limpiar cache de "no encontradas" para este dataset
    if force_refresh:
        # Limpiar cache de tablas no encontradas para este dataset
        tables_to_remove = [t for t in _DIMENSIONS_NOT_FOUND_CACHE if f"{project_id}.{dataset}" in t]
        for t in tables_to_remove:
            _DIMENSIONS_NOT_FOUND_CACHE.discard(t)
        # Limpiar cache de dimensiones también
        if cache_key in _DIMENSIONS_CACHE:
            del _DIMENSIONS_CACHE[cache_key]
    
    # ⚡ Verificar caché primero
    if use_cache and cache_key in _DIMENSIONS_CACHE and not force_refresh:
        cached_result = _DIMENSIONS_CACHE[cache_key]
        # Solo loguear si hay dimensiones disponibles, si no hay, ser silencioso
        if cached_result.get("dimensions") and len(cached_result["dimensions"]) > 0:
            log_info(f"✨ Dimensiones obtenidas desde caché ({len(cached_result['dimensions'])} tablas)")
        return cached_result
    
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
        # Las tablas de dimensiones están en el dataset "Dim", no en el dataset de la fact table
        table_id = f"{project_id}.{dim_dataset}.{dim_table}"
        
        # Si ya sabemos que esta tabla no existe, saltarla silenciosamente
        if table_id in _DIMENSIONS_NOT_FOUND_CACHE:
            continue
        
        try:
            schema_text = _get_single_table_schema(table_id, use_cache)
            dimensions[dim_name] = {
                "table_id": table_id,
                "table_name": dim_table,
                "schema": schema_text
            }
            log_info(f"✅ Schema de {dim_name} obtenido")
        except Exception as e:
            from google.api_core import exceptions as gcp_exceptions
            
            error_str = str(e)
            error_type = type(e).__name__
            
            # Detectar tipo específico de error
            if isinstance(e, gcp_exceptions.NotFound) or "404" in error_str or "Not found" in error_str or "notFound" in error_str:
                # Tabla no encontrada
                if table_id not in _DIMENSIONS_NOT_FOUND_CACHE:
                    # Limpiar caché si está lleno (FIFO)
                    if len(_DIMENSIONS_NOT_FOUND_CACHE) >= _MAX_DIMENSIONS_NOT_FOUND_CACHE_SIZE:
                        # Eliminar el primer elemento
                        oldest = next(iter(_DIMENSIONS_NOT_FOUND_CACHE))
                        _DIMENSIONS_NOT_FOUND_CACHE.discard(oldest)
                    
                    _DIMENSIONS_NOT_FOUND_CACHE.add(table_id)
                    log_warning(f"⚠️ Tabla de dimensión {dim_name} no encontrada")
                    log_warning(f"   ID buscado: {table_id}")
                    log_warning(f"   Verifica:")
                    log_warning(f"     1. Que la tabla exista en BigQuery Console")
                    log_warning(f"     2. Que el nombre sea exacto: '{dim_table}'")
                    log_warning(f"     3. Que esté en el dataset: {dataset}")
                    log_warning(f"     4. Ejecuta: python backend/check_dimensions.py para diagnóstico")
                if force_refresh:
                    _DIMENSIONS_NOT_FOUND_CACHE.discard(table_id)
            elif isinstance(e, gcp_exceptions.PermissionDenied) or "403" in error_str or "Permission" in error_str:
                # Error de permisos
                log_warning(f"⚠️ Permisos insuficientes para {dim_name} ({table_id})")
                log_warning(f"   Verifica que tengas permisos de lectura en BigQuery")
                log_warning(f"   Error: {error_str[:100]}")
            else:
                # Otro tipo de error
                log_warning(f"⚠️ Error obteniendo schema de {dim_name} ({table_id})")
                log_warning(f"   Tipo: {error_type}")
                log_warning(f"   Error: {error_str[:150]}")
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
    
    # Solo loguear si hay dimensiones, si no hay, ser más silencioso
    if len(dimensions) > 0:
        log_info(f"Dimensiones cargadas en {duration_ms/1000:.2f}s ({len(dimensions)} tablas)")
    # Si no hay dimensiones, no loguear nada (ya se mostraron warnings individuales)
    
    return result


def clear_dimensions_cache():
    """Limpia el cache de dimensiones - útil para forzar recarga"""
    global _DIMENSIONS_CACHE, _DIMENSIONS_NOT_FOUND_CACHE
    _DIMENSIONS_CACHE.clear()
    _DIMENSIONS_NOT_FOUND_CACHE.clear()
    log_info("🧹 Cache de dimensiones limpiado")


def clear_all_caches():
    """Limpia todos los cachés para liberar memoria"""
    global _SCHEMA_CACHE, _DIMENSIONS_CACHE, _DIMENSIONS_NOT_FOUND_CACHE
    schema_count = len(_SCHEMA_CACHE)
    dim_count = len(_DIMENSIONS_CACHE)
    not_found_count = len(_DIMENSIONS_NOT_FOUND_CACHE)
    
    _SCHEMA_CACHE.clear()
    _DIMENSIONS_CACHE.clear()
    _DIMENSIONS_NOT_FOUND_CACHE.clear()
    
    log_info(f"🧹 Todos los cachés limpiados: {schema_count} schemas, {dim_count} dimensiones, {not_found_count} 'no encontradas'")


def get_cache_stats() -> Dict[str, Any]:
    """Obtiene estadísticas de los cachés para monitoreo de memoria"""
    return {
        "schema_cache_size": len(_SCHEMA_CACHE),
        "schema_cache_max": _MAX_SCHEMA_CACHE_SIZE,
        "dimensions_cache_size": len(_DIMENSIONS_CACHE),
        "dimensions_not_found_cache_size": len(_DIMENSIONS_NOT_FOUND_CACHE),
        "dimensions_not_found_cache_max": _MAX_DIMENSIONS_NOT_FOUND_CACHE_SIZE
    }


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

