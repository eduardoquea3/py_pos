from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.config.db import CentralBase


class Company(CentralBase):
    """
    Modelo de Company (Compañía/Organización) para la base de datos CENTRAL.
    Registro de todas las compañías en el sistema.

    Relación 1:1 con Tenant: Cada company crea automáticamente un tenant con su propia DB.

    Este modelo solo existe en la DB central, NO en las DB de cada tenant.
    """

    __tablename__ = "companies"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, index=True)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="Relación 1:1 con Tenant - Cada company tiene un único tenant",
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Nombre de la compañía"
    )
    legal_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Nombre legal/razón social"
    )
    tax_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        unique=True,
        index=True,
        comment="RUC/NIT/Tax ID",
    )
    email: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Email de contacto"
    )
    phone: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="Teléfono de contacto"
    )
    address: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Dirección física"
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)
    )
    is_active: Mapped[bool] = mapped_column(
        default=True, nullable=False, comment="Estado activo/inactivo"
    )

    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name}, tenant_id={self.tenant_id})>"
