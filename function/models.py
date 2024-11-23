from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import User

class Alarm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 알림을 받을 사용자
    message = models.CharField(max_length=255)  # 알림 내용
    is_read = models.BooleanField(default=False)  # 알림 읽음 여부
    created_at = models.DateTimeField(auto_now_add=True)  # 알림 생성 시간

    def __str__(self):
        return f"알림: {self.message} - 사용자: {self.user.username}"
