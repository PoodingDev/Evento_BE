from django.urls import path

from .views import EventListCreateAPIView, EventRetrieveUpdateDestroyAPIView

urlpatterns = [
    path("", EventListCreateAPIView.as_view(), name="event-list-create"),
    path(
        "<int:pk>/",
        EventRetrieveUpdateDestroyAPIView.as_view(),
        name="event-detail",
    ),
]
