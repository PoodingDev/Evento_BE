from django.db import models

from event.models import Event
from user.models import User


class Comment(models.Model):
    comment_id = models.BigAutoField(primary_key=True)
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_id = models.ForeignKey(User, on_delete=models.CASCADE)
