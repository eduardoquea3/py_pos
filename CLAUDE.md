# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based backoffice system for point of sale management in a gas station (grifo). It handles internal operations, inventory, sales, users, and administrative reports.

### Multitenant Architecture

This system follows a **database-per-tenant** multitenant architecture. Each company (tenant) has its own isolated PostgreSQL database, with subdomain-based routing to determine which database to connect to.

**Key architectural document:** `docs/base.md` - Contains the complete multitenant architecture plan, including:
- Database schema for central registry and tenant databases
- Subdomain resolution flow
- Tenant creation process
- FastAPI implementation examples with SQLAlchemy

Always reference `docs/base.md` when working on multitenant features or database isolation.

#### Database Separation

The system uses **two separate databases**:

1. **Central DB** (`DB_URL` in settings.py):
   - Contains ONLY: `tenants` and `companies` tables
   - Managed by main Alembic: `alembic.ini` / `alembic/`
   - Uses `CentralBase` from `src/config/db.py`
   - Models: `src/modules/tenant/model.py`, `src/modules/company/model.py`

2. **Tenant DBs** (one per tenant):
   - Contains ALL business models: `users`, `serie`, products, sales, etc.
   - Managed by tenant Alembic: `alembic_tenant.ini` / `alembic_tenant/`
   - Uses `TenantBase` from `src/config/db.py`
   - Models: `src/modules/user/`, `src/modules/serie/`, etc.

**Important:** When creating new models, determine if they belong to:
- Central DB (tenant management) → use `CentralBase` and update `alembic/env.py`
- Tenant DB (business data) → use `TenantBase` and update `alembic_tenant/env.py`

## Development Commands

### Database Migrations

#### Central DB Migrations (tenants & companies)
```bash
# Generate migration for central DB
uv run alembic revision --autogenerate -m "Description"

# Apply migrations to central DB
uv run alembic upgrade head

# View current version
uv run alembic current
```

#### Tenant DB Migrations (users, series, business data)
```bash
# Generate migration for tenant DBs
uv run alembic -c alembic_tenant.ini revision --autogenerate -m "Description"

# Apply migrations to a specific tenant DB
TENANT_DB_URL="postgresql://user:pass@localhost:5432/tenant_acme" \
  uv run alembic -c alembic_tenant.ini upgrade head

# View current version of tenant DB
TENANT_DB_URL="postgresql://user:pass@localhost:5432/tenant_acme" \
  uv run alembic -c alembic_tenant.ini current
```

### Database Setup
```bash
# Start PostgreSQL with Docker
docker-compose up -d postgres

# With Podman
podman-compose up -d postgres

# Or manually with Podman
podman run -d --name pos_postgres \
  -e POSTGRES_DB=pos_database \
  -e POSTGRES_USER=pos_user \
  -e POSTGRES_PASSWORD=pos_password \
  -p 5432:5432 \
  postgres:15
```

### Application Setup and Run
```bash
# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with database connection details

# Run development server
uv run fastapi dev src/main.py

# Run production server
uv run fastapi run src/main.py
```

### Environment Configuration
Configure `.env` file with PostgreSQL connection details:
- `DB_HOST`: Database host (default: localhost)
- `DB_NAME`: Database name (default: pos_database)
- `DB_USER`: Database user (default: pos_user)
- `DB_PASS`: Database password (default: pos_password)
- `DB_PORT`: Database port (default: 5432)
- `DB_URL`: Database URL (default: postgresql://pos_user:pos_password@localhost:5432/pos_database)

## Architecture

### Project Structure
- `src/main.py`: FastAPI application entry point with logging configuration
- `src/config/`: Configuration modules for database, logging, API routes, and rate limiting
- `src/auth/`: Authentication module with controller, service, and models
- `src/entities/`: Domain entities (currently empty but prepared for expansion)

### Key Components

**Database Layer (`src/config/database.py`)**
- Custom `DatabaseEngine` class using psycopg (version 3) connection pooling
- Supports stored procedure execution via `execute_procedure()` method
- Uses environment variables for database configuration

**Authentication (`src/features/auth/`)**
- Model-based approach with Pydantic models for request/response validation
- Service layer that calls stored procedures for user operations
- Currently implements `find_user()` functionality via `find_by_username` stored procedure

**Configuration System**
- Centralized logging configuration with different log levels (INFO, WARN, ERROR, DEBUG)
- Rate limiting setup using slowapi
- Modular route registration system

### Database Integration
The application expects PostgreSQL stored procedures for database operations:
- `find_by_username(username)`: Returns user data for authentication

### Dependencies
Key technologies used:
- FastAPI with standard extras for web framework
- psycopg (version 3) for PostgreSQL connectivity with async support
- bcrypt and passlib for password handling
- JWT for token management
- slowapi for rate limiting
- Alembic for database migrations

## Development Guidelines

### Module Structure Convention
When creating a new module folder in `src/modules/`, ALWAYS include these five files:
- `__init__.py` - Package initialization
- `router.py` - FastAPI routes and endpoints
- `model.py` - SQLAlchemy models (inherit from `CentralBase` or `TenantBase`)
- `schema.py` - Pydantic schemas for request/response validation
- `service.py` - Business logic and database operations (use FUNCTIONS, not classes)

**Exception:** For the `common/` folder (static data tables), only include:
- `__init__.py`
- `{table_name}.py` - Named after the actual table (e.g., `countries.py`, `currencies.py`)

Example structure for a tenant module (business data):
```
src/modules/products/
├── __init__.py
├── router.py
├── model.py          # class Product(TenantBase): ...
├── schema.py
└── service.py        # def create_product(db, data): ...
```

Example structure for a central module (tenant management):
```
src/modules/company/
├── __init__.py
├── router.py
├── model.py          # class Company(CentralBase): ...
├── schema.py
└── service.py        # def create_company(db, data): ...
```

### Adding New Features
1. Determine if the feature belongs to Central DB or Tenant DB
2. Create module folder with required files
3. **For Central DB modules:**
   - Use `CentralBase` in model.py
   - Add model import to `alembic/env.py` (Central models section)
   - Generate migration: `uv run alembic revision --autogenerate -m "Add [feature]"`
4. **For Tenant DB modules:**
   - Use `TenantBase` in model.py
   - Add model import to `alembic_tenant/env.py` (Tenant models section)
   - Generate migration: `uv run alembic -c alembic_tenant.ini revision --autogenerate -m "Add [feature]"`
5. Register routes in `src/config/api.py`
