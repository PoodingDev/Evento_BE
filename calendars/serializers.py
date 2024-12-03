from rest_framework import serializers

from .models import Calendar, Subscription


class CalendarSerializer(serializers.ModelSerializer):
    """
    캘린더 데이터를 직렬화하는 Serializer
    """

    class Meta:
        model = Calendar
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    구독 데이터를 직렬화하는 Serializer
    """

    # 읽기 전용 캘린더 정보
    calendar = CalendarSerializer(read_only=True)

    # 쓰기 전용 캘린더 ID (구독 생성 시 사용)
    calendar_id = serializers.PrimaryKeyRelatedField(
        queryset=Calendar.objects.all(), source="calendar", write_only=True
    )

    class Meta:
        model = Subscription
        fields = ["id", "user", "calendar", "calendar_id", "created_at"]
