from uuid import UUID

from sqlalchemy.orm import Session

from src.modules.tenant.model import Tenant
from src.modules.tenant.util import (
    create_tenant_db,
    normalize_db_name,
    run_tenant_migrations,
)


def create_tenant(db: Session, name: str, subdomain: str) -> Tenant:
    """
    Crea un nuevo tenant con su base de datos.

    Este proceso incluye:
    1. Crear la base de datos del tenant (con nombre normalizado desde el name)
    2. Ejecutar las migraciones de tenant (users, series, etc.)
    3. Registrar el tenant en la DB central

    Ejemplo:
    - name="Panadería Juan", subdomain="panaderia" -> DB: "tn_panaderia_juan"
    - name="Empresa S.A.C.", subdomain="empresa1" -> DB: "tn_empresa_s_a_c_"
    """
    # Verificar que el subdomain no exista
    existing = db.query(Tenant).filter(Tenant.subdomain == subdomain).first()
    if existing:
        raise ValueError(f"El subdomain '{subdomain}' ya existe")

    # Crear la base de datos con nombre normalizado desde el name de la company
    db_name = normalize_db_name(name)
    db_url = create_tenant_db(db_name)

    # Crear el registro del tenant
    tenant = Tenant(
        name=name,
        subdomain=subdomain,
        db_name=db_name,
        db_url=db_url,
        status="active",
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    # Ejecutar migraciones en la DB del tenant
    try:
        run_tenant_migrations(db_url)
    except Exception as e:
        # Si falla, hacer rollback del tenant
        db.delete(tenant)
        db.commit()
        raise RuntimeError(f"Error ejecutando migraciones del tenant: {e}")

    return tenant


def get_tenant_by_subdomain(db: Session, subdomain: str) -> Tenant | None:
    """Obtiene un tenant por su subdomain"""
    return db.query(Tenant).filter(Tenant.subdomain == subdomain).first()


def get_tenant_by_id(db: Session, tenant_id: UUID) -> Tenant | None:
    """Obtiene un tenant por su ID"""
    return db.query(Tenant).filter(Tenant.id == tenant_id).first()


def get_all_tenants(db: Session) -> list[Tenant]:
    """Obtiene todos los tenants"""
    return db.query(Tenant).all()
