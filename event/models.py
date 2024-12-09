from django.db import models
from django.core.exceptions import ValidationError
from calendars.models import Calendar
from user.models import User
import uuid


class Event(models.Model):
    """
    Event 모델 정의
    - 일정 정보를 저장하며, 캘린더 및 관리 유저와 연동
    """
    event_id = models.UUIDField(
        primary_key=True,  # UUID를 기본 키로 사용
        default=uuid.uuid4,  # 기본값으로 UUID 자동 생성
        editable=False  # 수정 불가
    )
    calendar_id = models.ForeignKey(
        Calendar,  # 캘린더와의 외래키 관계
        on_delete=models.CASCADE,  # 캘린더 삭제 시 관련 이벤트 삭제
        related_name="events"  # 역참조 이름
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
        related_name="events"  # 역참조 이름
    )
    is_public = models.BooleanField(
        default=True, verbose_name="공개 여부"
    )  # 이벤트 공개 여부
    location = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="위치"
    )  # 이벤트 위치 (선택적)

    class Meta:
        """
        메타 정보
        """
        ordering = ["start_time"]  # 시작 시간을 기준으로 정렬
        verbose_name = "이벤트"
        verbose_name_plural = "이벤트"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        """
        이벤트의 문자열 표현
        """
        return f"{self.title} (ID: {self.event_id})"

    def clean(self):
        """
        유효성 검사
        - 종료 시간이 시작 시간보다 앞설 수 없음
        """
        if self.end_time <= self.start_time:
            raise ValidationError("종료 시간은 시작 시간 이후여야 합니다.")

    @staticmethod
    def public_events():
        """
        공개된 이벤트 조회
        """
        return Event.objects.filter(is_public=True)

    @staticmethod
    def private_events():
        """
        비공개 이벤트 조회
        """
        return Event.objects.filter(is_public=False)

    @classmethod
    def get_visible_events(cls, user):
        """
        사용자가 볼 수 있는 이벤트 목록을 반환
        - 공개 이벤트: 모든 사용자가 볼 수 있음
        - 비공개 이벤트: 캘린더 구독자만 볼 수 있음
        """
        return cls.objects.filter(
            Q(is_public=True) |  # 공개 이벤트
            Q(  # 비공개 이벤트 중 구독 중인 캘린더의 이벤트
                is_public=False,
                calendar__subscriptions__user=user,
                calendar__subscriptions__is_active=True
            )
        ).distinct()

    @classmethod
    def get_public_events(cls):
        """공개 이벤트만 반환"""
        return cls.objects.filter(is_public=True)

    @classmethod
    def get_private_events(cls, user):
        """사용자가 구독 중인 비공개 이벤트만 반환"""
        return cls.objects.filter(
            is_public=False,
            calendar__subscriptions__user=user,
            calendar__subscriptions__is_active=True
        ).distinct()