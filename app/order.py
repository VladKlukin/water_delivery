from datetime import date, time

from pydantic import BaseModel, EmailStr, Field


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(min_length=1, max_length=20)
    delivery_address: str = Field(min_length=1)
    bottles_quantity: int = Field(gt=0)
    delivery_date: date
    delivery_start: time
    delivery_end: time


class OrderResponse(BaseModel):
    status: str
    order_id: int