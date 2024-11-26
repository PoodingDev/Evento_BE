# calendars/models.py

from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()  # start_time으로 필드 이름을 통일

    def __str__(self):
        return self.title
