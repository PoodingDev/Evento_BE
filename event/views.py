from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Event
from .serializers import EventSerializer


class EventListCreateAPIView(ListCreateAPIView):
    """
    Event 목록 조회 및 생성
    """

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["이벤트"])
    def perform_create(self, serializer):
        # 생성 시 요청 사용자를 admin_id로 설정
        serializer.save(admin_id=self.request.user)


class EventRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    Event 상세 조회, 수정, 삭제
    """

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["이벤트"])
    def get_queryset(self):
        # 요청 사용자가 admin_id인 이벤트만 조회 가능
        return self.queryset.filter(admin_id=self.request.user)
