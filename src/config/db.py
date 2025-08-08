from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config.settings import settings

# Configuración de base de datos
engine = create_async_engine(
    settings.DB_URL,
)

SessionLocal = sessionmaker(
    autocommit=False, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    """
    Dependency para obtener sesión de base de datos en FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations():
    """
    Ejecuta las migraciones de Alembic automáticamente.
    """
    try:
        from alembic.config import Config
        from alembic import command

        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Migraciones ejecutadas exitosamente.")
    except Exception as error:
        print("Error al ejecutar migraciones:", error)
