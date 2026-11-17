from datetime import date, timedelta

from fastapi.testclient import TestClient

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