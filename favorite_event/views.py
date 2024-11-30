from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from favorite_event.serializers import (
    FavoriteCreateSerializer,
    FavoriteDeleteSerializer,
    FavoriteEventListSerializer,
    FavoriteEventResponseSerializer,
    FavoriteEventSerializer,
)
from favorite_event.services import FavoriteEventService, IsSuperUserOrStaffOrOwner


class FavoriteEventList(APIView):
    # 즐겨찾기 목록 조회 View
    permission_classes = [IsSuperUserOrStaffOrOwner]

    @extend_schema(tags=["즐겨찾기"], responses={200: FavoriteEventResponseSerializer})
    def get(self, request, user_id):
        # 즐겨찾기 목록 조회
        favorites, error = FavoriteEventService.get_user_favorites(user_id)
        if error:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        serializer = FavoriteEventListSerializer(favorites, many=True)
        return Response({"favorite_events": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["즐겨찾기"],
        request=FavoriteCreateSerializer,
        responses={201: FavoriteEventSerializer},
    )
    def post(self, request, user_id):
        # 즐겨찾기 추가
        favorite, error = FavoriteEventService.create_favorite(
            user_id, request.data.get("event_id")
        )
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        serializer = FavoriteEventSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FavoriteEventDelete(APIView):
    # 즐겨찾기 취소 View
    permission_classes = [IsSuperUserOrStaffOrOwner]

    @extend_schema(
        tags=["즐겨찾기"], request=FavoriteDeleteSerializer, responses={204: None}
    )
    def delete(self, request, user_id, event_id):
        # 즐겨찾기 취소
        success, error = FavoriteEventService.delete_favorite(user_id, event_id)
        if error:
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
