from django.urls import path
from .views import EventListCreateAPIView, EventDetailAPIView

urlpatterns = [
    # 전체 이벤트 조회 및 생성
    path('events/', EventListCreateAPIView.as_view(), name='event-list-create'),

    # 특정 이벤트 조회, 수정, 삭제
    path('events/<int:pk>/', EventDetailAPIView.as_view(), name='event-detail'),
]