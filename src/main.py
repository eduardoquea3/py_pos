from fastapi import FastAPI
from config.logging import configure_logging, LogLevels
from config.api import register_routes

configure_logging(LogLevels.info)

app = FastAPI()

register_routes(app)
