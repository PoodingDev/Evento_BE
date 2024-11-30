from django.db import models

from user.models import User


class Calendar(models.Model):
    calendar_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    color = models.CharField(max_length=7)
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_calendars"
    )
    invitation_code = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} (ID: {self.calendar_id})"
