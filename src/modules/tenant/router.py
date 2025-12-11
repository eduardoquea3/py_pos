from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from src.config.db import get_db
from src.modules.tenant.service import create_tenant
from typing import Dict, Any

router = APIRouter(prefix="/tenants", tags=["tenant"])


@router.post("/tenants", status_code=status.HTTP_201_CREATED)
async def crear_tenant(nombre: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Crea un nuevo tenant"""
    try:
        empresa = create_tenant(db, nombre)
        return {
            "status": "success",
            "message": "Tenant creado exitosamente",
            "data": empresa,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}"
        )
