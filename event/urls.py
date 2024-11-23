from django.urls import path
from .views import EventListCreateAPIView, EventRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('events/', EventListCreateAPIView.as_view(), name='event-list-create'),  # 이벤트 목록 조회 및 생성
    path('events/<int:pk>/', EventRetrieveUpdateDestroyAPIView.as_view(), name='event-detail'),  # 이벤트 상세 조회, 수정, 삭제
]
