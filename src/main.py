import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference  # type: ignore
from sqlalchemy import text

from src.config.api import register_routes
from src.config.db import central_engine
from src.config.logging import LogLevels, configure_logging
from src.config.settings import settings

configure_logging(LogLevels.info)

logger = logging.getLogger(__name__)


def verify_db_connection():
    """Verifica la conexión a la base de datos central (sincrónico)"""
    with central_engine.connect() as conn:
        conn.execute(text("SELECT 1"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando API...")

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, verify_db_connection)
        logger.info("✓ Database connection successful")
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
