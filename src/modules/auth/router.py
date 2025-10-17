from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.db import get_db
from src.modules.auth.schema import (
    PasswordChange,
    TokenRefresh,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from src.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Dependency para obtener el usuario actual desde el token JWT"""
    token = credentials.credentials

    # Decodificar token
    payload = AuthService.decode_token(token, token_type="access")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtener usuario
    user = await AuthService.get_user_by_id(db, UUID(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    return user


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
)
async def register(
    user_data: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Registra un nuevo usuario en el sistema.

    - **email**: Email único del usuario
    - **password**: Contraseña (mínimo 8 caracteres)
    - **full_name**: Nombre completo
    - **tenant_id**: ID del tenant (opcional, NULL para usuarios globales)
    """
    try:
        user = await AuthService.register_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
)
async def login(
    login_data: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Autentica un usuario y retorna tokens JWT.

    - **email**: Email del usuario
    - **password**: Contraseña

    Retorna:
    - **access_token**: Token de acceso (válido por 1 día)
    - **refresh_token**: Token de refresco (válido por 7 días)
    - **user**: Información del usuario
    """
    user = await AuthService.authenticate_user(db, login_data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear tokens
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role}

    access_token = AuthService.create_access_token(token_data)
    refresh_token = AuthService.create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar token de acceso",
)
async def refresh_token(
    token_data: TokenRefresh,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Renueva el access token usando el refresh token.

    - **refresh_token**: Token de refresco válido
    """
    # Decodificar refresh token
    payload = AuthService.decode_token(token_data.refresh_token, token_type="refresh")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    # Obtener usuario
    user = await AuthService.get_user_by_id(db, UUID(user_id))

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )

    # Crear nuevos tokens
    new_token_data = {"sub": str(user.id), "email": user.email, "role": user.role}

    access_token = AuthService.create_access_token(new_token_data)
    refresh_token = AuthService.create_refresh_token(new_token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener usuario actual",
)
async def get_me(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
):
    """
    Obtiene la información del usuario actualmente autenticado.

    Requiere: Token JWT válido en header Authorization: Bearer <token>
    """
    return current_user


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cambiar contraseña",
)
async def change_password(
    password_data: PasswordChange,
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Cambia la contraseña del usuario actual.

    - **current_password**: Contraseña actual
    - **new_password**: Nueva contraseña (mínimo 8 caracteres)

    Requiere: Token JWT válido
    """
    try:
        success = await AuthService.change_password(
            db, current_user.id, password_data
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        return None
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))