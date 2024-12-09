import os
import random
import string

import requests
from django.contrib.auth import logout
from django.http import JsonResponse
from django.utils import timezone
from dotenv import load_dotenv
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import UserSerializer, UserUpdateSerializer


def generate_random_nickname():
    return "".join(random.choices(string.ascii_letters + string.digits, k=8))


load_dotenv()


class LoginView(TokenObtainPairView):
    @extend_schema(tags=["사용자"])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=["사용자"])
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")

        # 비활성화된 계정이 있는지 확인
        try:
            existing_user = User.objects.get(email=email, is_active=False)
            # 기존 비활성 계정이 있다면 삭제
            existing_user.delete()
        except User.DoesNotExist:
            pass

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "user_id": user.user_id,
                    "email": user.email,
                    "username": user.username,
                    "birth": user.birth,
                    "nickname": user.nickname,
                },
                status=201,
            )
        return Response(serializer.errors, status=400)


from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated


class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["사용자"])
    def get_object(self):
        if not self.request.user.is_authenticated:
            raise AuthenticationFailed("인증되지 않은 사용자입니다.")
        return self.request.user

    @extend_schema(tags=["사용자"])
    def delete(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            # 계정 비활성화
            user.is_active = False
            user.save()
            # 로그아웃 처리
            logout(request)
            return Response(
                {"message": "계정이 성공적으로 비활성화되었습니다."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except AuthenticationFailed:
            return Response(
                {"error": "인증에 실패했습니다. 다시 로그인해주세요."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["사용자"])
    def get_object(self):
        if not self.request.user.is_authenticated:
            raise AuthenticationFailed("로그인이 필요합니다. 다시 로그인해주세요.")

        try:
            user = self.request.user
            if not user:
                raise NotFound("현재 로그인된 사용자의 정보를 찾을 수 없습니다.")
            return user
        except User.DoesNotExist:
            raise NotFound("현재 로그인된 사용자의 정보를 찾을 수 없습니다.")

    @extend_schema(tags=["사용자"])
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @extend_schema(tags=["사용자"])
    def put(self, request, *args, **kwargs):
        user = self.get_object()

        # 닉네임 중복 체크
        new_nickname = request.data.get("nickname")
        if (
            new_nickname
            and User.objects.filter(nickname=new_nickname)
            .exclude(user_id=user.user_id)
            .exists()
        ):
            raise ValidationError(
                "이미 사용 중인 닉네임입니다. 다른 닉네임을 선택해주세요."
            )

        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=["사용자"])
    def post(self, request):
        logout(request)
        return Response(
            {"message": "로그아웃이 완료되었습니다."}, status=status.HTTP_200_OK
        )


class GoogleLoginView(APIView):
    @extend_schema(tags=["사용자"])
    def post(self, request):
        code = request.data.get("code")
        state = request.data.get("state")
        if not code:
            return JsonResponse(
                {"error": "인가 코드가 제공되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not state:
            return JsonResponse(
                {"error": "state가 제공되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
            "grant_type": "authorization_code",
            "state": state,
        }

        response = requests.post(token_url, data=data)
        if response.status_code != 200:
            return JsonResponse(
                {"error": "토큰 가져오기 실패"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        access_token = response.json().get("access_token")
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_response = requests.get(userinfo_url, headers=headers)

        if userinfo_response.status_code != 200:
            return JsonResponse(
                {"error": "유저정보 가져오기 실패"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        user_info = userinfo_response.json()
        email = user_info.get("email")

        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                # 기존 계정 정보 저장
                user_id = user.user_id
                # 계정 삭제
                user.delete()

                # 새로운 계정 생성
                new_user = User.objects.create_user(
                    email=email,
                    username=user_info.get("name", ""),
                    birth=timezone.now().date(),
                    nickname=generate_random_nickname(),
                )
                new_user.set_unusable_password()
                new_user.save()
                user = new_user
            # 활성 계정인 경우 기존 사용자 사용
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=email,
                username=user_info.get("name", ""),
                birth=timezone.now().date(),
                nickname=generate_random_nickname(),
            )
            user.set_unusable_password()
            user.save()

        refresh = RefreshToken.for_user(user)
        return JsonResponse(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class NaverLoginView(APIView):
    @extend_schema(tags=["사용자"])
    def post(self, request):
        code = request.data.get("code")
        state = request.data.get("state")
        if not code:
            return Response(
                {"error": "인가 코드가 제공되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not state:
            return Response(
                {"error": "state가 제공되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_url = "https://nid.naver.com/oauth2.0/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": os.getenv("NAVER_CLIENT_ID"),
            "client_secret": os.getenv("NAVER_CLIENT_SECRET"),
            "redirect_uri": os.getenv("NAVER_REDIRECT_URI"),
            "code": code,
            "state": state,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        token_response = requests.post(token_url, data=data, headers=headers)
        if token_response.status_code != 200:
            return Response(
                {"error": "토큰 가져오기 실패"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        access_token = token_response.json().get("access_token")
        if not access_token:
            return Response(
                {"error": "액세스 토큰을 찾을 수 없습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        user_info_url = "https://openapi.naver.com/v1/nid/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_response = requests.get(user_info_url, headers=headers)

        if user_info_response.status_code != 200:
            return Response(
                {"error": "유저정보 가져오기 실패"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        user_info = user_info_response.json().get("response", {})
        email = user_info.get("email")
        if not email:
            return Response(
                {"error": "이메일 정보를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                user.delete()
                user = User.objects.create_user(
                    email=email,
                    username=user_info.get("name", ""),
                    birth=timezone.now().date(),
                    nickname=generate_random_nickname(),
                )
                user.set_unusable_password()
                user.save()
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=email,
                username=user_info.get("name", ""),
                birth=timezone.now().date(),
                nickname=generate_random_nickname(),
            )
            user.set_unusable_password()
            user.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class KakaoLoginView(APIView):
    @extend_schema(tags=["사용자"])
    def post(self, request):
        code = request.data.get("code")
        if not code:
            return Response(
                {"error": "인가 코드가 제공되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": os.getenv("KAKAO_CLIENT_ID"),
            "client_secret": os.getenv("KAKAO_CLIENT_SECRET"),
            "redirect_uri": os.getenv("KAKAO_REDIRECT_URI"),
            "code": code,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            "Accept": "application/json",
        }

        token_response = requests.post(token_url, data=data, headers=headers)
        if token_response.status_code != 200:
            return Response(
                {"error": "토큰 가져오기 실패"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        access_token = token_response.json().get("access_token")
        if not access_token:
            return Response(
                {"error": "액세스 토큰을 찾을 수 없습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_response = requests.get(user_info_url, headers=headers)

        if user_info_response.status_code != 200:
            return Response(
                {"error": "유저정보 가져오기 실패"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        user_info = user_info_response.json()
        email = user_info.get("kakao_account", {}).get("email")
        if not email:
            return Response(
                {"error": "이메일 정보를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                user.delete()
                user = User.objects.create_user(
                    email=email,
                    username=user_info.get("properties", {}).get("nickname", ""),
                    birth=timezone.now().date(),
                    nickname=generate_random_nickname(),
                )
                user.set_unusable_password()
                user.save()
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=email,
                username=user_info.get("properties", {}).get("nickname", ""),
                birth=timezone.now().date(),
                nickname=generate_random_nickname(),
            )
            user.set_unusable_password()
            user.save()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )
