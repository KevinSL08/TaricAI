"""
API v1 - Endpoints de clasificación TARIC.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import get_current_user, require_auth
from app.schemas.auth import UserInfo
from app.schemas.classification import (
    ClassifyRequest,
    ClassifyResponse,
    ErrorResponse,
)
from app.services.classifier import classify_product

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["classification"])


@router.post(
    "/classify",
    response_model=ClassifyResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Descripción inválida"},
        500: {"model": ErrorResponse, "description": "Error interno"},
        503: {"model": ErrorResponse, "description": "Servicio de IA no disponible"},
    },
    summary="Clasificar producto TARIC",
    description="Clasifica un producto según la nomenclatura TARIC usando IA (Claude API).",
)
async def classify(
    request: ClassifyRequest,
    user: Optional[dict] = Depends(get_current_user),
) -> ClassifyResponse:
    """
    Clasifica un producto y devuelve sugerencias de códigos TARIC.

    - Envía la descripción a Claude API con un prompt especializado
    - Devuelve 1-5 sugerencias ordenadas por confianza
    - Incluye razonamiento para cada sugerencia
    """
    try:
        if user:
            logger.info(f"Clasificacion por usuario {user['email']}")
        result = await classify_product(
            description=request.description,
            origin_country=request.origin_country,
            additional_context=request.additional_context,
        )
        return result
    except Exception as e:
        logger.error(f"Error en clasificación: {e}", exc_info=True)

        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            raise HTTPException(
                status_code=503,
                detail="Servicio de IA no disponible. Verifica la API key de Anthropic.",
            )

        raise HTTPException(
            status_code=500,
            detail=f"Error interno en la clasificación: {error_msg}",
        )


@router.get(
    "/search",
    summary="Búsqueda semántica de códigos TARIC",
    description="Busca códigos TARIC similares a la descripción usando embeddings.",
)
async def semantic_search_endpoint(
    q: str,
    top_k: int = 5,
    user: Optional[dict] = Depends(get_current_user),
):
    """Búsqueda semántica en Pinecone."""
    from app.core.config import settings

    if not settings.pinecone_api_key:
        raise HTTPException(status_code=503, detail="Pinecone no configurado")

    try:
        from app.services.embeddings import semantic_search

        results = await semantic_search(q, top_k=top_k)
        return {"query": q, "results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/auth/me",
    response_model=UserInfo,
    summary="Información del usuario autenticado",
    responses={401: {"model": ErrorResponse, "description": "No autenticado"}},
)
async def get_me(user: dict = Depends(require_auth)) -> UserInfo:
    """Retorna la información del usuario autenticado."""
    return UserInfo(id=user["id"], email=user["email"])


@router.get(
    "/health",
    summary="Estado del servicio de clasificación",
)
async def classification_health():
    """Verifica que el servicio de clasificación esté operativo."""
    from app.core.config import settings

    return {
        "status": "ok",
        "anthropic_configured": bool(settings.anthropic_api_key),
        "openai_configured": bool(settings.openai_api_key),
        "pinecone_configured": bool(settings.pinecone_api_key),
    }
