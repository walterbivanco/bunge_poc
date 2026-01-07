"""
Modelos Pydantic para validación de request/response
"""
from pydantic import BaseModel, Field
from typing import List, Any, Optional


class AskRequest(BaseModel):
    """Request para hacer una pregunta en lenguaje natural"""
    question: str = Field(
        ..., 
        min_length=1,
        description="Pregunta en lenguaje natural sobre los datos"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "¿Cuántos contratos hay por estado?"
            }
        }


class AskResponse(BaseModel):
    """Response con el SQL generado y los resultados"""
    question: str = Field(..., description="Pregunta original del usuario")
    sql: str = Field(..., description="Query SQL generada")
    columns: List[str] = Field(..., description="Nombres de las columnas")
    rows: List[List[Any]] = Field(..., description="Filas de resultados")
    total_rows: int = Field(..., description="Total de filas retornadas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "¿Cuántos contratos hay?",
                "sql": "SELECT COUNT(*) as total FROM tabla",
                "columns": ["total"],
                "rows": [[150]],
                "total_rows": 1
            }
        }


class ErrorResponse(BaseModel):
    """Response de error"""
    error: str = Field(..., description="Mensaje de error")
    details: Optional[str] = Field(None, description="Detalles adicionales del error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Error al generar SQL",
                "details": "El modelo no pudo interpretar la pregunta"
            }
        }


class HealthResponse(BaseModel):
    """Response del health check"""
    status: str = Field(..., description="Estado del servicio")
    bigquery: bool = Field(..., description="Estado de conexión a BigQuery")
    vertex_ai: bool = Field(..., description="Estado de Vertex AI")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "bigquery": True,
                "vertex_ai": True
            }
        }

