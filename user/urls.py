from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserCreateView,
    UserDeleteView,
    UserDetailView,
    SocialLoginView,
    LoginView,
)

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="user-register"),
    path("me/", UserDetailView.as_view(), name="user-me"),
    path("delete/", UserDeleteView.as_view(), name="user-delete"),
    path("social-login/", SocialLoginView.as_view(), name="social_login"),
    path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
