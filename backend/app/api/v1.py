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
from app.schemas.duties import (
    DutyCalculationRequest,
    DutyCalculationResponse,
)
from app.services.classifier import classify_product
from app.services.tariff_calculator import calculate_import_duties

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["classification", "duties"])


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


@router.post(
    "/calculate-duties",
    response_model=DutyCalculationResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Datos invalidos"},
        404: {"model": ErrorResponse, "description": "Codigo no encontrado"},
        500: {"model": ErrorResponse, "description": "Error interno"},
        503: {"model": ErrorResponse, "description": "API externa no disponible"},
    },
    summary="Calcular aranceles de importacion",
    description="Calcula aranceles, IVA y coste total de importacion para un codigo TARIC usando datos oficiales.",
)
async def calculate_duties(
    request: DutyCalculationRequest,
    user: Optional[dict] = Depends(get_current_user),
) -> DutyCalculationResponse:
    """
    Calcula los aranceles de importacion para un codigo TARIC.

    - Obtiene tipos arancelarios reales de UK Trade Tariff API
    - Calcula arancel base segun pais de origen
    - Aplica IVA espanol (21%, 10% o 4%)
    - Retorna desglose completo del coste de importacion
    """
    if user:
        logger.info(f"Calculo aranceles por usuario {user['email']}")

    if request.iva_type not in ("general", "reducido", "superreducido"):
        raise HTTPException(
            status_code=400,
            detail="iva_type debe ser: general, reducido o superreducido",
        )

    try:
        result = await calculate_import_duties(
            commodity_code=request.commodity_code,
            origin_country=request.origin_country,
            customs_value_eur=request.customs_value_eur,
            weight_kg=request.weight_kg,
            iva_type=request.iva_type,
        )
        return DutyCalculationResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error en calculo de aranceles: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en el calculo: {str(e)}",
        )


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
