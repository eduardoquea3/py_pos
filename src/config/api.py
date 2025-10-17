from fastapi import FastAPI

from src.modules.auth.router import router as auth_router
from src.modules.tenant.router import router as tenant_router
from src.modules.user.router import router as user_router


def register_routes(app: FastAPI):
    """Registra todos los routers de la aplicación"""
    # Autenticación
    app.include_router(auth_router)

    # Gestión de tenants (empresas)
    app.include_router(tenant_router)

    # Usuarios
    app.include_router(user_router)
