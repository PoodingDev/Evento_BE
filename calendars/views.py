
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from .models import Calendar, Subscription
from user.models import User
from .serializers import CalendarSerializer, SubscriptionSerializer


class CalendarListCreateAPIView(ListCreateAPIView):
    """
    캘린더 목록 조회 및 생성
    """
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    # permission_classes = [IsAuthenticated]  # 로그인한 사용자만 접근 가능
    permission_classes = [AllowAny]  # 인증 없이 접근 가능

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

# 캘린더 검색
class CalendarSearchAPIView(ListAPIView):
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'creator__nickname']  # 닉네임 검색 가능

    def get_queryset(self):
        return Calendar.objects.filter(is_public=True)

class AdminCalendarsAPIView(ListAPIView):
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Calendar.objects.filter(creator=self.request.user)


class CalendarMembersAPIView(ListAPIView):
    serializer_class = serializers.StringRelatedField(many=True)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        calendar_id = self.kwargs.get('pk')
        return User.objects.filter(created_calendars__calendar_id=calendar_id)