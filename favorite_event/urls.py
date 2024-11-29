from django.urls import path
from favorite_event import views

app_name = "favorites"  # 네임스페이스 설정 (선택 사항)

urlpatterns = [
    path("favorite-events/", views.FavoriteEventList.as_view(), name="favorite-events-list"),
    path("favorite-events/<int:pk>/", views.FavoriteEventDetail.as_view(), name="favorite-events-detail"),
    path("favorite-events/add/<int:event_id>/", views.FavoriteEventAdd.as_view(), name="favorite-event-add"),
]
