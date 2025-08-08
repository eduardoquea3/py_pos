# Backoffice Punto de Venta para Grifo

Este proyecto es el sistema de backoffice para la gestión de un punto de venta en un grifo (estación de servicio). Permite administrar operaciones internas, inventario, ventas, usuarios y reportes.

**Funcionalidades principales:**
- Gestión de productos y combustibles.
- Control de inventario.
- Administración de ventas y facturación.
- Gestión de usuarios y roles.
- Generación de reportes administrativos.

**Tecnologías utilizadas:**
- Python
- FastAPI
- PostgreSQL
- uv (gestor de entornos y dependencias)

**Arquitectura del proyecto:**
- `src/main.py`: Punto de entrada de la aplicación FastAPI
- `src/config/`: Módulos de configuración para base de datos, logging, rutas API y rate limiting
- `src/features/`: Características del sistema organizadas por módulos
  - Cada módulo contiene: `routes.py` (endpoints), `model.py` (modelos), `schema.py` (validación), `service.py` (lógica de negocio)
- `src/entities/`: Entidades del dominio

**Instalación y uso:**

### 1. Base de datos (PostgreSQL)
Ejecuta la base de datos con Docker/Podman:
```bash
# Con Docker
docker-compose up -d postgres

# Con Podman usando compose
podman-compose up -d postgres

# O crear contenedor directamente con Podman:
podman run -d --name pg-py-pos \
  -e POSTGRES_DB=pos \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=admin \
  -p 5432:5432 \
  postgres
```

### 2. Aplicación
1. Clona el repositorio.
2. Instala dependencias con `uv`:
   ```bash
   uv sync
   ```
3. Configura las variables de entorno creando un archivo `.env`:
   ```bash
   cp .env.example .env
   # Edita .env con los datos de conexión a PostgreSQL
   ```
4. Ejecuta el servidor de desarrollo:
   ```bash
   uv run fastapi dev src/main.py
   ```
