from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class CompanyBase(BaseModel):
    """Schema base para Company"""

    name: str
    legal_name: str | None = None
    tax_id: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None


class CompanyCreate(CompanyBase):
    """
    Schema para crear una Company.

    Al crear una company, automáticamente se crea:
    - Un tenant con el subdomain especificado
    - Una base de datos para ese tenant
    - La relación 1:1 entre company y tenant
    """

    subdomain: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern="^[a-z0-9-]+$",
        description="Subdominio único para el tenant (ej: 'acme', 'empresa1')",
    )


class CompanyUpdate(BaseModel):
    """Schema para actualizar una Company"""

    name: str | None = None
    legal_name: str | None = None
    tax_id: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    is_active: bool | None = None


class CompanyResponse(CompanyBase):
    """Schema de respuesta para Company"""

    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
