from rest_framework import serializers

from .models import Event


class EventSerializer(serializers.ModelSerializer):
    """
    Event 모델 직렬화
    """

    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["event_id"]  # Primary key는 읽기 전용
