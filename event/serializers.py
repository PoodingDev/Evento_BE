from django.db.models import Q
from rest_framework import serializers

from favorite_event.models import FavoriteEvent

from .models import Event


class EventSerializer(serializers.ModelSerializer):
    """
    Event 모델에 대한 기본 Serializer
    """

    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "event_id",
            "calendar_id",
            "title",
            "description",
            "start_time",
            "end_time",
            "admin_id",
            "is_public",
            "location",
            "is_liked",
            "is_active"
        ]
        read_only_fields = ["event_id", "admin_id"]

    def get_is_liked(self, obj):
        """
        현재 사용자가 이벤트를 좋아요 했는지 여부를 검증하고 반환
        True: FavoriteEvent에 해당 이벤트가 존재하는 경우
        False: FavoriteEvent에 해당 이벤트가 존재하지 않는 경우
        """
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        try:
            # FavoriteEvent 존재 여부 확인 (user_id 사용)
            favorite = FavoriteEvent.objects.filter(
                Q(user_id=request.user.user_id) & Q(event_id=obj.event_id)
            ).first()

            # 디버깅용 로그
            print(f"User ID: {request.user.user_id}")
            print(f"Event ID: {obj.event_id}")
            print(f"Favorite exists: {favorite is not None}")

            return favorite is not None

        except Exception as e:
            # 디버깅용 로그
            print(f"Error in get_is_liked: {str(e)}")
            return False

    def create(self, validated_data):
        validated_data["admin_id"] = self.context["request"].user
        return super().create(validated_data)


class PublicEventSerializer(serializers.ModelSerializer):
    """
    공개 이벤트용 Serializer
    """

    class Meta:
        model = Event
        fields = [
            "event_id",
            "calendar_id",
            "title",
            "description",
            "start_time",
            "end_time",
            "admin_id",
            "is_public",
            "location",
        ]
        read_only_fields = ["event_id", "admin_id"]

    def create(self, validated_data):
        validated_data["is_public"] = True  # 공개 이벤트로 설정
        validated_data["admin_id"] = self.context["request"].user
        return super().create(validated_data)


class PrivateEventSerializer(serializers.ModelSerializer):
    """
    비공개 이벤트용 Serializer
    """

    class Meta:
        model = Event
        fields = [
            "event_id",
            "calendar_id",
            "title",
            "description",
            "start_time",
            "end_time",
            "admin_id",
            "is_public",
            "location",
        ]
        read_only_fields = ["event_id", "admin_id", "is_public"]

    def create(self, validated_data):
        validated_data["is_public"] = False  # 비공개 이벤트로 설정
        validated_data["admin_id"] = self.context["request"].user
        return super().create(validated_data)
