# 🏗️ Plan de Sistema Multitenant con Python (DB por Empresa)

## 📘 Descripción General

Este documento define la arquitectura, flujo y base técnica para desarrollar un sistema **multitenant** en **Python** usando una **base de datos por tenant (empresa)**.

El objetivo es permitir que:

- Los usuarios se registren y creen una empresa.
- Cada empresa tenga su **propia base de datos** con sus datos aislados.
- El **subdominio** determine automáticamente a qué base de datos conectarse.

---

## ⚙️ Arquitectura General

### Componentes Principales

| Componente                     | Descripción                                                                                           |
| ------------------------------ | ----------------------------------------------------------------------------------------------------- |
| **DB Central (Registry)**      | Contiene los usuarios globales, la tabla de `tenants` (empresas), y el mapping entre subdominio y DB. |
| **DB por Tenant**              | Cada empresa tiene su propia base de datos con la misma estructura.                                   |
| **Backend (FastAPI o Django)** | Middleware detecta el subdominio y conecta a la DB correspondiente.                                   |
| **Frontend (React / Next.js)** | Cada empresa accede mediante `empresa.ejemplo.com`.                                                   |
| **Nginx / Ingress**            | Usa wildcard `*.ejemplo.com` y reenvía requests al backend.                                           |
| **Migraciones (Alembic)**      | Se ejecutan por cada tenant al crear o actualizar su base.                                            |

---

## 🗂️ Modelo de Datos (DB Central)

### Tabla `tenants`

| Campo           | Tipo      | Descripción                          |
| --------------- | --------- | ------------------------------------ |
| `id`            | UUID      | Identificador único                  |
| `name`          | text      | Nombre de la empresa                 |
| `subdomain`     | text      | Subdominio asignado (`acme`)         |
| `db_name`       | text      | Nombre de la base creada             |
| `db_url`        | text      | URL de conexión (encriptada en prod) |
| `created_at`    | timestamp | Fecha de creación                    |
| `status`        | text      | `active`, `paused`                   |
| `admin_user_id` | uuid      | Usuario administrador (opcional)     |

### Tabla `users` (opcional global)

| Campo           | Tipo | Descripción                 |
| --------------- | ---- | --------------------------- |
| `id`            | uuid | Identificador               |
| `email`         | text | Correo                      |
| `password_hash` | text | Contraseña en hash          |
| `role`          | text | Rol (`admin`, `superadmin`) |
| `tenant_id`     | uuid | Null si es usuario global   |

---

## 🚀 Flujo de Creación de Empresa (Tenant)

1. Un usuario crea una empresa desde el frontend.
2. El backend:
   - Genera un `tenant_id`, `db_name` y `db_url`.
   - Crea la nueva base de datos (`CREATE DATABASE tenant_xxx;`).
   - Ejecuta migraciones de esquema con Alembic.
   - Crea un usuario admin inicial dentro de la DB del tenant.
   - Inserta el registro en la DB central.
3. Se asigna un **subdominio** (`acme.ejemplo.com`).
4. El front usa ese subdominio para acceder a la DB del tenant.

---

## 🌐 Resolución por Subdominio

Ejemplo:
`acme.ejemplo.com` → backend recibe `Host: acme.ejemplo.com`
→ extrae `acme` → busca en `tenants` → obtiene `db_url` → conecta a esa DB.

---

## 💻 Ejemplo Base (FastAPI + SQLAlchemy)

```python
# main.py
from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import threading

app = FastAPI()

CENTRAL_DB_URL = "postgresql://admin:admin@localhost:5432/central_registry"
central_engine = create_engine(CENTRAL_DB_URL)
CentralSessionLocal = sessionmaker(bind=central_engine)

tenant_engines = {}
tenant_engines_lock = threading.Lock()

def get_central_db():
    db = CentralSessionLocal()
    try:
        yield db
    finally:
        db.close()

def extract_subdomain_from_host(host: str, main_domain: str = "ejemplo.com"):
    host_no_port = host.split(":")[0]
    if host_no_port.endswith(main_domain):
        parts = host_no_port.split(".")
        if len(parts) > 2:
            return parts[0]
    return None

def get_tenant_record(db: Session, subdomain: str):
    return db.execute(
        text("SELECT id, subdomain, db_url FROM tenants WHERE subdomain=:s"),
        {"s": subdomain}
    ).first()

def get_or_create_engine(db_url: str):
    with tenant_engines_lock:
        if db_url in tenant_engines:
            return tenant_engines[db_url]
        engine = create_engine(db_url, pool_size=5, max_overflow=10)
        SessionLocal = sessionmaker(bind=engine)
        tenant_engines[db_url] = {"engine": engine, "sessionmaker": SessionLocal}
        return tenant_engines[db_url]

async def get_tenant_session(request: Request, central_db: Session = Depends(get_central_db)):
    host = request.headers.get("host", "")
    subdomain = extract_subdomain_from_host(host)
    if not subdomain:
        raise HTTPException(status_code=400, detail="Subdominio no detectado")
    tenant = get_tenant_record(central_db, subdomain)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant no encontrado")

    db_url = tenant.db_url
    tenant_entry = get_or_create_engine(db_url)
    session = tenant_entry["sessionmaker"]()
    try:
        yield session
    finally:
        session.close()

@app.get("/me")
def read_me(tenant_db: Session = Depends(get_tenant_session)):
    r = tenant_db.execute(text("SELECT 'ok' as status")).first()
    return {"status": r.status}

@app.post("/admin/create-tenant")
def create_tenant(name: str, subdomain: str, central_db: Session = Depends(get_central_db)):
    exists = central_db.execute(text("SELECT 1 FROM tenants WHERE subdomain=:s"), {"s": subdomain}).first()
    if exists:
        raise HTTPException(400, "subdominio existente")

    db_name = f"tenant_{subdomain}"
    try:
        central_engine.execute(text(f"CREATE DATABASE {db_name}"))
    except Exception as e:
        raise HTTPException(500, f"Error creando DB: {e}")

    db_url = f"postgresql://tenant_user:tenant_pass@localhost:5432/{db_name}"
    central_db.execute(text(
        "INSERT INTO tenants (name, subdomain, db_name, db_url, created_at) VALUES (:n, :s, :d, :u, now())"),
        {"n": name, "s": subdomain, "d": db_name, "u": db_url}
    )
    central_db.commit()
    # ejecutar migraciones Alembic
    # run_alembic_upgrade(db_url)
    return {"ok": True, "db_name": db_name}
```
