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

**Instalación y uso:**
1. Clona el repositorio.
2. Crea un entorno y activa dependencias con `uv`:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```
3. Configura las variables de entorno para la conexión a la base de datos PostgreSQL.
4. Ejecuta el servidor:
   ```bash
   uvicorn main:app --reload
   ```
