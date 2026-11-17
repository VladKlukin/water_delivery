from datetime import date, time

from app.main import get_delivery_intervals


def test_weekday_intervals():
    # 18 ноября 2026 года - среда
    intervals = get_delivery_intervals(date(2026, 11, 18))

    assert intervals == [
        (time(10, 0), time(11, 0)),
        (time(12, 0), time(13, 0)),
        (time(15, 0), time(16, 0)),
    ]


def test_weekend_intervals():
    # 21 ноября 2026 года - суббота
    intervals = get_delivery_intervals(date(2026, 11, 21))

    assert intervals == [
        (time(12, 0), time(13, 0)),
        (time(15, 0), time(16, 0)),
    ]