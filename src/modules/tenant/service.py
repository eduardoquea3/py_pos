import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.modules.tenant.model import Tenant
from src.modules.tenant.schema import TenantCreate, TenantUpdate

logger = logging.getLogger(__name__)


class TenantService:
    """Servicio para gestión de tenants (empresas)"""

    @staticmethod
    async def create_tenant(
        db: AsyncSession, tenant_data: TenantCreate, admin_user_id: Optional[UUID] = None
    ) -> Tenant:
        """
        Crea un nuevo tenant:
        1. Verifica que el subdominio no exista
        2. Crea la nueva base de datos
        3. Ejecuta migraciones (pendiente implementar)
        4. Registra el tenant en la DB central
        """
        # Verificar si el subdominio ya existe
        result = await db.execute(
            select(Tenant).where(Tenant.subdomain == tenant_data.subdomain)
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise ValueError(f"El subdominio '{tenant_data.subdomain}' ya existe")

        # Generar nombre de base de datos
        db_name = f"tenant_{tenant_data.subdomain}"

        # Crear la base de datos del tenant
        try:
            # Nota: necesitamos una conexión con privilegios de creación de DB
            # En producción esto debería hacerse con un usuario con permisos adecuados
            await db.execute(text(f"CREATE DATABASE {db_name}"))
            await db.commit()
            logger.info(f"Base de datos '{db_name}' creada exitosamente")
        except Exception as e:
            logger.error(f"Error al crear base de datos '{db_name}': {e}")
            raise ValueError(f"No se pudo crear la base de datos: {e}")

        # Construir URL de conexión para el tenant
        db_url = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{db_name}"

        # Crear registro del tenant
        new_tenant = Tenant(
            name=tenant_data.name,
            subdomain=tenant_data.subdomain,
            db_name=db_name,
            db_url=db_url,
            admin_user_id=admin_user_id,
            status="active",
        )

        db.add(new_tenant)
        await db.commit()
        await db.refresh(new_tenant)

        # TODO: Ejecutar migraciones Alembic en la nueva base de datos del tenant
        # await self._run_tenant_migrations(db_url)

        logger.info(
            f"Tenant '{tenant_data.name}' creado exitosamente con subdominio '{tenant_data.subdomain}'"
        )

        return new_tenant

    @staticmethod
    async def get_tenant_by_subdomain(
        db: AsyncSession, subdomain: str
    ) -> Optional[Tenant]:
        """Obtiene un tenant por su subdominio"""
        result = await db.execute(select(Tenant).where(Tenant.subdomain == subdomain))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_tenant_by_id(db: AsyncSession, tenant_id: UUID) -> Optional[Tenant]:
        """Obtiene un tenant por su ID"""
        result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_tenants(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> tuple[list[Tenant], int]:
        """Lista todos los tenants con paginación"""
        # Obtener total
        count_result = await db.execute(select(Tenant))
        total = len(count_result.all())

        # Obtener tenants con paginación
        result = await db.execute(select(Tenant).offset(skip).limit(limit))
        tenants = result.scalars().all()

        return list(tenants), total

    @staticmethod
    async def update_tenant(
        db: AsyncSession, tenant_id: UUID, tenant_data: TenantUpdate
    ) -> Optional[Tenant]:
        """Actualiza un tenant existente"""
        tenant = await TenantService.get_tenant_by_id(db, tenant_id)

        if not tenant:
            return None

        # Actualizar solo los campos proporcionados
        update_data = tenant_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tenant, field, value)

        await db.commit()
        await db.refresh(tenant)

        logger.info(f"Tenant {tenant_id} actualizado exitosamente")

        return tenant

    @staticmethod
    async def delete_tenant(db: AsyncSession, tenant_id: UUID) -> bool:
        """
        Elimina un tenant (marca como suspendido en lugar de eliminar)
        Para eliminar completamente se requeriría:
        1. Eliminar la base de datos del tenant
        2. Eliminar el registro de la tabla tenants
        """
        tenant = await TenantService.get_tenant_by_id(db, tenant_id)

        if not tenant:
            return False

        # Por seguridad, solo marcamos como suspendido
        tenant.status = "suspended"
        await db.commit()

        logger.warning(f"Tenant {tenant_id} marcado como suspendido")

        return True