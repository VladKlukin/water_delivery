import os
from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app, get_session


@pytest.fixture
def client():
    test_database_url = os.getenv("TEST_DATABASE_URL")

    if not test_database_url:
        pytest.fail("Укажи TEST_DATABASE_URL в файле .env")

    test_engine = create_engine(test_database_url)
    test_session_local = sessionmaker(
        bind=test_engine,
        autoflush=False,
    )

    # Создаем таблицы в тестовой базе по моделям SQLAlchemy
    Base.metadata.create_all(bind=test_engine)

    def get_test_session():
        with test_session_local() as session:
            yield session

    # Подменяем зависимость для запросов из теста
    app.dependency_overrides[get_session] = get_test_session

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_session, None)
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()

def make_order_data():
    # Завтрашний день гарантированно не в прошлом
    tomorrow = date.today() + timedelta(days=1)

    return {
        "customer_name": "Иванов Иван Иванович",
        "email": "ivan@example.com",
        "phone": "79171112233",
        "delivery_address": "Самара, Мичурина 21",
        "bottle_quantity": 2,
        "delivery_date": tomorrow.isoformat(),
        "delivery_start": "12:00:00",
        "delivery_end": "13:00:00",
    }


def test_create_and_cancel_order(client):
    response = client.post("/order", json=make_order_data())

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

    order_id = data["order_id"]

    response = client.get("/order/list")

    assert response.status_code == 200
    order = next(
        item for item in response.json() if item["id"] == order_id
    )
    assert order["status"] == "new"

    response = client.patch(f"/order/{order_id}/cancel")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

    response = client.get("/order/list")
    order = next(
        item for item in response.json() if item["id"] == order_id
    )
    assert order["status"] == "cancelled"


def test_cancel_missing_order(client):
    response = client.patch("/order/999999/cancel")

    assert response.status_code == 404
    assert response.json()["detail"] == "Заказ не найден"   