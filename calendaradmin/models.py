from django.db import models

from calendars.models import Calendar
from user.models import User


class CalendarAdmin(models.Model):
    admin_id = models.BigIntegerField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    calendar_id = models.ForeignKey(Calendar, on_delete=models.CASCADE)