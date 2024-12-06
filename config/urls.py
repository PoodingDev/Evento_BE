from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin URL
    path("admin/", admin.site.urls),
    # Swagger 및 Schema 관련
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # User 관련
    path("api/users/", include("user.urls")),
    # 캘린더 관련
    path('api/calendars/', include('calendars.urls')),  # 캘린더 앱 URL 등록
    # 이벤트 관련
    path("api/events/", include("event.urls")),
    # 댓글 관련 (특정 이벤트에 종속)
    path("api/events/<int:event_id>/comments/", include("comment.urls")),
    # 유저별 즐겨찾기 관련
    path("api/users/<str:user_id>/", include("favorite_event.urls")),
]
