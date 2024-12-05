from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/users/", include("user.urls")),
    path('api/calendars/', include('calendars.urls')),  # 캘린더 앱 URL 등록
    path("api/events/<int:event_id>/", include("comment.urls")),
    path("api/users/<str:user_id>/", include("favorite_event.urls")),
    path("calendars/", include("calendars.urls")),
    path("events/", include("event.urls")),
]
