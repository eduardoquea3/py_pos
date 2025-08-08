from pydantic import BaseModel
from typing import Optional


class PaymentMethodBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    requires_reference: bool = False


class PaymentMethodCreate(PaymentMethodBase):
    pass


class PaymentMethodUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    requires_reference: Optional[bool] = None


class PaymentMethodResponse(PaymentMethodBase):
    id_payment_method: int
    
    class Config:
        from_attributes = True