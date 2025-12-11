from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from src.config.db import TenantBase


class User(TenantBase):
    """
    Modelo de Usuario para la base de datos del TENANT.
    Cada tenant tiene su propia tabla de usuarios en su propia base de datos.

    Este modelo existe SOLO en las DB de cada tenant, NO en la DB central.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False, comment="Contraseña hasheada")
    full_name = Column(String(255), nullable=False)
    role = Column(
        String(50),
        default="user",
        nullable=False,
        comment="Roles: admin, user, manager",
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
