
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Calendar, Subscription
from .serializers import CalendarSerializer, SubscriptionSerializer


class CalendarListCreateAPIView(ListCreateAPIView):
    """
    캘린더 목록 조회 및 생성
    """
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 접근 가능

    def get_queryset(self):
        # 자신의 캘린더만 조회
        return self.queryset.filter(creator=self.request.user)

    def perform_create(self, serializer):
        # 생성 시 캘린더 소유자를 요청 사용자로 설정
        serializer.save(creator=self.request.user)


class CalendarRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    캘린더 상세 조회, 수정, 삭제
    """
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 자신의 캘린더만 조회 가능
        return self.queryset.filter(creator=self.request.user)


class SubscriptionListCreateAPIView(ListCreateAPIView):
    """
    구독한 캘린더 조회 및 구독 추가
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 현재 사용자의 구독 정보만 반환
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # 구독 생성 시 사용자 설정
        serializer.save(user=self.request.user)


class SubscriptionDeleteAPIView(DestroyAPIView):
    """
    구독 삭제
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 현재 사용자의 구독 정보만 반환
        return Subscription.objects.filter(user=self.request.user)

