from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Event
from .serializers import EventSerializer

# Create your views here.
# 이벤트 목록 조회 및 생성
class EventListCreateAPIView(ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()  # 추가적으로 필요한 로직이 있다면 여기에 추가

# 이벤트 상세 조회, 수정, 삭제
class EventRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]