from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.config.db import CentralBase


class Tenant(CentralBase):
    """
    Modelo de Tenant (Empresa) para la base de datos CENTRAL.
    Cada tenant tiene su propia base de datos aislada.

    Este modelo solo existe en la DB central, NO en las DB de cada tenant.
    """

    __tablename__ = "tenants"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, index=True)
    name: Mapped[str] = mapped_column(
        String(255), comment="Nombre de la empresa", nullable=False
    )
    subdomain: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        comment="Subdominio asignado (ej: 'acme')",
        nullable=False,
    )
    db_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        comment="Nombre de la base de datos",
        nullable=False,
    )
    db_url: Mapped[str] = mapped_column(
        Text,
        comment="URL de conexión a la base de datos del tenant",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    status: Mapped[str] = mapped_column(
        String(20),
        comment="Estado: active, paused, suspended",
        nullable=False,
        default="active",
    )
    admin_user_id: Mapped[UUID | None] = mapped_column(
        comment="ID del usuario administrador", nullable=True
    )

    def __repr__(self):
        return f"<Tenant(id={self.id}, name={self.name}, subdomain={self.subdomain})>"
