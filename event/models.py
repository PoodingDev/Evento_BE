from django.db import models
from calendars.models import Calendar
from user.models import User

class Event(models.Model):
    event_id = models.BigIntegerField(primary_key=True)
    calendar_id = models.ForeignKey(Calendar, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    admin_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    # location = models.CharField(max_length=255, null=True, blank=True)
