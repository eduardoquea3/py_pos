from fastapi import FastAPI

from src.modules.company.router import router as company_router
from src.modules.tenant.router import router as tenant_router


def register_routes(app: FastAPI):
    """Registra todos los routers de la aplicación"""
    # Autenticación
    # app.include_router(auth_router)

    # Gestión de companies (empresas) - DB Central
    # Al crear una company, automáticamente se crea un tenant con su DB
    app.include_router(company_router)

    # Gestión de tenants - DB Central
    app.include_router(tenant_router)

    # Usuarios - DB Tenant
    # app.include_router(user_router)
