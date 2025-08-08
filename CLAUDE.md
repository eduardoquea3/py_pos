# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based backoffice system for point of sale management in a gas station (grifo). It handles internal operations, inventory, sales, users, and administrative reports.

## Development Commands

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
- `DB_PASSWORD`: Database password (default: pos_password)

## Architecture

### Project Structure
- `src/main.py`: FastAPI application entry point with logging configuration
- `src/config/`: Configuration modules for database, logging, API routes, and rate limiting
- `src/auth/`: Authentication module with controller, service, and models
- `src/entities/`: Domain entities (currently empty but prepared for expansion)

### Key Components

**Database Layer (`src/config/database.py`)**
- Custom `DatabaseEngine` class using psycopg2 connection pooling
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
- psycopg2-binary for PostgreSQL connectivity
- bcrypt and passlib for password handling
- JWT for token management
- slowapi for rate limiting
- Alembic for database migrations

## Development Guidelines

### Feature Structure Convention
When creating a new feature folder in `src/features/`, ALWAYS include these five files:
- `__init__.py` - Package initialization
- `routes.py` - FastAPI routes and endpoints
- `model.py` - SQLAlchemy models
- `schema.py` - Pydantic schemas for request/response validation
- `service.py` - Business logic and database operations

**Exception:** For the `common/` folder (static data tables), only include:
- `__init__.py`
- `{table_name}.py` - Named after the actual table (e.g., `countries.py`, `currencies.py`)

Example structure for a regular feature:
```
src/features/products/
├── __init__.py
├── routes.py
├── model.py
├── schema.py
└── service.py
```

Example structure for common/static data:
```
src/features/common/
├── __init__.py
├── countries.py
├── currencies.py
└── payment_methods.py
```

### Adding New Features
1. Create feature folder with required files
2. Add model import to `alembic/env.py`
3. Register routes in `src/config/api.py`
4. Generate migration: `uv run alembic revision --autogenerate -m "Add [feature]"`