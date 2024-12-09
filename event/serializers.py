from rest_framework import serializers

from .models import Event


class EventSerializer(serializers.ModelSerializer):
    """
    Event 모델에 대한 기본 Serializer
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
