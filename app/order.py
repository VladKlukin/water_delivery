from datetime import date, time,datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict,field_validator


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(min_length=1, max_length=20)
    delivery_address: str = Field(min_length=1)
    bottle_quantity: int = Field(gt=0)
    delivery_date: date
    delivery_start: time
    delivery_end: time

    @field_validator("delivery_date")
    @classmethod
    def validate_delivery_date(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Дата доставки не может быть в прошлом")

        return value

    @field_validator("delivery_start", "delivery_end")
    @classmethod
    def validate_delivery_time(cls, value: time) -> time:
        if value.utcoffset() is not None:
            raise ValueError("Укажите время без часового пояса")

        return value


class OrderResponse(BaseModel):
    status: str
    order_id: int

class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    email: EmailStr
    phone: str
    delivery_address: str
    bottle_quantity: int
    delivery_date: date | datetime
    delivery_start: time
    delivery_end: time
    status: str
    created_at: datetime