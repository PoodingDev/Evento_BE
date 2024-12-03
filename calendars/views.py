from rest_framework.filters import SearchFilter
from rest_framework.generics import (
    DestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from user.models import User
from .models import Calendar, Subscription
from .serializers import CalendarSerializer, SubscriptionSerializer


class CalendarListCreateAPIView(ListCreateAPIView):
    """
    캘린더 목록 조회 및 생성
    """
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]  # 인증 없이 접근 가능

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # 현재 사용자가 생성한 캘린더만 조회
            return self.queryset.filter(creator=self.request.user)
        return Calendar.objects.none()  # 인증되지 않은 경우 빈 쿼리셋 반환

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            # 캘린더 생성 시 요청 사용자를 소유자로 설정
            serializer.save(creator=self.request.user)


class CalendarRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    캘린더 상세 조회, 수정, 삭제
    """
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]  # 인증 없이 접근 가능

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # 현재 사용자가 생성한 캘린더만 접근 가능
            return self.queryset.filter(creator=self.request.user)
        return Calendar.objects.none()


class SubscriptionListCreateAPIView(ListCreateAPIView):
    """
    구독한 캘린더 조회 및 구독 추가
    """
    serializer_class = SubscriptionSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]  # 인증 없이 접근 가능

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # 현재 사용자가 구독한 캘린더 목록 반환
            return Subscription.objects.filter(user=self.request.user)
        return Subscription.objects.none()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            # 구독 생성 시 요청 사용자를 설정
            serializer.save(user=self.request.user)


class SubscriptionDeleteAPIView(DestroyAPIView):
    """
    구독 삭제
    """
    serializer_class = SubscriptionSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]  # 인증 없이 접근 가능

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # 현재 사용자가 구독한 캘린더만 삭제 가능
            return Subscription.objects.filter(user=self.request.user)
        return Subscription.objects.none()


class CalendarSearchAPIView(ListAPIView):
    """
    공개된 캘린더 검색
    """
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name", "creator__nickname"]

    def get_queryset(self):
        # 공개된 캘린더만 검색 가능
        return Calendar.objects.filter(is_public=True)


class AdminCalendarsAPIView(ListAPIView):
    """
    관리 권한이 있는 캘린더 목록 조회
    """
    serializer_class = CalendarSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]  # 인증 없이 접근 가능

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # 사용자가 관리자인 캘린더만 반환
            return Calendar.objects.filter(creator=self.request.user)
        return Calendar.objects.none()


class CalendarMembersAPIView(ListAPIView):
    """
    캘린더에 속한 관리자 멤버 조회
    """
    serializer_class = SubscriptionSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]  # 인증 없이 접근 가능

    def get_queryset(self):
        calendar_id = self.kwargs.get("pk")
        if calendar_id:
            # 특정 캘린더에 속한 구독 사용자 조회
            return Subscription.objects.filter(calendar_id=calendar_id)
        return Subscription.objects.none()
