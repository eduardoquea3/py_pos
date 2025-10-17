from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Schema para registro de nuevo usuario"""

    email: EmailStr
    password: str = Field(..., min_length=8, description="Contraseña (mínimo 8 caracteres)")
    full_name: str = Field(..., min_length=1, max_length=255)
    tenant_id: Optional[UUID] = None


class UserLogin(BaseModel):
    """Schema para login de usuario"""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema para respuesta de usuario (sin password)"""

    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    tenant_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema para respuesta de autenticación con tokens"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenRefresh(BaseModel):
    """Schema para renovar token"""

    refresh_token: str


class PasswordChange(BaseModel):
    """Schema para cambio de contraseña"""

    current_password: str
    new_password: str = Field(..., min_length=8)