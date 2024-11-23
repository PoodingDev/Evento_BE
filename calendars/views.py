from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Calendar
from .serializers import CalendarSerializer

# 캘린더 목록 조회 및 생성
class CalendarListCreateAPIView(ListCreateAPIView):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 가능

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)  # 캘린더 소유자 저장

# 캘린더 상세 조회, 수정, 삭제
class CalendarRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 가능

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)  # 자신의 캘린더만 보이게