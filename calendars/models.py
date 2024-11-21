from django.db import models
from users.models import User

class Calendar(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=False)
    color = models.CharField(max_length=20, null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_calendars')
    invitation_code = models.CharField(max_length=255, null=True, blank=True)
