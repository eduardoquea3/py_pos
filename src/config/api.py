from fastapi import FastAPI
from src.features.auth.routes import router as auth_router
from src.features.payment_method.routes import router as payment_method_router


def register_routes(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(payment_method_router)
