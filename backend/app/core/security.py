"""
Autenticacion y verificacion de tokens JWT de Supabase.
"""

import logging
from typing import Optional

from fastapi import Header, HTTPException
from supabase import create_client

from app.core.config import settings

logger = logging.getLogger(__name__)

_supabase_client = None


def _get_supabase():
    """Obtiene el cliente Supabase (singleton)."""
    global _supabase_client
    if _supabase_client is None:
        if not settings.supabase_url or not settings.supabase_key:
            return None
        _supabase_client = create_client(settings.supabase_url, settings.supabase_key)
    return _supabase_client


async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> Optional[dict]:
    """
    Dependency de FastAPI que verifica el token JWT de Supabase.

    Si no hay token o Supabase no esta configurado, retorna None (acceso anonimo).
    Si hay token invalido, lanza 401.
    """
    if not authorization:
        return None

    supabase = _get_supabase()
    if not supabase:
        return None

    # Extraer token del header "Bearer <token>"
    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization

    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        if not user:
            raise HTTPException(status_code=401, detail="Token invalido")
        return {
            "id": str(user.id),
            "email": user.email,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Error verificando token: {e}")
        raise HTTPException(status_code=401, detail="Token invalido o expirado")


async def require_auth(
    authorization: Optional[str] = Header(None),
) -> dict:
    """
    Dependency que REQUIERE autenticacion (lanza 401 si no hay token).
    """
    user = await get_current_user(authorization)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Autenticacion requerida. Incluye header Authorization: Bearer <token>",
        )
    return user
