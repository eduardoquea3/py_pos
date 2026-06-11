import asyncio
import os
import logging
import sys
from contextlib import asynccontextmanager
import subprocess

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference  # type: ignore
from sqlalchemy import text

from src.config.api import register_routes
from src.config.db import CentralSessionLocal, central_engine
from src.config.logging import LogLevels, configure_logging
from src.config.settings import settings
from src.modules.company.schema import CompanyCreate
from src.modules.company.service import create_company

configure_logging(LogLevels.info)

logger = logging.getLogger(__name__)


def verify_db_connection():
    """Verifica la conexión a la base de datos central (sincrónico)"""
    with central_engine.connect() as conn:
        conn.execute(text("SELECT 1"))


def run_central_migrations():
    """Aplica migraciones de la DB central antes del bootstrap de desarrollo."""
    subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        check=True,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )


def seed_development_company():
    """Crea una company/tenant/DB de desarrollo si no existe."""
    if settings.ENV != "development":
        return

    db = CentralSessionLocal()
    try:
        existing = db.execute(text("SELECT 1 FROM companies LIMIT 1")).fetchone()
        if existing:
            return

        create_company(
            db,
            CompanyCreate(
                name="Development Company",
                subdomain="dev",
                legal_name="Development Company",
                tax_id=None,
                email=None,
                phone=None,
                address=None,
            ),
        )
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando API...")

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, verify_db_connection)
        logger.info("✓ Database connection successful")
        if settings.ENV == "development":
            await loop.run_in_executor(None, run_central_migrations)
        await loop.run_in_executor(None, seed_development_company)
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        sys.exit(1)

    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)


@app.get("/docs", include_in_schema=False)
async def scalar_html():
    print(settings.DB_URL)
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        scalar_proxy_url="https://proxy.scalar.com",
    )


register_routes(app)
