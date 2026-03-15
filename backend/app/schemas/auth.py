"""Schemas Pydantic para autenticacion."""

from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    """Informacion del usuario autenticado."""

    id: str = Field(..., description="UUID del usuario en Supabase")
    email: str = Field(..., description="Email del usuario")
