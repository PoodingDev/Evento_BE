from django.urls import path
from . import views

urlpatterns = [
    #임시 URL 패턴
    path('', views.home, name='home'),
]
