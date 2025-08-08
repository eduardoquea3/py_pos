from sqlalchemy.orm import Session
from src.features.payment_method.model import PaymentMethod
from src.features.payment_method.schema import PaymentMethodCreate, PaymentMethodUpdate
from typing import List, Optional


def get_payment_methods(db: Session) -> List[PaymentMethod]:
    """Obtener todos los métodos de pago"""
    return db.query(PaymentMethod).filter(PaymentMethod.is_active == True).all()


def get_payment_method(db: Session, payment_method_id: int) -> Optional[PaymentMethod]:
    """Obtener un método de pago por ID"""
    return db.query(PaymentMethod).filter(
        PaymentMethod.id_payment_method == payment_method_id
    ).first()


def create_payment_method(db: Session, payment_method: PaymentMethodCreate) -> PaymentMethod:
    """Crear un nuevo método de pago"""
    db_payment_method = PaymentMethod(**payment_method.dict())
    db.add(db_payment_method)
    db.commit()
    db.refresh(db_payment_method)
    return db_payment_method


def update_payment_method(
    db: Session, 
    payment_method_id: int, 
    payment_method_update: PaymentMethodUpdate
) -> Optional[PaymentMethod]:
    """Actualizar un método de pago"""
    db_payment_method = get_payment_method(db, payment_method_id)
    if db_payment_method:
        update_data = payment_method_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_payment_method, field, value)
        db.commit()
        db.refresh(db_payment_method)
    return db_payment_method


def delete_payment_method(db: Session, payment_method_id: int) -> bool:
    """Desactivar un método de pago (soft delete)"""
    db_payment_method = get_payment_method(db, payment_method_id)
    if db_payment_method:
        db_payment_method.is_active = False
        db.commit()
        return True
    return False