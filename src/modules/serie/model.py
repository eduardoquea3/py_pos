from sqlalchemy import Column, Integer, String

from src.config.db import TenantBase


class Serie(TenantBase):
    """
    Modelo de Serie para la base de datos del TENANT.
    Este modelo existe SOLO en las DB de cada tenant, NO en la DB central.
    """

    __tablename__ = "serie"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
