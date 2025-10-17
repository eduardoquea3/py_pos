import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.modules.auth.schema import PasswordChange, UserLogin, UserRegister
from src.modules.user.model import User

logger = logging.getLogger(__name__)

# Configuración para hasheo de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Servicio para autenticación y gestión de usuarios"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashea una contraseña usando bcrypt"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crea un JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            # Default: 1 día desde settings
            expire = datetime.utcnow() + timedelta(days=1)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")

        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Crea un JWT refresh token (7 días por defecto)"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)

        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_REFRESH, algorithm="HS256"
        )

        return encoded_jwt

    @staticmethod
    def decode_token(token: str, token_type: str = "access") -> Optional[dict]:
        """Decodifica y valida un JWT token"""
        try:
            secret = (
                settings.JWT_SECRET
                if token_type == "access"
                else settings.JWT_SECRET_REFRESH
            )
            payload = jwt.decode(token, secret, algorithms=["HS256"])

            # Verificar tipo de token
            if payload.get("type") != token_type:
                return None

            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expirado")
            return None
        except jwt.JWTError as e:
            logger.error(f"Error al decodificar token: {e}")
            return None

    @staticmethod
    async def register_user(
        db: AsyncSession, user_data: UserRegister
    ) -> User:
        """Registra un nuevo usuario"""
        # Verificar si el email ya existe
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ValueError(f"El email '{user_data.email}' ya está registrado")

        # Crear nuevo usuario
        hashed_password = AuthService.hash_password(user_data.password)

        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            full_name=user_data.full_name,
            tenant_id=user_data.tenant_id,
            role="user",  # Por defecto es user
            is_active=True,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info(f"Usuario '{user_data.email}' registrado exitosamente")

        return new_user

    @staticmethod
    async def authenticate_user(
        db: AsyncSession, login_data: UserLogin
    ) -> Optional[User]:
        """Autentica un usuario con email y contraseña"""
        # Buscar usuario por email
        result = await db.execute(select(User).where(User.email == login_data.email))
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(f"Intento de login fallido: usuario '{login_data.email}' no encontrado")
            return None

        # Verificar contraseña
        if not AuthService.verify_password(login_data.password, user.password_hash):
            logger.warning(f"Intento de login fallido: contraseña incorrecta para '{login_data.email}'")
            return None

        # Verificar si el usuario está activo
        if not user.is_active:
            logger.warning(f"Intento de login de usuario inactivo: '{login_data.email}'")
            return None

        logger.info(f"Usuario '{login_data.email}' autenticado exitosamente")

        return user

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Obtiene un usuario por su ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Obtiene un usuario por su email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def change_password(
        db: AsyncSession, user_id: UUID, password_data: PasswordChange
    ) -> bool:
        """Cambia la contraseña de un usuario"""
        user = await AuthService.get_user_by_id(db, user_id)

        if not user:
            return False

        # Verificar contraseña actual
        if not AuthService.verify_password(
            password_data.current_password, user.password_hash
        ):
            raise ValueError("Contraseña actual incorrecta")

        # Actualizar contraseña
        user.password_hash = AuthService.hash_password(password_data.new_password)
        await db.commit()

        logger.info(f"Contraseña cambiada para usuario {user_id}")

        return True