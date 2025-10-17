from sqlalchemy import Column, Integer, String

from src.config.db import Base


class Serie(Base):
    __tablename__ = "serie"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
