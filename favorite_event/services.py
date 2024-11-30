from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response

from event.models import Event
from favorite_event.models import FavoriteEvent
from user.models import User


class IsSuperUserOrStaffOrOwner(permissions.BasePermission):
    # 슈퍼유저, 스태프, 또는 본인인 경우에만 접근 허용
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        user_id = view.kwargs.get("user_id")

        if request.user.is_superuser or request.user.is_staff:
            return True

        return str(request.user.user_id) == str(user_id)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        return obj.user_id.user_id == request.user.user_id


class FavoriteEventService:
    @staticmethod
    def get_user_favorites(user_id):
        # 즐겨찾기 목록 조회
        try:
            user = User.objects.get(user_id=user_id)
            favorites = FavoriteEvent.objects.filter(user_id=user).select_related(
                "event_id"
            )
            return favorites, None
        except User.DoesNotExist:
            return None, {
                "error": "사용자 없음",
                "message": "해당 사용자를 찾을 수 없습니다.",
            }

    @staticmethod
    def create_favorite(user_id, event_id):
        # 즐겨찾기 추가
        try:
            user = User.objects.get(user_id=user_id)

            if not event_id:
                return None, {
                    "error": "잘못된 요청",
                    "message": "이벤트 ID가 필요합니다.",
                }

            try:
                event = Event.objects.get(event_id=event_id)
            except Event.DoesNotExist:
                return None, {
                    "error": "잘못된 요청",
                    "message": "이벤트 ID가 유효하지 않습니다.",
                }

            if FavoriteEvent.objects.filter(user_id=user, event_id=event).exists():
                return None, {
                    "error": "중복 등록",
                    "message": "이미 즐겨찾기한 이벤트입니다.",
                }

            favorite = FavoriteEvent.objects.create(user_id=user, event_id=event)
            return favorite, None

        except User.DoesNotExist:
            return None, {
                "error": "사용자 없음",
                "message": "해당 사용자를 찾을 수 없습니다.",
            }

    @staticmethod
    def delete_favorite(user_id, event_id):
        # 즐겨찾기 취소
        try:
            user = User.objects.get(user_id=user_id)

            if not event_id:
                return None, {
                    "error": "잘못된 요청",
                    "message": "이벤트 ID가 필요합니다.",
                }

            try:
                favorite = FavoriteEvent.objects.get(user_id=user, event_id=event_id)
                favorite.delete()
                return True, None
            except FavoriteEvent.DoesNotExist:
                return None, {
                    "error": "삭제 실패",
                    "message": "해당 즐겨찾기를 찾을 수 없습니다.",
                }

        except User.DoesNotExist:
            return None, {
                "error": "사용자 없음",
                "message": "해당 사용자를 찾을 수 없습니다.",
            }
