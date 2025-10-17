"""
Configuración y helpers para sistema multitenant.
Cada tenant tiene su propia base de datos aislada.
"""

import logging
import threading
from typing import Optional

from fastapi import HTTPException, Request, status
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from src.config.db import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Cache de engines por tenant (thread-safe)
tenant_engines: dict[str, dict] = {}
tenant_engines_lock = threading.Lock()


def extract_subdomain_from_host(host: str, main_domain: str = "localhost") -> Optional[str]:
    """
    Extrae el subdominio del header Host.

    Args:
        host: Header Host completo (ej: "acme.ejemplo.com:8000")
        main_domain: Dominio principal (ej: "ejemplo.com" o "localhost")

    Returns:
        Subdominio o None si no se detecta

    Examples:
        >>> extract_subdomain_from_host("acme.ejemplo.com", "ejemplo.com")
        'acme'
        >>> extract_subdomain_from_host("acme.localhost:8000", "localhost")
        'acme'
        >>> extract_subdomain_from_host("ejemplo.com", "ejemplo.com")
        None
    """
    # Remover puerto si existe
    host_no_port = host.split(":")[0]

    # Verificar si termina con el dominio principal
    if host_no_port.endswith(main_domain):
        parts = host_no_port.split(".")

        # Si hay más de 2 partes (o más de 1 para localhost), el primero es el subdominio
        min_parts = 2 if main_domain == "localhost" else 3

        if len(parts) >= min_parts:
            return parts[0]

    return None


async def get_tenant_db_url(central_db: AsyncSession, subdomain: str) -> Optional[str]:
    """
    Obtiene la URL de conexión de un tenant desde la DB central.

    Args:
        central_db: Sesión de la base de datos central
        subdomain: Subdominio del tenant

    Returns:
        URL de conexión del tenant o None si no existe
    """
    result = await central_db.execute(
        text("SELECT db_url, status FROM tenants WHERE subdomain = :subdomain"),
        {"subdomain": subdomain},
    )
    tenant_record = result.first()

    if not tenant_record:
        return None

    # Verificar que el tenant esté activo
    if tenant_record.status != "active":
        logger.warning(f"Intento de acceso a tenant inactivo: {subdomain} (status: {tenant_record.status})")
        return None

    return tenant_record.db_url


def get_or_create_tenant_engine(db_url: str) -> dict:
    """
    Obtiene o crea un engine para un tenant específico (con cache thread-safe).

    Args:
        db_url: URL de conexión del tenant

    Returns:
        Dict con 'engine' y 'sessionmaker'
    """
    with tenant_engines_lock:
        if db_url in tenant_engines:
            return tenant_engines[db_url]

        # Crear nuevo engine async para el tenant
        engine = create_async_engine(
            db_url,
            echo=False,  # Desactivar echo en producción
            pool_size=5,
            max_overflow=10,
        )

        session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        tenant_engines[db_url] = {"engine": engine, "sessionmaker": session_maker}

        logger.info(f"Nuevo engine creado para tenant: {db_url.split('/')[-1]}")

        return tenant_engines[db_url]


async def get_tenant_session(request: Request):
    """
    Dependency para obtener sesión de DB del tenant basado en subdominio.

    Esta función se usa como dependency en rutas que requieren acceso a la DB del tenant.

    Example:
        @app.get("/products")
        async def get_products(tenant_db: AsyncSession = Depends(get_tenant_session)):
            # tenant_db conecta automáticamente a la DB del tenant según el subdominio
            ...

    Raises:
        HTTPException: 400 si no se detecta subdominio, 404 si no existe el tenant
    """
    # Obtener host del request
    host = request.headers.get("host", "")

    # Extraer subdominio
    subdomain = extract_subdomain_from_host(host, main_domain="localhost")

    if not subdomain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se detectó subdominio. Accede mediante: {tenant}.localhost:8000",
        )

    # Obtener sesión de la DB central
    async with AsyncSessionLocal() as central_db:
        # Buscar tenant en DB central
        db_url = await get_tenant_db_url(central_db, subdomain)

        if not db_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tenant '{subdomain}' no encontrado o inactivo",
            )

    # Obtener o crear engine para el tenant
    tenant_entry = get_or_create_tenant_engine(db_url)

    # Crear sesión para el tenant
    async with tenant_entry["sessionmaker"]() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_tenant_info(request: Request) -> Optional[dict]:
    """
    Helper para obtener información del tenant actual sin crear sesión de DB.

    Returns:
        Dict con info del tenant: {'subdomain': str, 'db_url': str, 'name': str} o None
    """
    host = request.headers.get("host", "")
    subdomain = extract_subdomain_from_host(host, main_domain="localhost")

    if not subdomain:
        return None

    async with AsyncSessionLocal() as central_db:
        result = await central_db.execute(
            text("SELECT subdomain, db_url, name FROM tenants WHERE subdomain = :subdomain AND status = 'active'"),
            {"subdomain": subdomain},
        )
        tenant_record = result.first()

        if not tenant_record:
            return None

        return {
            "subdomain": tenant_record.subdomain,
            "db_url": tenant_record.db_url,
            "name": tenant_record.name,
        }