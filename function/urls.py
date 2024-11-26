
from django.urls import path
from . import views

urlpatterns = [
    path('create_alarm/<int:user_id>/<str:message>/', views.create_alarm, name='create_alarm'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello, name='hello'),  # /function/hello/ 경로로 요청이 오면 hello 뷰 실행
]
