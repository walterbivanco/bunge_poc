"""
Módulo del Agente LangGraph para NL to SQL
Implementa un agente básico con herramientas estructuradas usando LangGraph
"""
import os
import time
from typing import TypedDict, Optional, List, Dict, Any, Annotated, Sequence
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

from app.db import get_table_schema, get_dimensions_info, execute_query
from app.llm import nl_to_sql, recommend_chart_type
from app.prompts import get_prompt
from app.logger import log_info, log_error, log_warning


# ============================================================================
# Estado del Agente
# ============================================================================

class AgentState(TypedDict):
    """Estado del agente durante la ejecución"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    question: str
    conversation_history: Optional[List[Dict]]
    schema: Optional[str]
    table_full_id: Optional[str]
    dimensions_info: Optional[Dict]
    sql: Optional[str]
    query_result: Optional[Dict]
    chart_recommendation: Optional[Dict]
    error: Optional[str]
    steps: List[Dict]
    request_id: str


# ============================================================================
# Herramientas del Agente
# ============================================================================

@tool
def get_schema_tool() -> str:
    """
    Obtiene el schema de la tabla principal de BigQuery.
    Esta herramienta debe ser llamada primero para obtener la estructura de la tabla.
    
    Returns:
        JSON string con 'schema' (texto del schema) y 'table_id' (ID completo de la tabla)
    """
    import json
    try:
        log_info("🔧 [Tool] Obteniendo schema de BigQuery...")
        schema_text, table_id = get_table_schema(use_cache=True)
        log_info(f"✅ [Tool] Schema obtenido: {table_id}")
        result = {
            "schema": schema_text,
            "table_id": table_id,
            "success": True
        }
        return json.dumps(result)
    except Exception as e:
        log_error(f"❌ [Tool] Error obteniendo schema", e)
        result = {
            "schema": None,
            "table_id": None,
            "success": False,
            "error": str(e)
        }
        return json.dumps(result)


@tool
def get_dimensions_tool() -> str:
    """
    Obtiene información de las tablas de dimensiones disponibles.
    Estas tablas contienen información descriptiva (nombres, descripciones) que se pueden usar en JOINs.
    
    Returns:
        JSON string con información de dimensiones o None si no hay disponibles
    """
    import json
    try:
        log_info("🔧 [Tool] Obteniendo información de dimensiones...")
        dimensions_info = get_dimensions_info(use_cache=True, force_refresh=False)
        
        if dimensions_info.get("dimensions") and len(dimensions_info["dimensions"]) > 0:
            dim_names = list(dimensions_info["dimensions"].keys())
            log_info(f"✅ [Tool] {len(dim_names)} tablas de dimensiones disponibles: {', '.join(dim_names)}")
            result = {
                "dimensions": dimensions_info,
                "success": True,
                "count": len(dimensions_info["dimensions"])
            }
        else:
            log_info("ℹ️  [Tool] Sin tablas de dimensiones disponibles")
            result = {
                "dimensions": None,
                "success": True,
                "count": 0
            }
        return json.dumps(result)
    except Exception as e:
        log_warning(f"⚠️  [Tool] Error obteniendo dimensiones: {e}")
        result = {
            "dimensions": None,
            "success": False,
            "error": str(e)
        }
        return json.dumps(result)


@tool
def generate_sql_tool(
    question: str,
    schema: str,
    table_id: str,
    dimensions_info: Optional[str] = None,
    conversation_history: Optional[str] = None
) -> str:
    """
    Genera SQL desde una pregunta en lenguaje natural usando Gemini.
    
    Args:
        question: Pregunta del usuario en lenguaje natural
        schema: Schema de la tabla principal (obtenido con get_schema_tool, como JSON string)
        table_id: ID completo de la tabla (project.dataset.table)
        dimensions_info: Información de tablas de dimensiones (opcional, como JSON string)
        conversation_history: Historial de conversación anterior (opcional, como JSON string)
    
    Returns:
        JSON string con 'sql' generado y metadata
    """
    import json
    try:
        log_info(f"🔧 [Tool] Generando SQL para: {question[:50]}...")
        
        # Parsear inputs JSON
        schema_data = json.loads(schema) if isinstance(schema, str) else schema
        schema_text = schema_data.get("schema") if isinstance(schema_data, dict) else schema
        
        dim_info = None
        if dimensions_info:
            dim_data = json.loads(dimensions_info) if isinstance(dimensions_info, str) else dimensions_info
            dim_info = dim_data.get("dimensions") if isinstance(dim_data, dict) else dim_data
        
        conv_history = None
        if conversation_history:
            conv_history = json.loads(conversation_history) if isinstance(conversation_history, str) else conversation_history
        
        # Extraer project_id, dataset, table del table_id
        parts = table_id.split('.')
        if len(parts) != 3:
            raise ValueError(f"table_id debe tener formato project.dataset.table, recibido: {table_id}")
        
        project_id, dataset, table = parts
        
        # Construir prompt
        prompt = get_prompt(
            question=question,
            schema=schema_text,
            project_id=project_id,
            dataset=dataset,
            table=table,
            dimensions_info=dim_info,
            conversation_history=conv_history
        )
        
        # Generar SQL
        llm_result = nl_to_sql(prompt)
        sql = llm_result['sql']
        
        log_info(f"✅ [Tool] SQL generado: {sql[:100]}...")
        
        result = {
            "sql": sql,
            "success": True,
            "duration_ms": llm_result.get('duration_ms'),
            "tokens_used": llm_result.get('tokens_used'),
            "model_used": llm_result.get('model_used')
        }
        return json.dumps(result)
    except Exception as e:
        log_error(f"❌ [Tool] Error generando SQL", e)
        result = {
            "sql": None,
            "success": False,
            "error": str(e)
        }
        return json.dumps(result)


@tool
def execute_query_tool(sql: str, max_rows: int = 100) -> str:
    """
    Ejecuta una consulta SQL en BigQuery.
    
    Args:
        sql: Consulta SQL a ejecutar (puede venir como JSON string con campo "sql" o directamente)
        max_rows: Número máximo de filas a retornar (default: 100)
    
    Returns:
        JSON string con resultados de la consulta (columns, rows, total_rows, etc.)
    """
    import json
    try:
        log_info(f"🔧 [Tool] Ejecutando SQL en BigQuery...")
        
        # Parsear SQL si viene como JSON
        sql_query = sql
        if isinstance(sql, str) and sql.strip().startswith("{"):
            try:
                sql_data = json.loads(sql)
                sql_query = sql_data.get("sql", sql)
            except:
                pass
        
        log_info(f"SQL: {sql_query[:200]}...")
        
        result = execute_query(sql_query, max_rows=max_rows)
        
        log_info(f"✅ [Tool] Query ejecutado: {result['total_rows']} filas retornadas")
        
        output = {
            "success": True,
            "columns": result.get("columns", []),
            "rows": result.get("rows", []),
            "total_rows": result.get("total_rows", 0),
            "bytes_processed": result.get("bytes_processed")
        }
        return json.dumps(output)
    except Exception as e:
        log_error(f"❌ [Tool] Error ejecutando query", e)
        output = {
            "success": False,
            "error": str(e),
            "columns": [],
            "rows": [],
            "total_rows": 0
        }
        return json.dumps(output)


@tool
def recommend_chart_tool(
    question: str,
    columns: str,
    rows: str,
    max_rows_sample: int = 20
) -> str:
    """
    Analiza los resultados de una consulta y recomienda el tipo de gráfico más apropiado.
    
    Args:
        question: Pregunta original del usuario
        columns: Lista de nombres de columnas (como JSON string)
        rows: Lista de filas de datos (como JSON string)
        max_rows_sample: Número máximo de filas a analizar (default: 20)
    
    Returns:
        JSON string con 'chart_type' y 'chart_config' o None si no se recomienda gráfico
    """
    import json
    try:
        # Parsear inputs JSON
        cols = json.loads(columns) if isinstance(columns, str) else columns
        rws = json.loads(rows) if isinstance(rows, str) else rows
        
        if not cols or not rws or len(rws) == 0:
            result = {
                "success": True,
                "chart_type": None,
                "chart_config": None
            }
            return json.dumps(result)
        
        log_info(f"🔧 [Tool] Analizando datos para recomendación de gráfico...")
        
        recommendation = recommend_chart_type(
            question=question,
            columns=cols,
            rows=rws,
            max_rows_sample=max_rows_sample
        )
        
        chart_type = recommendation.get("chart_type")
        if chart_type:
            log_info(f"✅ [Tool] Gráfico recomendado: {chart_type}")
        else:
            log_info("ℹ️  [Tool] No se recomienda visualización para estos datos")
        
        result = {
            "success": True,
            "chart_type": chart_type,
            "chart_config": recommendation.get("chart_config")
        }
        return json.dumps(result)
    except Exception as e:
        log_warning(f"⚠️  [Tool] Error recomendando gráfico: {e}")
        result = {
            "success": False,
            "chart_type": None,
            "chart_config": None,
            "error": str(e)
        }
        return json.dumps(result)


# Lista de todas las herramientas disponibles
TOOLS = [
    get_schema_tool,
    get_dimensions_tool,
    generate_sql_tool,
    execute_query_tool,
    recommend_chart_tool
]


# ============================================================================
# Nodos del Grafo
# ============================================================================

def start_node(state: AgentState) -> AgentState:
    """Nodo inicial: prepara el estado del agente"""
    request_id = state.get("request_id", "unknown")
    log_info(f"[{request_id}] 🚀 Iniciando agente LangGraph")
    
    # Inicializar mensajes si no existen
    if "messages" not in state or not state["messages"]:
        state["messages"] = [HumanMessage(content=state["question"])]
    
    # Inicializar steps si no existe
    if "steps" not in state:
        state["steps"] = []
    
    return state


def agent_node(state: AgentState, model: ChatVertexAI) -> AgentState:
    """
    Nodo principal del agente: el LLM decide qué herramienta usar
    """
    request_id = state.get("request_id", "unknown")
    log_info(f"[{request_id}] 🤖 Agente decidiendo siguiente acción...")
    
    messages = state.get("messages", [])
    
    # Llamar al modelo con las herramientas disponibles
    response = model.invoke(messages)
    
    # Agregar respuesta del agente al estado
    state["messages"] = list(messages) + [response]
    
    return state


def should_continue(state: AgentState) -> str:
    """
    Función de enrutamiento: decide si continuar con herramientas o finalizar
    """
    request_id = state.get("request_id", "unknown")
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None
    
    # Si el último mensaje tiene tool_calls, ejecutar herramientas
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        log_info(f"[{request_id}] 🔧 Agente decidió usar herramientas: {[tc['name'] for tc in last_message.tool_calls]}")
        return "tools"
    
    # Si no hay tool_calls, finalizar
    log_info(f"[{request_id}] ✅ Agente completó sin más herramientas")
    return "end"


def finalize_node(state: AgentState) -> AgentState:
    """
    Nodo final: prepara la respuesta final del agente
    """
    request_id = state.get("request_id", "unknown")
    log_info(f"[{request_id}] 📦 Finalizando respuesta del agente...")
    
    messages = state.get("messages", [])
    
    # Extraer información del estado y mensajes
    # Buscar resultados de herramientas en los mensajes
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            # Los resultados de herramientas están en ToolMessage
            # Extraer información relevante según la herramienta usada
            pass
    
    # El estado ya tiene toda la información necesaria
    return state


# ============================================================================
# Construcción del Grafo
# ============================================================================

def create_agent_graph() -> StateGraph:
    """
    Crea y retorna el grafo del agente LangGraph
    """
    # Inicializar el modelo LLM con Vertex AI Gemini
    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("VERTEX_LOCATION", "us-central1")
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    model = ChatVertexAI(
        model_name=model_name,
        project=project_id,
        location=location,
        temperature=0,
        max_tokens=1024,
    )
    
    # Bindear herramientas al modelo
    model_with_tools = model.bind_tools(TOOLS)
    
    # Crear grafo
    workflow = StateGraph(AgentState)
    
    # Agregar nodos
    workflow.add_node("start", start_node)
    workflow.add_node("agent", lambda state: agent_node(state, model_with_tools))
    workflow.add_node("tools", ToolNode(TOOLS))
    workflow.add_node("finalize", finalize_node)
    
    # Definir edges
    workflow.set_entry_point("start")
    workflow.add_edge("start", "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": "finalize"
        }
    )
    workflow.add_edge("tools", "agent")  # Después de ejecutar herramientas, volver al agente
    workflow.add_edge("finalize", END)
    
    return workflow.compile()


# ============================================================================
# Función Principal para Ejecutar el Agente
# ============================================================================

def run_agent(
    question: str,
    conversation_history: Optional[List[Dict]] = None,
    request_id: str = "unknown"
) -> Dict[str, Any]:
    """
    Ejecuta el agente LangGraph para procesar una pregunta y generar resultados.
    
    Por ahora, usa un enfoque simplificado que ejecuta las herramientas en secuencia
    pero usando LangGraph como orquestador. Esto asegura compatibilidad mientras
    el agente se ajusta para tomar decisiones más inteligentes.
    
    Args:
        question: Pregunta del usuario en lenguaje natural
        conversation_history: Historial de conversación anterior (opcional)
        request_id: ID único del request para logging
    
    Returns:
        Dict con los resultados: sql, columns, rows, total_rows, chart_type, chart_config, etc.
    """
    start_time = time.time()
    log_info(f"[{request_id}] 🎯 Ejecutando agente LangGraph para: {question[:50]}...")
    
    try:
        # Por ahora, usar flujo secuencial pero estructurado con herramientas
        # Esto permite migración gradual a un agente más inteligente
        steps = []
        
        # Paso 1: Obtener schema
        step_start = time.time()
        log_info(f"[{request_id}] Paso 1: Obteniendo schema...")
        schema_result_str = get_schema_tool.invoke({})
        import json
        schema_result = json.loads(schema_result_str)
        schema = schema_result.get("schema")
        table_full_id = schema_result.get("table_id")
        step_duration = (time.time() - step_start) * 1000
        steps.append({"name": "Get Schema", "duration_ms": step_duration})
        
        if not schema:
            raise Exception("No se pudo obtener el schema de la tabla")
        
        # Paso 2: Obtener dimensiones (opcional)
        step_start = time.time()
        log_info(f"[{request_id}] Paso 2: Obteniendo dimensiones...")
        dim_result_str = get_dimensions_tool.invoke({})
        dim_result = json.loads(dim_result_str)
        dimensions_info = dim_result.get("dimensions") if dim_result.get("success") else None
        step_duration = (time.time() - step_start) * 1000
        steps.append({"name": "Get Dimensions", "duration_ms": step_duration})
        
        # Paso 3: Generar SQL
        step_start = time.time()
        log_info(f"[{request_id}] Paso 3: Generando SQL...")
        # Preparar inputs para generate_sql_tool
        schema_json = json.dumps({"schema": schema, "table_id": table_full_id})
        dim_json = json.dumps({"dimensions": dimensions_info}) if dimensions_info else None
        conv_json = json.dumps(conversation_history) if conversation_history else None
        
        sql_result_str = generate_sql_tool.invoke({
            "question": question,
            "schema": schema_json,
            "table_id": table_full_id,
            "dimensions_info": dim_json,
            "conversation_history": conv_json
        })
        sql_result = json.loads(sql_result_str)
        sql = sql_result.get("sql")
        step_duration = (time.time() - step_start) * 1000
        steps.append({"name": "Generate SQL", "duration_ms": step_duration})
        
        if not sql:
            raise Exception(f"Error generando SQL: {sql_result.get('error', 'Unknown error')}")
        
        # Paso 4: Ejecutar query
        step_start = time.time()
        log_info(f"[{request_id}] Paso 4: Ejecutando query...")
        query_result_str = execute_query_tool.invoke({"sql": sql})
        query_result = json.loads(query_result_str)
        step_duration = (time.time() - step_start) * 1000
        steps.append({"name": "Execute Query", "duration_ms": step_duration})
        
        if not query_result.get("success"):
            raise Exception(f"Error ejecutando query: {query_result.get('error', 'Unknown error')}")
        
        # Paso 5: Recomendar chart (opcional, solo si hay resultados)
        chart_recommendation = None
        if query_result.get("total_rows", 0) > 0 and query_result.get("total_rows", 0) <= 100:
            step_start = time.time()
            log_info(f"[{request_id}] Paso 5: Recomendando gráfico...")
            chart_result_str = recommend_chart_tool.invoke({
                "question": question,
                "columns": json.dumps(query_result.get("columns", [])),
                "rows": json.dumps(query_result.get("rows", []))
            })
            chart_result = json.loads(chart_result_str)
            chart_recommendation = chart_result if chart_result.get("success") else None
            step_duration = (time.time() - step_start) * 1000
            steps.append({"name": "Recommend Chart", "duration_ms": step_duration})
        
        # Preparar respuesta final
        total_time_ms = (time.time() - start_time) * 1000
        
        result = {
            "sql": sql,
            "columns": query_result.get("columns", []),
            "rows": query_result.get("rows", []),
            "total_rows": query_result.get("total_rows", 0),
            "chart_type": chart_recommendation.get("chart_type") if chart_recommendation else None,
            "chart_config": chart_recommendation.get("chart_config") if chart_recommendation else None,
            "duration_ms": total_time_ms,
            "steps": steps
        }
        
        log_info(f"[{request_id}] ✅ Agente completado en {total_time_ms/1000:.2f}s")
        return result
        
    except Exception as e:
        log_error(f"[{request_id}] ❌ Error ejecutando agente", e)
        # Fallback al flujo tradicional
        log_info(f"[{request_id}] 🔄 Usando flujo tradicional como fallback...")
        return _fallback_traditional_flow(question, conversation_history, request_id)


def _fallback_traditional_flow(
    question: str,
    conversation_history: Optional[List[Dict]],
    request_id: str
) -> Dict[str, Any]:
    """
    Flujo tradicional como fallback si el agente falla
    """
    log_info(f"[{request_id}] 🔄 Usando flujo tradicional como fallback...")
    
    # Obtener schema
    schema_text, table_full_id = get_table_schema()
    
    # Obtener dimensiones
    dimensions_info = None
    try:
        dimensions_info = get_dimensions_info(force_refresh=False)
        if not dimensions_info.get("dimensions"):
            dimensions_info = None
    except:
        pass
    
    # Construir prompt
    project_id = os.getenv("PROJECT_ID")
    dataset = os.getenv("BQ_DATASET")
    table = os.getenv("BQ_TABLE")
    
    prompt = get_prompt(
        question=question,
        schema=schema_text,
        project_id=project_id,
        dataset=dataset,
        table=table,
        dimensions_info=dimensions_info,
        conversation_history=conversation_history
    )
    
    # Generar SQL
    llm_result = nl_to_sql(prompt)
    sql = llm_result['sql']
    
    # Ejecutar query
    bq_result = execute_query(sql)
    
    # Recomendar chart
    chart_recommendation = None
    if bq_result["total_rows"] > 0 and bq_result["total_rows"] <= 100:
        try:
            chart_recommendation = recommend_chart_type(
                question=question,
                columns=bq_result["columns"],
                rows=bq_result["rows"]
            )
        except:
            pass
    
    return {
        "sql": sql,
        "columns": bq_result["columns"],
        "rows": bq_result["rows"],
        "total_rows": bq_result["total_rows"],
        "chart_type": chart_recommendation.get("chart_type") if chart_recommendation else None,
        "chart_config": chart_recommendation.get("chart_config") if chart_recommendation else None,
        "duration_ms": 0,  # Se calculará en main.py
        "steps": []
    }
