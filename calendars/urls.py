from django.urls import path

from .views import (
    CalendarListCreateAPIView,
    CalendarRetrieveUpdateDestroyAPIView,
    SubscriptionDeleteAPIView,
    SubscriptionListCreateAPIView,
    CalendarSearchAPIView,
    AdminCalendarsAPIView,
    CalendarMembersAPIView,
)

urlpatterns = [
    # 캘린더 관련 엔드포인트
    path("calendars/", CalendarListCreateAPIView.as_view(), name="calendar_list_create"),
    path("calendars/<int:pk>/", CalendarRetrieveUpdateDestroyAPIView.as_view(), name="calendar_detail"),
    path("calendars/search/", CalendarSearchAPIView.as_view(), name="calendar_search"),
    path("calendars/<int:pk>/members/", CalendarMembersAPIView.as_view(), name="calendar_members"),

    # 구독 관련 엔드포인트
    path("subscriptions/", SubscriptionListCreateAPIView.as_view(), name="subscription_list_create"),
    path("subscriptions/<int:pk>/", SubscriptionDeleteAPIView.as_view(), name="subscription_delete"),

    # 관리 캘린더 엔드포인트
    path("calendars/admin/", AdminCalendarsAPIView.as_view(), name="admin_calendars"),
]
