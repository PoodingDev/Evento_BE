from django.urls import path

from .views import (
    EventRetrieveUpdateDestroyAPIView,
    EventUploadView,
    PrivateEventCreateAPIView,
    PrivateEventListAPIView,
    PublicEventCreateAPIView,
    PublicEventListAPIView,
    ActiveCalendarEventListAPIView
)

urlpatterns = [
    # 공개 이벤트 목록 조회
    path("public/list/", PublicEventListAPIView.as_view(), name="public-event-list"),
    # 공개 이벤트 생성
    path(
        "public/create/",
        PublicEventCreateAPIView.as_view(),
        name="public-event-create",
    ),
    # 비공개 이벤트 목록 조회
    path("private/list/", PrivateEventListAPIView.as_view(), name="private-event-list"),
    # 비공개 이벤트 생성
    path(
        "private/create/",
        PrivateEventCreateAPIView.as_view(),
        name="private-event-create",
    ),
    # 이벤트 상세 조회, 수정, 삭제 (UUID 형식의 event_id 사용)
    path(
        "<uuid:event_id>/",
        EventRetrieveUpdateDestroyAPIView.as_view(),
        name="event-detail",
    ),

    path("active/", ActiveCalendarEventListAPIView.as_view(), name="active-event-list"),
    # CSV 업로드 및 업데이트
    path("upload/", EventUploadView.as_view(), name="event-upload"),
]
