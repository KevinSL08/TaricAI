"""Schemas Pydantic para el endpoint de clasificación TARIC."""

from pydantic import BaseModel, Field


class ClassifyRequest(BaseModel):
    """Request para clasificar un producto."""

    description: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Descripción del producto a clasificar",
        examples=["Café tostado en grano, arábica, de Colombia, 1kg"],
    )
    origin_country: str | None = Field(
        None,
        min_length=2,
        max_length=2,
        description="Código ISO 3166-1 alpha-2 del país de origen",
        examples=["CO", "CN", "US"],
    )
    additional_context: str | None = Field(
        None,
        max_length=1000,
        description="Contexto adicional (material, uso, composición...)",
    )


class TaricSuggestion(BaseModel):
    """Una sugerencia de código TARIC."""

    code: str = Field(..., description="Código TARIC (hasta 10 dígitos)")
    description: str = Field(..., description="Descripción oficial del código")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confianza de la clasificación (0-1)"
    )
    reasoning: str = Field(..., description="Razonamiento de por qué este código aplica")
    duty_rate: str | None = Field(None, description="Tasa arancelaria si está disponible")
    chapter: str | None = Field(None, description="Capítulo TARIC (2 dígitos)")
    section: str | None = Field(None, description="Sección TARIC (numeral romano)")


class ClassifyResponse(BaseModel):
    """Response de la clasificación TARIC."""

    product_description: str = Field(..., description="Descripción del producto original")
    suggestions: list[TaricSuggestion] = Field(
        ..., description="Sugerencias de clasificación ordenadas por confianza"
    )
    top_code: str = Field(..., description="Código TARIC más probable")
    top_confidence: float = Field(..., description="Confianza del código más probable")
    notes: str | None = Field(None, description="Notas adicionales o advertencias")
    source: str = Field(
        default="claude-ai", description="Fuente de la clasificación"
    )


class ErrorResponse(BaseModel):
    """Response de error."""

    error: str
    detail: str | None = None
