from .views import EventListCreateAPIView, EventRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('events/', EventListCreateAPIView.as_view(), name='event-list-create'),
    path('events/<int:pk>/', EventRetrieveUpdateDestroyAPIView.as_view(), name='event-detail'),
]
