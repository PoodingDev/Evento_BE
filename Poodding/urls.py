from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/calendars/', include('calendars.urls')),
    path('api/events/', include('event.urls')),
    path('accounts/', include('allauth.urls')),
    path('api/auth/', include('users.urls'))  # 이 줄만 유지
]
