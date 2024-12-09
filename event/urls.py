from django.urls import path
from .views import (
    PublicEventListAPIView,
    PublicEventListCreateAPIView,
    PrivateEventListAPIView,
    PrivateEventListCreateAPIView,
    EventRetrieveUpdateDestroyAPIView,
    EventUploadView,
    UserRelatedEventListAPIView,
    PublicEventViewSet,
    PrivateEventViewSet,
    EventDetailView
)

urlpatterns = [
    # 공개 이벤트 목록 조회
    path("public/list/", PublicEventListAPIView.as_view(), name="public-event-list"),
    # 공개 이벤트 생성
    path("public/create/", PublicEventListCreateAPIView.as_view(), name="public-event-create"),

    # 비공개 이벤트 목록 조회
    path("private/list/", PrivateEventListAPIView.as_view(), name="private-event-list"),
    # 비공개 이벤트 생성
    path("private/create/", PrivateEventListCreateAPIView.as_view(), name="private-event-create"),

    # 이벤트 상세 조회, 수정, 삭제
    path("<int:pk>/", EventRetrieveUpdateDestroyAPIView.as_view(), name="event-detail"),

    path("events/user-related/", UserRelatedEventListAPIView.as_view(), name="user-related-events"),

    path('public/', PublicEventViewSet.as_view(), name='public-events'),
    path('private/', PrivateEventViewSet.as_view(), name='private-events'),
    path('<uuid:event_id>/', EventDetailView.as_view(), name='event-detail'),
    # CSV 업로드 및 업데이트
    path("upload/", EventUploadView.as_view(), name="event-upload"),
]
