import random
import string
import uuid

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
        try:
            is_new = self.pk is None
            if not self.invitation_code:
                self.invitation_code = self.generate_invitation_code()
            super().save(*args, **kwargs)

            if is_new:
                CalendarAdmin.objects.get_or_create(user=self.creator, calendar=self)
        except Exception as e:
            print(f"Error during save: {e}")
            raise

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
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

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

class Event(models.Model):
    """
    Event 모델 정의
    - 일정 정보를 저장하며, 캘린더 및 관리 유저와 연동
    """

    event_id = models.UUIDField(
        primary_key=True,  # UUID를 기본 키로 사용
        default=uuid.uuid4,  # 기본값으로 UUID 자동 생성
        editable=False,  # 수정 불가
    )
    calendar_id = models.ForeignKey(
        Calendar,  # 캘린더와의 외래키 관계
        on_delete=models.CASCADE,  # 캘린더 삭제 시 관련 이벤트 삭제
        related_name="calendar_app_events",  # 역참조 이름
    )
    title = models.CharField(max_length=255, verbose_name="이벤트 제목")  # 이벤트 제목
    description = models.TextField(
        null=True, blank=True, verbose_name="이벤트 설명"
    )  # 이벤트 설명 (선택적)
    start_time = models.DateTimeField(verbose_name="시작 시간")  # 시작 시간
    end_time = models.DateTimeField(verbose_name="종료 시간")  # 종료 시간
    admin_id = models.ForeignKey(
        User,  # 유저와의 외래키 관계
        on_delete=models.CASCADE,  # 유저 삭제 시 관련 이벤트 삭제
        related_name="calendar_events",  # 역참조 이름
    )
    is_public = models.BooleanField(
        default=False, verbose_name="공개 여부"
    )  # 이벤트 공개 여부
    is_active = models.BooleanField()
    location = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="위치"
    )  # 이벤트 위치 (선택적)