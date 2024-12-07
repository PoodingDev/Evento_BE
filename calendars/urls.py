from django.urls import path
from .views import (
    AdminInvitationView,
    AdminCalendarsAPIView,
    CalendarListCreateAPIView,
    CalendarMembersAPIView,
    CalendarRetrieveUpdateDestroyAPIView,
    CalendarSearchAPIView,
    SubscriptionDeleteAPIView,
    SubscriptionListCreateAPIView,
    ActiveSubscriptionsAPIView,
    UpdateActiveStatusAPIView
)


urlpatterns = [
    # 캘린더 목록 조회 및 생성
    path("", CalendarListCreateAPIView.as_view(), name="calendar-list-create"),

    # 캘린더 상세 조회, 수정, 삭제
    path("<int:pk>/", CalendarRetrieveUpdateDestroyAPIView.as_view(), name="calendar-detail"),

    # 캘린더 구독 및 취소
    path("<int:calendar_id>/subscriptions/", SubscriptionListCreateAPIView.as_view(), name="subscription-list-create"),
    path("<int:calendar_id>/unsubscriptions/", SubscriptionDeleteAPIView.as_view(), name="subscription-delete"),

    # 캘린더 검색
    path("search/", CalendarSearchAPIView.as_view(), name="calendar-search"),

    # 관리 권한이 있는 캘린더 조회
    path("admin/", AdminCalendarsAPIView.as_view(), name="admin-calendars"),

    # 캘린더 멤버 조회
    path("<int:pk>/members/", CalendarMembersAPIView.as_view(), name="calendar-members"),

    # 관리자 초대
    path("admins/invite/", AdminInvitationView.as_view(), name="admin-invitation"),

    path("subscriptions/active/", ActiveSubscriptionsAPIView.as_view(), name="active-subscriptions"),
    path("subscriptions/update-status/", UpdateActiveStatusAPIView.as_view(), name="update-active-status"),
]
