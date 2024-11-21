from django.db import models
from calendars.models import Calendar
from users.models import User

class Event(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255, null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
