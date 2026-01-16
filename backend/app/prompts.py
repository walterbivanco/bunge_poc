"""
Prompts para la generación de SQL desde lenguaje natural
"""
import os

# ⚡ Prompt ultra-optimizado para respuesta rápida
BASE_PROMPT = """Convierte esta pregunta a SQL de BigQuery. Responde SOLO con el SQL, sin explicaciones.

TABLA PRINCIPAL (FACT TABLE): `{project_id}.{dataset}.{table}`

COLUMNAS DE LA TABLA PRINCIPAL:
{schema}
{dimensions_info}
REGLAS CRÍTICAS:
- Solo SELECT (nunca INSERT/UPDATE/DELETE)
{dimension_rules}
- Usa solo columnas de los schemas proporcionados
- Agrega LIMIT 100
- Sin markdown ni explicaciones

PREGUNTA: {question}

SQL:"""


def get_prompt(
    question: str, 
    schema: str, 
    project_id: str, 
    dataset: str, 
    table: str,
    dimensions_info: dict = None
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
    
    return BASE_PROMPT.format(
        question=question,
        schema=schema,
        project_id=project_id,
        dataset=dataset,
        table=table,
        dimensions_info=dim_text,
        dimension_rules=dimension_rules
    )

