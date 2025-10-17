from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.config.db import Base


class Tenant(Base):
    """
    Modelo de Tenant (Empresa) para la base de datos central.
    Cada tenant tiene su propia base de datos aislada.
    """

    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    name = Column(String(255), nullable=False, comment="Nombre de la empresa")
    subdomain = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Subdominio asignado (ej: 'acme')",
    )
    db_name = Column(
        String(100), unique=True, nullable=False, comment="Nombre de la base de datos"
    )
    db_url = Column(
        Text, nullable=False, comment="URL de conexión a la base de datos del tenant"
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(
        String(20),
        default="active",
        nullable=False,
        comment="Estado: active, paused, suspended",
    )
    admin_user_id = Column(
        UUID(as_uuid=True), nullable=True, comment="ID del usuario administrador"
    )

    def __repr__(self):
        return f"<Tenant(id={self.id}, name={self.name}, subdomain={self.subdomain})>"