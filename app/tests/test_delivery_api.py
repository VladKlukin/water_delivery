from datetime import date, datetime, timedelta
from fastapi.testclient import TestClient
import app.main as main
from app.main import app

client = TestClient(app)


def test_get_delivery_slots():
    # Находим ближайшую будущую субботу
    today = date.today()
    days_until_saturday = (5 - today.weekday()) % 7 or 7
    saturday = today + timedelta(days=days_until_saturday)

    response = client.get(
        "/delivery-slots",
        params={"delivery_date": saturday.isoformat()},
    )

    assert response.status_code == 200
    assert response.json() == {
        "date": saturday.isoformat(),
        "intervals": [
            {"start": "12:00:00", "end": "13:00:00"},
            {"start": "15:00:00", "end": "16:00:00"},
        ],
    }


def test_get_delivery_slots_for_past_date():
    yesterday = date.today() - timedelta(days=1)

    response = client.get(
        "/delivery-slots",
        params={"delivery_date": yesterday.isoformat()},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Дата доставки не может быть в прошлом"


def test_today_started_interval_is_unavailable(monkeypatch):
    class FixedDatetime(datetime):
        @classmethod
        def now(cls):
            return cls.combine(date.today(), datetime.strptime("12:00", "%H:%M").time())

    monkeypatch.setattr(main, "datetime", FixedDatetime)
    today = date.today().isoformat()
    response = client.get("/delivery-slots", params={"delivery_date": today})
    assert response.status_code == 200
    assert response.json()["intervals"] == [{"start": "15:00:00", "end": "16:00:00"}]

    response = client.post("/order", json={
        "customer_name": "Иван Иванов", "email": "ivan@example.com",
        "phone": "79171112233", "delivery_address": "Самара",
        "bottle_quantity": 1, "delivery_date": today,
        "delivery_start": "12:00:00", "delivery_end": "13:00:00",
    })
    assert response.status_code == 422
