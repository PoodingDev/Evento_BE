from django.shortcuts import get_object_or_404
from favorite_event.models import FavoriteEvent
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from event.models import Event # 이벤트 모델을 가져옵니다.
from favorite_event.serializers import FavoriteEventSerializer


# 즐겨찾기 이벤트 목록 조회 및 추가 (GET, POST)
class FavoriteEventList(generics.ListCreateAPIView):
    queryset = FavoriteEvent.objects.all()  # 모든 즐겨찾기 이벤트 조회
    serializer_class = FavoriteEventSerializer  # 직렬화할 때 사용할 시리얼라이저


# 즐겨찾기 이벤트 상세 조회, 수정 및 삭제 (GET, PUT, DELETE)
class FavoriteEventDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = (
        FavoriteEvent.objects.all()
    )  # 특정 즐겨찾기 이벤트를 가져오기 위한 쿼리셋
    serializer_class = (
        FavoriteEventSerializer  # 데이터를 직렬화할 때 사용할 시리얼라이저
    )


# 특정 이벤트를 즐겨찾기에 추가하는 기능 (POST)
class FavoriteEventAdd(APIView):
    permission_classes = [IsAuthenticated]  # 로그인한 사용자만 접근 가능

    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)  # 이벤트 가져오기

        # 이미 즐겨찾기 추가된 이벤트인지 확인
        if FavoriteEvent.objects.filter(user=request.user, event=event).exists():
            return Response(
                {"detail": "이미 즐겨찾기한 이벤트입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 즐겨찾기 이벤트 추가
        FavoriteEvent.objects.create(user=request.user, event=event)

        return Response(
            {"detail": "즐겨찾기 이벤트가 추가되었습니다."},
            status=status.HTTP_201_CREATED,
        )


class FavoriteEventAdd(APIView):
    def post(self, request, event_id):
        # 이벤트 즐겨찾기 추가 로직
        return Response(
            {"message": "Favorite event added"}, status=status.HTTP_201_CREATED
        )
