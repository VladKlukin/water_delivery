from collections.abc import Generator
import uvicorn
from fastapi import Depends, FastAPI,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.order import OrderRead
from .database import SessionLocal
from .models import Orders
from .order import OrderCreate, OrderResponse
from datetime import datetime, time,date
from pathlib import Path
from fastapi.responses import FileResponse
app = FastAPI()

@app.get("/orders", include_in_schema=False)
def show_orders_page():
    file_path = Path(__file__).parent / "static" / "orders.html"
    return FileResponse(file_path)

@app.get("/", include_in_schema=False)
def show_order_form():
    file_path = Path(__file__).parent / "static" / "index.html"
    return FileResponse(file_path)


def get_delivery_intervals(delivery_date: date) -> list[tuple[time, time]]:
    intervals = [
        (time(12, 0), time(13, 0)),
        (time(15, 0), time(16, 0)),
    ]


    if delivery_date.weekday() < 5:
        intervals.insert(0, (time(10, 0), time(11, 0)))

    return intervals

def get_available_intervals(delivery_date: date) -> list[tuple[time, time]]:
    now = datetime.now()
    intervals = get_delivery_intervals(delivery_date)
    if delivery_date == now.date():
        return [interval for interval in intervals if interval[0] > now.time()]
    return intervals

def validate_delivery_interval(order_data: OrderCreate) -> None:
    selected_interval = (
        order_data.delivery_start,
        order_data.delivery_end,
    )

    if selected_interval not in get_available_intervals(order_data.delivery_date):
        raise HTTPException(
            status_code=422,
            detail="Этот интервал доставки недоступен в выбранный день",
        )

def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session

@app.post("/order", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate,
    session: Session = Depends(get_session),
):
    validate_delivery_interval(order_data)
    order = Orders(
    **order_data.model_dump(),
    status="new",
)

    session.add(order)
    session.commit()
    session.refresh(order)

    return OrderResponse(status="success", order_id=order.id)

@app.get("/order/list", response_model=list[OrderRead])
def get_orders(session: Session = Depends(get_session)):
    query = select(Orders).order_by(Orders.id)
    orders = session.scalars(query).all()

    return orders

@app.get("/delivery-slots")
def get_slots(delivery_date: date):
    if delivery_date < date.today():
        raise HTTPException(
            status_code=422,
            detail="Дата доставки не может быть в прошлом",
        )

    intervals = get_available_intervals(delivery_date)

    return {
        "date": delivery_date,
        "intervals": [
            {"start": start, "end": end}
            for start, end in intervals
        ],
    }
@app.patch("/order/{order_id}/cancel")
def cancel_order(
    order_id: int,
    session: Session = Depends(get_session),
):
    order = session.get(Orders, order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Заказ не найден",
        )

    order.status = "cancelled"
    session.commit()
    session.refresh(order)

    return {
        "message": "Заказ отменен",
        "order_id": order.id,
        "status": order.status,
    }


if __name__ == "__main__":   
    uvicorn.run("app.main:app",reload=True)
