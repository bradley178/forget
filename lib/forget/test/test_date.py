from forget.date import friendly_display
from datetime import datetime, timedelta

class TestDateDisplay(object):
    def test_now(self):
        assert "now" == friendly_display(datetime.now())

    def test_tomorrow(self):
        assert "tomorrow" == friendly_display(datetime.now() + timedelta(days=1))

    def test_3_days(self):
        assert "in 3 days" == friendly_display(datetime.now() + timedelta(days=3))

    def test_10_minutes(self):
        assert "in 10 minutes" == friendly_display(datetime.now() + timedelta(minutes=10))

    def test_45_minutes(self):
        assert "in 45 minutes" == friendly_display(datetime.now() + timedelta(minutes=45))

    def test_1_hour(self):
        assert "in an hour" == friendly_display(datetime.now() + timedelta(hours=1))

    def test_1_hour_10_minutes(self):
        assert "in an hour" == friendly_display(datetime.now() + timedelta(hours=1, minutes=10))

    def test_1_hour_45_minutes(self):
        assert "in 2 hours" == friendly_display(datetime.now() + timedelta(hours=1, minutes=45))

    def test_2_hours(self):
        assert "in 2 hours" == friendly_display(datetime.now() + timedelta(hours=2))
