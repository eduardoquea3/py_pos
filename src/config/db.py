from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from src.config.settings import settings

# Configuración de base de datos async
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Opcional: muestra las queries SQL en consola
    future=True,
)

# Para async usa async_sessionmaker en lugar de sessionmaker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db():
    """
    Dependency para obtener sesión de base de datos en FastAPI.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
