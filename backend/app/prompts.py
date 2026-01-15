"""
Prompts para la generación de SQL desde lenguaje natural
"""

# ⚡ Prompt ultra-optimizado para respuesta rápida
BASE_PROMPT = """Convierte esta pregunta a SQL de BigQuery. Responde SOLO con el SQL, sin explicaciones.

TABLA PRINCIPAL (FACT TABLE): `{project_id}.{dataset}.{table}`

COLUMNAS DE LA TABLA PRINCIPAL:
{schema}
{dimensions_info}
REGLAS:
- Solo SELECT (nunca INSERT/UPDATE/DELETE)
- Puedes hacer JOINs con las tablas de dimensiones cuando sea necesario
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
    # Construir información de dimensiones si está disponible
    dim_text = ""
    if dimensions_info and dimensions_info.get("dimensions"):
        dim_text = "\n\nTABLAS DE DIMENSIONES (puedes hacer JOINs cuando sea necesario):\n"
        
        for dim_name, dim_data in dimensions_info["dimensions"].items():
            dim_text += f"\n{dim_name} (`{dim_data['table_id']}`):\n"
            dim_text += f"  Columnas: {dim_data['schema']}\n"
        
        dim_text += "\nRELACIONES:\n"
        for rel in dimensions_info.get("relationships", []):
            dim_text += f"- {table}.{rel['fact_column']} → {rel['dim_table']}.{rel['dim_column']}\n"
    
    return BASE_PROMPT.format(
        question=question,
        schema=schema,
        project_id=project_id,
        dataset=dataset,
        table=table,
        dimensions_info=dim_text
    )

