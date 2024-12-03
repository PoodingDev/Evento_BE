import os
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.utils import timezone
from dotenv import load_dotenv
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
import requests
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
        return self.request.user

    @extend_schema(tags=["사용자"])
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @extend_schema(tags=["사용자"])
    def put(self, request, *args, **kwargs):
        user = self.get_object()
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

class SocialLoginView(APIView):
    @extend_schema(tags=["사용자"])
    def post(self, request):
        code = request.data.get("code")
        state = request.data.get("state")
        if not code:
            return JsonResponse(
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
            "state": state,
        }

        response = requests.post(token_url, data=data)
        if response.status_code != 200:
            return Response(
                {"error": "토큰 가져오기 실패"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        access_token = response.json().get("access_token")
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        userinfo_response = requests.get(userinfo_url, headers=headers)

        if userinfo_response.status_code != 200:
            return Response(
                {"error": "유저정보 가져오기 실패"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        user_info = userinfo_response.json()
        email = user_info.get("email")

        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                return JsonResponse(
                    {"error": "이 계정으로는 로그인할 수 없습니다."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except ObjectDoesNotExist:
            user = User.objects.create_user(
                email=email,
                username=user_info.get("name", ""),
                birth=timezone.now().date(),
                nickname=user_info.get("given_name", ""),
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
