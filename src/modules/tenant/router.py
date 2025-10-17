from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.db import get_db
from src.modules.tenant.schema import (
    TenantCreate,
    TenantListResponse,
    TenantResponse,
    TenantUpdate,
)
from src.modules.tenant.service import TenantService

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.post(
    "/",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo tenant (empresa)",
)
async def create_tenant(
    tenant_data: TenantCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Crea un nuevo tenant (empresa) con su propia base de datos aislada.

    - **name**: Nombre de la empresa
    - **subdomain**: Subdominio único (ej: 'acme' para acme.ejemplo.com)

    El sistema creará automáticamente:
    - Una nueva base de datos para el tenant
    - La estructura de tablas necesaria (mediante migraciones)
    - El registro del tenant en la base central
    """
    try:
        tenant = await TenantService.create_tenant(db, tenant_data)
        return tenant
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear tenant: {str(e)}",
        )


@router.get(
    "/",
    response_model=TenantListResponse,
    summary="Listar todos los tenants",
)
async def list_tenants(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
):
    """
    Obtiene la lista de todos los tenants registrados.

    - **skip**: Número de registros a omitir (para paginación)
    - **limit**: Número máximo de registros a retornar
    """
    tenants, total = await TenantService.list_tenants(db, skip, limit)
    return TenantListResponse(tenants=tenants, total=total)


@router.get(
    "/subdomain/{subdomain}",
    response_model=TenantResponse,
    summary="Obtener tenant por subdominio",
)
async def get_tenant_by_subdomain(
    subdomain: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Obtiene un tenant específico por su subdominio.

    - **subdomain**: El subdominio del tenant (ej: 'acme')
    """
    tenant = await TenantService.get_tenant_by_subdomain(db, subdomain)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant con subdominio '{subdomain}' no encontrado",
        )

    return tenant


@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
    summary="Obtener tenant por ID",
)
async def get_tenant_by_id(
    tenant_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Obtiene un tenant específico por su ID.

    - **tenant_id**: UUID del tenant
    """
    tenant = await TenantService.get_tenant_by_id(db, tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant con ID '{tenant_id}' no encontrado",
        )

    return tenant


@router.patch(
    "/{tenant_id}",
    response_model=TenantResponse,
    summary="Actualizar tenant",
)
async def update_tenant(
    tenant_id: UUID,
    tenant_data: TenantUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Actualiza la información de un tenant existente.

    - **tenant_id**: UUID del tenant a actualizar
    - **name**: Nuevo nombre (opcional)
    - **status**: Nuevo estado: active, paused, suspended (opcional)
    """
    tenant = await TenantService.update_tenant(db, tenant_id, tenant_data)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant con ID '{tenant_id}' no encontrado",
        )

    return tenant


@router.delete(
    "/{tenant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Suspender tenant",
)
async def delete_tenant(
    tenant_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Suspende un tenant (no lo elimina completamente por seguridad).

    - **tenant_id**: UUID del tenant a suspender
    """
    success = await TenantService.delete_tenant(db, tenant_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant con ID '{tenant_id}' no encontrado",
        )

    return None