from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.config.database import get_db
from src.features.payment_method import service
from src.features.payment_method.schema import (
    PaymentMethodCreate,
    PaymentMethodUpdate,
    PaymentMethodResponse
)

router = APIRouter(
    prefix="/payment-methods",
    tags=["payment-methods"],
)


@router.get("/", response_model=List[PaymentMethodResponse])
def get_payment_methods(db: Session = Depends(get_db)):
    """Obtener todos los métodos de pago activos"""
    return service.get_payment_methods(db)


@router.get("/{payment_method_id}", response_model=PaymentMethodResponse)
def get_payment_method(payment_method_id: int, db: Session = Depends(get_db)):
    """Obtener un método de pago por ID"""
    payment_method = service.get_payment_method(db, payment_method_id)
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    return payment_method


@router.post("/", response_model=PaymentMethodResponse, status_code=status.HTTP_201_CREATED)
def create_payment_method(
    payment_method: PaymentMethodCreate,
    db: Session = Depends(get_db)
):
    """Crear un nuevo método de pago"""
    return service.create_payment_method(db, payment_method)


@router.put("/{payment_method_id}", response_model=PaymentMethodResponse)
def update_payment_method(
    payment_method_id: int,
    payment_method_update: PaymentMethodUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un método de pago"""
    payment_method = service.update_payment_method(db, payment_method_id, payment_method_update)
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    return payment_method


@router.delete("/{payment_method_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment_method(payment_method_id: int, db: Session = Depends(get_db)):
    """Desactivar un método de pago"""
    success = service.delete_payment_method(db, payment_method_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )