"""
Prompts para la generación de SQL desde lenguaje natural
"""

# ⚡ Prompt ultra-optimizado para respuesta rápida
BASE_PROMPT = """Convierte esta pregunta a SQL de BigQuery. Responde SOLO con el SQL, sin explicaciones.

TABLA: `{project_id}.{dataset}.{table}`

COLUMNAS:
{schema}

REGLAS:
- Solo SELECT (nunca INSERT/UPDATE/DELETE)
- Usa solo columnas del schema
- Agrega LIMIT 100
- Sin markdown ni explicaciones

PREGUNTA: {question}

SQL:"""


def get_prompt(question: str, schema: str, project_id: str, dataset: str, table: str) -> str:
    """
    Construye el prompt completo para enviar a Gemini
    
    Args:
        question: Pregunta en lenguaje natural del usuario
        schema: Schema de la tabla (columnas con tipos)
        project_id: ID del proyecto GCP
        dataset: Dataset de BigQuery
        table: Nombre de la tabla
        
    Returns:
        Prompt formateado listo para enviar al LLM
    """
    return BASE_PROMPT.format(
        question=question,
        schema=schema,
        project_id=project_id,
        dataset=dataset,
        table=table
    )

