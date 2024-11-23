
from django.urls import path
from . import views

urlpatterns = [
    path('create_alarm/<int:user_id>/<str:message>/', views.create_alarm, name='create_alarm'),
]

