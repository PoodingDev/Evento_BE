from django.db import models

from event.models import Event
from user.models import User


class FavoriteEvent(models.Model):
    favorite_event_id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    d_day = models.DateField(auto_now_add=True)
    easy_insidebar = models.BooleanField(default=True)
