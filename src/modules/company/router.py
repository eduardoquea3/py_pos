from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.config.db import get_central_db
from src.modules.company import service
from src.modules.company.schema import CompanyCreate, CompanyResponse, CompanyUpdate

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/", response_model=CompanyResponse, status_code=201)
def create_company(company_data: CompanyCreate, db: Session = Depends(get_central_db)):
    """
    Crea una nueva compañía en la DB central.

    Este endpoint automáticamente:
    - Crea un tenant con el subdomain especificado
    - Crea una base de datos PostgreSQL para ese tenant
    - Ejecuta las migraciones en la DB del tenant (users, series, etc.)
    - Crea la compañía con relación 1:1 al tenant

    Ejemplo de request body:
    {
        "name": "ACME Corporation",
        "subdomain": "acme",
        "legal_name": "ACME Corp S.A.",
        "tax_id": "20123456789",
        "email": "contacto@acme.com",
        "phone": "+51 999 999 999",
        "address": "Av. Principal 123"
    }
    """
    try:
        return service.create_company(db, company_data)
    except ValueError as e:
        # Error de validación (ej: subdomain duplicado)
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Error en la creación de DB o migraciones
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Otros errores
        raise HTTPException(
            status_code=500, detail=f"Error inesperado creando compañía: {str(e)}"
        )


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: UUID, db: Session = Depends(get_central_db)):
    """Obtiene una compañía por ID"""
    company = service.get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/tenant/{tenant_id}", response_model=list[CompanyResponse])
def get_companies_by_tenant(tenant_id: UUID, db: Session = Depends(get_central_db)):
    """Obtiene todas las compañías de un tenant"""
    return service.get_companies_by_tenant(db, tenant_id)


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: UUID,
    company_data: CompanyUpdate,
    db: Session = Depends(get_central_db),
):
    """Actualiza una compañía"""
    company = service.update_company(db, company_id, company_data)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.delete("/{company_id}", status_code=204)
def delete_company(company_id: UUID, db: Session = Depends(get_central_db)):
    """Elimina una compañía"""
    if not service.delete_company(db, company_id):
        raise HTTPException(status_code=404, detail="Company not found")
