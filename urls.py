from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('favorites.urls')),  # favorites 앱의 URL을 포함
]
