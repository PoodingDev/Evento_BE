import os

import requests
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from dotenv import load_dotenv
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import UserSerializer, UserUpdateSerializer

load_dotenv()

from .models import User
from .serializers import UserSerializer, UserUpdateSerializer

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


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["사용자"])
    def get_object(self):
        if not self.request.user.is_authenticated:
            return Response(
                {
                    "error": "인증 실패",
                    "message": "로그인이 필요합니다. 다시 로그인해주세요.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            user = self.request.user
            if not user:
                return Response(
                    {
                        "error": "사용자 정보 없음",
                        "message": "현재 로그인된 사용자의 정보를 찾을 수 없습니다.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            return user
        except User.DoesNotExist:
            return Response(
                {
                    "error": "사용자 정보 없음",
                    "message": "현재 로그인된 사용자의 정보를 찾을 수 없습니다.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    @extend_schema(tags=["사용자"])
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        if isinstance(user, Response):
            return user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @extend_schema(tags=["사용자"])
    def put(self, request, *args, **kwargs):
        user = self.get_object()
        if isinstance(user, Response):  # 에러인 경우
            return user

        # 닉네임 중복 체크
        new_nickname = request.data.get("nickname")
        if (
            new_nickname
            and User.objects.filter(nickname=new_nickname)
            .exclude(user_id=user.user_id)
            .exists()
        ):
            return Response(
                {
                    "error": "닉네임 중복",
                    "message": "이미 사용 중인 닉네임입니다. 다른 닉네임을 선택해주세요.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["사용자"])
    def get_object(self):
        return self.request.user

    @extend_schema(tags=["사용자"])
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(status=204)


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
        try:
            code = request.data.get("code")
            if not code:
                return Response(
                    {"error": "인가 코드가 제공되지 않았습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token_url = "https://oauth2.googleapis.com/token"
            data = {
                "code": code,
                "client_id": os.getenv("CLIENT_ID"),
                "client_secret": os.getenv("CLIENT_SECRET"),
                "redirect_uri": os.getenv("REDIRECT_URI"),
                "grant_type": "authorization_code",
            }

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            }

            response = requests.post(token_url, data=data, headers=headers)
            print("Google Response:", response.status_code, response.json())
            if response.status_code != 200:
                return Response(
                    {"error": "토큰 가져오기 실패", "details": response.text},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            token_data = response.json()
            access_token = token_data.get("access_token")
            if not access_token:
                return Response(
                    {"error": "액세스 토큰을 찾을 수 없습니다."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            userinfo_headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            }
            userinfo_response = requests.get(userinfo_url, headers=userinfo_headers)

            if userinfo_response.status_code != 200:
                return Response(
                    {
                        "error": "유저정보 가져오기 실패",
                        "details": userinfo_response.text,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            user_info = userinfo_response.json()
            email = user_info.get("email")
            if not email:
                return Response(
                    {"error": "이메일 정보를 찾을 수 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                user = User.objects.get(email=email)
                if not user.is_active:
                    new_user = User.objects.create_user(
                        email=email,
                        username=user_info.get("name", ""),
                        birth=timezone.now().date(),
                        nickname=user_info.get("given_name", ""),
                    )
                    new_user.set_unusable_password()
                    new_user.save()
                    refresh = RefreshToken.for_user(new_user)
                    return Response(
                        {
                            "access": str(refresh.access_token),
                            "refresh": str(refresh),
                            "user": {
                                "email": new_user.email,
                                "username": new_user.username,
                                "nickname": new_user.nickname,
                            },
                        },
                        status=status.HTTP_200_OK,
                    )

                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "user": {
                            "email": user.email,
                            "username": user.username,
                            "nickname": user.nickname,
                        },
                    },
                    status=status.HTTP_200_OK,
                )

            except User.DoesNotExist:
                user = User.objects.create_user(
                    email=email,
                    username=user_info.get("name", ""),
                    birth=timezone.now().date(),
                    nickname=user_info.get("given_name", ""),
                )
                user.set_unusable_password()
                user.save()
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "user": {
                            "email": user.email,
                            "username": user.username,
                            "nickname": user.nickname,
                        },
                    },
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NaverLoginView(APIView):
    @extend_schema(tags=["사용자"])
    def post(self, request):
        try:
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
                "code": code,
                "state": state,
            }

            token_response = requests.post(token_url, data=data)
            if token_response.status_code != 200:
                return Response(
                    {"error": "토큰 가져오기 실패", "details": token_response.text},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            access_token = token_response.json().get("access_token")
            user_info_url = "https://openapi.naver.com/v1/nid/me"
            headers = {"Authorization": f"Bearer {access_token}"}
            user_info_response = requests.get(user_info_url, headers=headers)

            if user_info_response.status_code != 200:
                return Response(
                    {
                        "error": "유저정보 가져오기 실패",
                        "details": user_info_response.text,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            user_info = user_info_response.json().get("response", {})
            email = user_info.get("email")
            if not email:
                return Response(
                    {"error": "이메일 정보를 찾을 수 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user, created = User.objects.get_or_create(email=email)
            if created or not user.is_active:
                user.username = user_info.get("name", "")
                user.birth = timezone.now().date()
                user.nickname = user_info.get("nickname", "")
                user.set_unusable_password()
                user.is_active = True
                user.save()

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "email": user.email,
                        "username": user.username,
                        "nickname": user.nickname,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class KakaoLoginView(APIView):
    @extend_schema(tags=["사용자"])
    def post(self, request):
        try:
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
                "redirect_uri": os.getenv("KAKAO_REDIRECT_URI"),
                "code": code,
            }

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            }

            token_response = requests.post(token_url, data=data, headers=headers)
            if token_response.status_code != 200:
                return Response(
                    {"error": "토큰 가져오기 실패", "details": token_response.text},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            token_data = token_response.json()
            access_token = token_data.get("access_token")
            if not access_token:
                return Response(
                    {"error": "액세스 토큰을 찾을 수 없습니다."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            user_info_url = "https://kapi.kakao.com/v2/user/me"
            user_headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            }

            user_info_response = requests.get(user_info_url, headers=user_headers)
            if user_info_response.status_code != 200:
                return Response(
                    {
                        "error": "유저정보 가져오기 실패",
                        "details": user_info_response.text,
                    },
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
                    new_user = User.objects.create_user(
                        email=email,
                        username=user_info.get("properties", {}).get("nickname", ""),
                        birth=timezone.now().date(),
                        nickname=user_info.get("properties", {}).get("nickname", ""),
                    )
                    new_user.set_unusable_password()
                    new_user.save()
                    refresh = RefreshToken.for_user(new_user)
                    return Response(
                        {
                            "access": str(refresh.access_token),
                            "refresh": str(refresh),
                            "user": {
                                "email": new_user.email,
                                "username": new_user.username,
                                "nickname": new_user.nickname,
                            },
                        },
                        status=status.HTTP_200_OK,
                    )

                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "user": {
                            "email": user.email,
                            "username": user.username,
                            "nickname": user.nickname,
                        },
                    },
                    status=status.HTTP_200_OK,
                )

            except User.DoesNotExist:
                user = User.objects.create_user(
                    email=email,
                    username=user_info.get("properties", {}).get("nickname", ""),
                    birth=timezone.now().date(),
                    nickname=user_info.get("properties", {}).get("nickname", ""),
                )
                user.set_unusable_password()
                user.save()
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "user": {
                            "email": user.email,
                            "username": user.username,
                            "nickname": user.nickname,
                        },
                    },
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
