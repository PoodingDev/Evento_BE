from django.db import models
from django.utils import timezone

from event.models import Event
from user.models import User


class FavoriteEvent(models.Model):
    favorite_event_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    easy_insidebar = models.BooleanField(default=True)

    def calculate_d_day(self):
        """
        현재 날짜와 이벤트 시작 날짜의 차이를 계산하여 D-day 반환
        """
        try:
            today = timezone.localtime().date()
            event_date = self.event_id.start_time.date()

            diff = (event_date - today).days

            if diff > 0:
                return f"D-{diff}"
            elif diff < 0:
                return f"D+{abs(diff)}"
            else:
                return "D-Day"
        except Exception as e:
            print(f"Error calculating d_day: {str(e)}")
            return None

    class Meta:
        db_table = "favorite_event"
