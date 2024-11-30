from django.urls import path

from favorite_event import views

app_name = "favorites"  # 네임스페이스 설정 (선택 사항)

urlpatterns = [
    path("favorites/", views.FavoriteEventList.as_view(), name="favorite-list"),
    path(
        "favorites/<int:event_id>/",
        views.FavoriteEventDelete.as_view(),
        name="favorite-delete",
    ),
]
