import os
from dotenv import load_dotenv
from django.utils import timezone
import requests
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from mypy.state import state

load_dotenv()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class SocialLoginView(APIView):
    def post(self, request):
        code = request.data.get('code')
        state = request.data.get('state')
        if not code:
            return JsonResponse({"error": "인가 코드가 제공되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

        token_url = "https://oauth2.googleapis.com/token"

        data = {
            "code": code,
            "client_id": os.getenv('CLIENT_ID'),
            "client_secret": os.getenv('CLIENT_SECRET'),
            "redirect_uri": os.getenv('REDIRECT_URI'),
            "grant_type": "authorization_code",
            "state": state
        }

        response = requests.post(token_url, data=data)
        # 사용자 정보 가져오기

        if not response.status_code == 200:
            print(f"토큰 가져오기 실패")
            print(response.status_code)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        access_token = response.json().get("access_token")

        # Access Token을 사용하여 Google 사용자 정보 가져오기
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        userinfo_response = requests.get(userinfo_url, headers=headers)

        if not userinfo_response.status_code == 200:
            print(f"유저정보 가져오기 실패")
            print(response.status_code)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user_info = userinfo_response.json()

        email = user_info.get('email')

        try:
            user = User.objects.get(user_email=email)
            if user.is_active:
                tokens = get_tokens_for_user(user)
                return JsonResponse({
                    "access_token": tokens['access'],
                    "refresh_token": tokens['refresh']
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"error": "이 계정으로는 로그인할 수 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            # 새 사용자 생성
            user = User.objects.create_user(
                user_login_id=email,
                user_email=email,
                user_name=user_info.get('name', ''),
                user_birth=timezone.now(),
                user_nickname=user_info.get('given_name', ''),
            )
            user.set_unusable_password()
            user.save()
            tokens = get_tokens_for_user(user)
            return JsonResponse({
                "access_token": tokens['access'],
                "refresh_token": tokens['refresh']
            }, status=status.HTTP_200_OK)
