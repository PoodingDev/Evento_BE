from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserCreateView,
    UserDeleteView,
    UserDetailView,
    NaverLoginView,
    KakaoLoginView,
    SocialLoginView,
    LoginView,
)

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="user-register"),
    path("me/", UserDetailView.as_view(), name="user-me"),
    path("delete/", UserDeleteView.as_view(), name="user-delete"),
    #구글 소셜 로그인
    path("social-login/", SocialLoginView.as_view(), name="social_login"),
    path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    #네이버 소셜 로그인
    path("naver/login/", NaverLoginView.as_view(), name="naver_login"),
    #카카오 소셜 로그인
    path("kakao/login/", KakaoLoginView.as_view(), name="kakaologin"),
]
