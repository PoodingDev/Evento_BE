from django.urls import path

from .views import UserCreateView, UserDeleteView, UserDetailView

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="user-register"),
    path("me/", UserDetailView.as_view(), name="user-me"),
    path("delete/", UserDeleteView.as_view(), name="user-delete"),
]
