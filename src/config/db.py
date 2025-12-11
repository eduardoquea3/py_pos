from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config.settings import settings

# ============================================
# BASE DE DATOS CENTRAL (Central Registry)
# ============================================
# Esta base de datos contiene solo:
# - tenants: registro de todos los tenants
# - companies: registro de compañías (futuro)
central_engine = create_engine(settings.DB_URL, echo=False)
CentralSessionLocal = sessionmaker(
    bind=central_engine, autoflush=False, autocommit=False
)
CentralBase = declarative_base()


def get_central_db():
    """Sesión para la base de datos central (solo tenants y companies)"""
    db = CentralSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================
# BASE DE DATOS TENANT (Por Tenant)
# ============================================
# Esta base de datos contiene todos los modelos de negocio:
# - users, series, products, sales, inventory, etc.
# Se conecta dinámicamente según el tenant activo
TenantBase = declarative_base()

# Este engine se configurará dinámicamente por tenant
# mediante middleware de FastAPI
tenant_engine = None
TenantSessionLocal = None


def get_tenant_db():
    """Sesión para la base de datos del tenant activo"""
    if TenantSessionLocal is None:
        raise RuntimeError(
            "Tenant database not configured. Use set_tenant_engine() first."
        )
    db = TenantSessionLocal()
    try:
        yield db
    finally:
        db.close()


def set_tenant_engine(db_url: str):
    """Configura el engine para el tenant activo"""
    global tenant_engine, TenantSessionLocal
    tenant_engine = create_engine(db_url, echo=False)
    TenantSessionLocal = sessionmaker(
        bind=tenant_engine, autoflush=False, autocommit=False
    )


# Alias para compatibilidad (deprecated, usar CentralBase o TenantBase explícitamente)
Base = CentralBase


def get_db():
    """Deprecated: Usar get_central_db() o get_tenant_db() explícitamente"""
    return get_central_db()
