from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from calendars.models import Event

class FavoriteEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 사용자와 연관
    event = models.ForeignKey(Event, on_delete=models.CASCADE)  # 이벤트와 연관
    created_at = models.DateTimeField(auto_now_add=True)  # 즐겨찾기 추가 시간
    description = models.CharField(max_length=255, null=False, default='기본값')  # description 필드 추가

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"
