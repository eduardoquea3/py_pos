import logging
import sys

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from sqlalchemy import text

from src.config.api import register_routes
from src.config.db import engine
from src.config.logging import LogLevels, configure_logging

configure_logging(LogLevels.info)

logger = logging.getLogger(__name__)

app = FastAPI(docs_url=None, redoc_url=None)


@app.on_event("startup")
async def check_database_connection():
    """Verifica que la base de datos existe y es accesible al iniciar."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✓ Database connection successful")
    except Exception:
        print("\n✗ Database connection failed\n", file=sys.stderr)
        sys.exit(1)


@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        scalar_proxy_url="https://proxy.scalar.com",
    )


register_routes(app)
