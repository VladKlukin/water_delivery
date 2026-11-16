from datetime import datetime, time

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Integer,
    String,
    Text,
    Time,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Orders(Base):
    __tablename__ = "orders"

    __table_args__ = (
        CheckConstraint(
            "bottle_quantity > 0",
            name="check_bottle_quantity_positive",
        ),
        CheckConstraint(
            "delivery_start < delivery_end",
            name="check_delivery_time",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    customer_name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(254))
    phone: Mapped[str] = mapped_column(Text)
    delivery_address: Mapped[str] = mapped_column(String(500))

    bottle_quantity: Mapped[int] = mapped_column(Integer)

    delivery_date: Mapped[datetime] = mapped_column(DateTime)
    delivery_start: Mapped[time] = mapped_column(Time)
    delivery_end: Mapped[time] = mapped_column(Time)

    status: Mapped[str] = mapped_column(String(20))

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )