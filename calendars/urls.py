from django.urls import path
from . import views

urlpatterns = [
    # 임시 URL
    path('', views.calendar_home, name='calendar_home'),
]
