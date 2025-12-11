import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config.db import TenantBase
from src.config.settings import settings

# ============================================
# MODELOS DE LA DB TENANT
# ============================================
from src.modules.serie.model import Serie  # noqa: F401
from src.modules.user.model import User  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# IMPORTANTE: Este alembic maneja SOLO las DB de tenants (users, series, etc.)
# Para la DB central (tenants y companies), se usa el alembic principal
target_metadata = TenantBase.metadata


def get_url():
    """
    Obtiene la URL de la base de datos del tenant.
    Por defecto usa DB_URL, pero puede ser sobrescrito con TENANT_DB_URL
    para aplicar migraciones a un tenant específico.
    """
    return os.getenv("TENANT_DB_URL", settings.DB_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
