from fastapi import FastAPI
from src.config.logging import configure_logging, LogLevels
from src.config.api import register_routes
from src.config.database import run_migrations

configure_logging(LogLevels.info)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    run_migrations()

register_routes(app)
