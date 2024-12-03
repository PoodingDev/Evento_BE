from django.urls import path

from .views import (
    CalendarListCreateAPIView,
    CalendarRetrieveUpdateDestroyAPIView,
    SubscriptionDeleteAPIView,
    SubscriptionListCreateAPIView,
)

urlpatterns = [
    # 캘린더 관련 엔드포인트
    path(
        "calendars/", CalendarListCreateAPIView.as_view(), name="calendar-list-create"
    ),
    path(
        "calendars/<int:pk>/",
        CalendarRetrieveUpdateDestroyAPIView.as_view(),
        name="calendar-detail",
    ),
    # 구독 관련 엔드포인트
    path(
        "subscriptions/",
        SubscriptionListCreateAPIView.as_view(),
        name="subscription-list-create",
    ),
    path(
        "subscriptions/<int:pk>/",
        SubscriptionDeleteAPIView.as_view(),
        name="subscription-delete",
    ),
    path("calendars/search/", CalendarSearchAPIView.as_view(), name="calendar-search"),
    path("calendars/admin/", AdminCalendarsAPIView.as_view(), name="admin-calendars"),
    path(
        "calendars/<int:pk>/members/",
        CalendarMembersAPIView.as_view(),
        name="calendar-members",
    ),
]
