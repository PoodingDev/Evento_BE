from django.urls import path
from .views import CalendarListCreateAPIView, CalendarRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('calendars/', CalendarListCreateAPIView.as_view(), name='calendar-list-create'),
    path('calendars/<int:pk>/', CalendarRetrieveUpdateDestroyAPIView.as_view(), name='calendar-detail'),
]
