import os
import re
import subprocess
import unicodedata

from sqlalchemy import create_engine, text

from src.config.settings import settings


def normalize_db_name(company_name: str) -> str:
    """
    Normaliza el nombre de una compañía para usarlo como nombre de base de datos.

    Reglas:
    - Convierte a minúsculas
    - Reemplaza acentos por vocales sin acento (á->a, é->e, etc.)
    - Reemplaza espacios por guion bajo (_)
    - Reemplaza puntos (.) por guion bajo (_)
    - Elimina caracteres especiales
    - Prefijo: tn_

    Ejemplos:
    - "Panadería Juan" -> "tn_panaderia_juan"
    - "Empresa S.A.C." -> "tn_empresa_s_a_c_"
    - "Café José" -> "tn_cafe_jose"

    Args:
        company_name: Nombre de la compañía

    Returns:
        str: Nombre normalizado para la base de datos
    """
    # Normalizar caracteres Unicode (descomponer acentos)
    normalized = unicodedata.normalize("NFD", company_name)
    # Eliminar marcas diacríticas (acentos)
    without_accents = "".join(
        char for char in normalized if unicodedata.category(char) != "Mn"
    )

    # Convertir a minúsculas
    lower = without_accents.lower()

    # Reemplazar puntos por guion bajo
    no_dots = lower.replace(".", "_")

    # Reemplazar espacios por guion bajo
    no_spaces = no_dots.replace(" ", "_")

    # Eliminar caracteres que no sean alfanuméricos o guion bajo
    clean = re.sub(r"[^a-z0-9_]", "", no_spaces)

    # Eliminar guiones bajos múltiples consecutivos
    clean = re.sub(r"_+", "_", clean)

    # Eliminar guiones bajos solo al inicio (mantener los del final)
    clean = clean.lstrip("_")

    # Agregar prefijo
    db_name = f"tn_{clean}"

    return db_name


def create_tenant_db(db_name: str) -> str:
    """
    Crea una nueva base de datos para un tenant.

    Args:
        db_name: Nombre de la base de datos (ej: 'tenant_acme')

    Returns:
        str: URL de conexión a la nueva base de datos
    """
    # Usar isolation_level='AUTOCOMMIT' para CREATE DATABASE
    engine = create_engine(settings.DB_URL, isolation_level="AUTOCOMMIT", echo=False)

    try:
        with engine.connect() as conn:
            # Verificar si la DB ya existe
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": db_name},
            )
            if result.fetchone():
                raise ValueError(f"La base de datos '{db_name}' ya existe")

            # Crear la base de datos
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))

        print(f"✓ Base de datos '{db_name}' creada exitosamente")

        # Construir la URL de conexión
        db_url = f"postgresql://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{db_name}"
        return db_url

    except Exception as e:
        print(f"✗ Error creando base de datos: {e}")
        raise
    finally:
        engine.dispose()


def run_tenant_migrations(db_url: str):
    """
    Ejecuta las migraciones de Alembic para la base de datos de un tenant.

    Args:
        db_url: URL de conexión a la base de datos del tenant
    """
    # Configurar la variable de entorno para que alembic_tenant use esta DB
    env = os.environ.copy()
    env["TENANT_DB_URL"] = db_url

    try:
        # Ejecutar alembic upgrade head
        result = subprocess.run(
            ["uv", "run", "alembic", "-c", "alembic_tenant.ini", "upgrade", "head"],
            env=env,
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"✓ Migraciones aplicadas exitosamente a {db_url}")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"✗ Error ejecutando migraciones: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise
