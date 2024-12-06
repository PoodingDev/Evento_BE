from django.urls import path
from .views import (
    PublicEventListAPIView,
    PrivateEventListCreateAPIView,
    EventRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path("events/public/", PublicEventListAPIView.as_view(), name="public-event-list"),
    path("events/private/", PrivateEventListCreateAPIView.as_view(), name="private-event-list-create"),
    path("events/<int:pk>/", EventRetrieveUpdateDestroyAPIView.as_view(), name="event-detail"),
]
