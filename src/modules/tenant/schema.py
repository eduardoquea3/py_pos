from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TenantCreate(BaseModel):
    """Schema para crear un nuevo tenant"""

    name: str = Field(..., min_length=1, max_length=255, description="Nombre de la empresa")
    subdomain: str = Field(
        ...,
        min_length=3,
        max_length=100,
        pattern="^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="Subdominio (solo letras minúsculas, números y guiones)",
    )

    @field_validator("subdomain")
    @classmethod
    def validate_subdomain(cls, v: str) -> str:
        """Validar que el subdominio no contenga palabras reservadas"""
        reserved = {"www", "api", "admin", "app", "mail", "ftp", "localhost"}
        if v.lower() in reserved:
            raise ValueError(f"El subdominio '{v}' está reservado")
        return v.lower()


class TenantResponse(BaseModel):
    """Schema para respuesta de tenant"""

    id: UUID
    name: str
    subdomain: str
    db_name: str
    created_at: datetime
    status: str
    admin_user_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class TenantUpdate(BaseModel):
    """Schema para actualizar un tenant"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, pattern="^(active|paused|suspended)$")


class TenantListResponse(BaseModel):
    """Schema para lista de tenants"""

    tenants: list[TenantResponse]
    total: int