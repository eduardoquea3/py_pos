from uuid import UUID

from sqlalchemy.orm import Session

from src.modules.company.model import Company
from src.modules.company.schema import CompanyCreate, CompanyUpdate
from src.modules.tenant import service as tenant_service


def create_company(db: Session, company_data: CompanyCreate) -> Company:
    """
    Crea una nueva compañía en la DB central.

    Este proceso automáticamente:
    1. Crea un tenant con el subdomain especificado
    2. Crea la base de datos del tenant
    3. Ejecuta las migraciones en la DB del tenant
    4. Crea la compañía con relación 1:1 al tenant

    Args:
        db: Sesión de la base de datos central
        company_data: Datos de la compañía a crear (incluye subdomain)

    Returns:
        Company: La compañía creada

    Raises:
        ValueError: Si el subdomain ya existe
        RuntimeError: Si hay error creando la DB o ejecutando migraciones
    """
    # Extraer subdomain del company_data
    data_dict = company_data.model_dump()
    subdomain = data_dict.pop("subdomain")

    # Crear el tenant (esto crea la DB y ejecuta migraciones)
    tenant = tenant_service.create_tenant(
        db=db,
        name=data_dict["name"],  # Usar el nombre de la company como nombre del tenant
        subdomain=subdomain,
    )

    # Crear la compañía vinculada al tenant
    company = Company(tenant_id=tenant.id, **data_dict)
    db.add(company)
    db.commit()
    db.refresh(company)

    return company


def get_company(db: Session, company_id: UUID) -> Company | None:
    """Obtiene una compañía por ID"""
    return db.query(Company).filter(Company.id == company_id).first()


def get_companies(db: Session) -> list[Company]:
    """Obtiene todas las compañías"""
    return db.query(Company).all()


def get_companies_by_tenant(db: Session, tenant_id: UUID) -> list[Company]:
    """Obtiene todas las compañías de un tenant"""
    return db.query(Company).filter(Company.tenant_id == tenant_id).all()


def update_company(
    db: Session, company_id: UUID, company_data: CompanyUpdate
) -> Company | None:
    """Actualiza una compañía"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return None

    update_data = company_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)
    return company


def delete_company(db: Session, company_id: UUID) -> bool:
    """Elimina una compañía"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return False

    db.delete(company)
    db.commit()
    return True
