import string
from random import random

from django.conf import settings
from django.db import models

from user.models import User


class Calendar(models.Model):
    calendar_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_calendars",
    )
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="CalendarAdmin",
        related_name="admin_calendars",
        blank=True,
    )
    description = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    color = models.CharField(max_length=7)
    created_at = models.DateTimeField(auto_now_add=True)
    invitation_code = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "calendars"  # 테이블명 명시적 지정

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # 객체가 새로 생성되는 경우 확인
        if not self.invitation_code:
            self.invitation_code = self.generate_invitation_code()
        super().save(*args, **kwargs)

        if is_new:
            # 새로운 캘린더 생성 시 creator를 member로 추가 및 is_active 초기화
            Subscription.objects.create(
                user=self.creator, calendar=self, is_active=True
            )

        # 생성자를 자동으로 관리자로 추가
        if (
            self.pk
            and not CalendarAdmin.objects.filter(
                user=self.creator, calendar=self
            ).exists()
        ):
            CalendarAdmin.objects.create(user=self.creator, calendar=self)

    def __str__(self):
        return f"{self.name} (ID: {self.calendar_id})"

    @staticmethod
    def generate_invitation_code():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def has_admin_permission(self, user):
        """사용자의 관리자 권한 확인"""
        return user == self.creator or self.admins.filter(id=user.id).exists()


class Subscription(models.Model):
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="subscriptions"
    )
    calendar = models.ForeignKey(
        "calendars.Calendar", on_delete=models.CASCADE, related_name="subscriptions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=True)  # 사이드바 표시 여부
    is_on_calendar = models.BooleanField(default=True)  # 캘린더에 표시 여부
    is_active = models.BooleanField(default=True)  # 체크박스 상태

    class Meta:
        pass
        # unique_together = ("user", "calendar")
        # ordering = ("created_at",)

    def __str__(self):
        return f"{self.user.nickname} subscribed to {self.calendar.name}"


class CalendarAdmin(models.Model):
    """
    캘린더 관리자 정보 저장
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="calendar_admin_roles"
    )
    calendar = models.ForeignKey(
        Calendar, on_delete=models.CASCADE, related_name="calendar_admins"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} is admin of {self.calendar}"
