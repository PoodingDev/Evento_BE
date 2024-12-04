from django.urls import path

from .views import (
    AdminCalendarsAPIView,
    CalendarListCreateAPIView,
    CalendarMembersAPIView,
    CalendarRetrieveUpdateDestroyAPIView,
    CalendarSearchAPIView,
    SubscriptionDeleteAPIView,
    SubscriptionListCreateAPIView,
)

urlpatterns = [
    path(
        "calendars/", CalendarListCreateAPIView.as_view(), name="calendar-list-create"
    ),
    path(
        "calendars/<int:pk>/",
        CalendarRetrieveUpdateDestroyAPIView.as_view(),
        name="calendar-detail",
    ),
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
