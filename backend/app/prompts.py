"""
Prompts para la generación de SQL desde lenguaje natural
"""
import os

# ⚡ Prompt ultra-optimizado para respuesta rápida
BASE_PROMPT = """Convierte esta pregunta a SQL de BigQuery. Responde SOLO con el SQL, sin explicaciones.

TABLA PRINCIPAL (FACT TABLE): `{project_id}.{dataset}.{table}`
⚠️ CRÍTICO: DEBES usar EXACTAMENTE este nombre de tabla: `{project_id}.{dataset}.{table}` - NO lo modifiques, NO lo cambies, úsalo tal cual está escrito aquí.

COLUMNAS DE LA TABLA PRINCIPAL:
{schema}
{dimensions_info}
REGLAS CRÍTICAS:
- Solo SELECT (nunca INSERT/UPDATE/DELETE)
- ⚠️ USA EXACTAMENTE el nombre de tabla: `{project_id}.{dataset}.{table}` - NO inventes nombres, NO uses variaciones
{dimension_rules}
- Usa solo columnas de los schemas proporcionados
- Agrega LIMIT 100
- Sin markdown ni explicaciones
{conversation_context}

PREGUNTA ACTUAL: {question}

SQL:"""


def get_prompt(
    question: str, 
    schema: str, 
    project_id: str, 
    dataset: str, 
    table: str,
    dimensions_info: dict = None,
    conversation_history: list = None
) -> str:
    """
    Construye el prompt completo para enviar a Gemini
    
    Args:
        question: Pregunta en lenguaje natural del usuario
        schema: Schema de la tabla principal (columnas con tipos)
        project_id: ID del proyecto GCP
        dataset: Dataset de BigQuery
        table: Nombre de la tabla principal
        dimensions_info: Dict con información de tablas de dimensiones (opcional)
        conversation_history: Lista de mensajes anteriores para contexto (opcional)
        
    Returns:
        Prompt formateado listo para enviar al LLM
    """
    # Construir información de dimensiones si está disponible Y existen tablas
    dim_text = ""
    dimension_rules = ""
    
    # Solo incluir dimensiones si realmente existen tablas cargadas
    if dimensions_info and dimensions_info.get("dimensions") and len(dimensions_info["dimensions"]) > 0:
        table_full = f"{project_id}.{dataset}.{table}"
        dim_text = "\n\n⚠️ TABLAS DE DIMENSIONES DISPONIBLES - IMPORTANTE: Si la pregunta menciona 'nombre', 'name', o información descriptiva, DEBES hacer JOIN:\n"
        
        for dim_name, dim_data in dimensions_info["dimensions"].items():
            dim_text += f"\n{dim_name} (`{dim_data['table_id']}`):\n"
            dim_text += f"  Columnas: {dim_data['schema']}\n"
        
        # Solo incluir relaciones para tablas que realmente existen
        available_dim_tables = set(dimensions_info["dimensions"].keys())
        dim_text += "\n🔗 RELACIONES PARA JOINs (OBLIGATORIO cuando se piden nombres):\n"
        # Obtener dataset de dimensiones (puede ser diferente al de la fact table)
        dim_dataset = os.getenv("BQ_DIM_DATASET", "Dim")
        
        for rel in dimensions_info.get("relationships", []):
            # Solo incluir relación si la tabla de dimensión existe
            if rel['dim_table'] in available_dim_tables:
                dim_table_full = f"{project_id}.{dim_dataset}.{rel['dim_table']}"
                dim_text += f"\n- Para obtener información de {rel['dim_table']}:\n"
                dim_text += f"  JOIN `{dim_table_full}` AS {rel['dim_table']} ON `{table_full}`.{rel['fact_column']} = {rel['dim_table']}.{rel['dim_column']}\n"
                dim_text += f"  Usa esta relación cuando la pregunta mencione nombres/descripciones de {rel['dim_table'].replace('Dim', '').lower()}\n"
        
        # Reglas específicas solo si hay dimensiones disponibles - MÁS EXPLÍCITAS
        dimension_rules = """- ⚠️ CRÍTICO: Si la pregunta menciona "nombre", "name", "province name", "product name", "by month", "by year", "by quarter" o cualquier información descriptiva → DEBES hacer JOIN OBLIGATORIAMENTE
- ⚠️ NO uses columnas de texto de la fact table si hay una dimensión disponible (ej: NO uses delivery_province si puedes usar DimProvince.province_name)
- ⚠️ Cuando hagas JOIN, usa EXACTAMENTE las relaciones proporcionadas en la sección RELACIONES
- ⚠️ Si la pregunta pide agrupar por "province name" → HAZ JOIN con DimProvince y usa DimProvince.province_name en el GROUP BY
- ⚠️ Si la pregunta pide agrupar por "product name" → HAZ JOIN con DimProducts y usa DimProducts.product_name en el GROUP BY
- ⚠️ Si la pregunta pide análisis temporal (mes, trimestre, año) → HAZ JOIN con DimTime"""
    else:
        # Sin dimensiones disponibles
        dimension_rules = "- Usa solo las columnas de la tabla principal proporcionada"
    
    # Construir contexto de conversación si hay historial
    conversation_context = ""
    if conversation_history and len(conversation_history) > 0:
        # Limitar a las últimas 5 interacciones para no hacer el prompt muy largo
        recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
        conversation_context = "\n\n📋 CONTEXTO DE CONVERSACIÓN ANTERIOR (para referencias como 'the same', 'previous query', etc.):\n"
        for msg in recent_history:
            if msg.get("role") == "user":
                conversation_context += f"Usuario: {msg.get('content', '')}\n"
            elif msg.get("role") == "assistant":
                sql = msg.get('sql', '')
                if sql:
                    conversation_context += f"Asistente: {msg.get('content', '')} (SQL: {sql[:100]}...)\n"
                else:
                    conversation_context += f"Asistente: {msg.get('content', '')}\n"
        conversation_context += "\n💡 Si la pregunta actual hace referencia a algo anterior (ej: 'the same', 'that query', 'previous results'), usa el contexto de arriba para entender qué se refiere.\n"
    
    return BASE_PROMPT.format(
        question=question,
        schema=schema,
        project_id=project_id,
        dataset=dataset,
        table=table,
        dimensions_info=dim_text,
        dimension_rules=dimension_rules,
        conversation_context=conversation_context
    )

