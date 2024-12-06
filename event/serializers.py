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
        read_only_fields = ["event_id", "admin_id"]  # ID 및 admin_id는 읽기 전용

    def validate(self, data):
        """
        이벤트 유효성 검사:
        - 시작 시간(start_time)은 종료 시간(end_time)보다 빨라야 합니다.
        - 이벤트는 같은 시간대에 겹치면 안 됩니다.
        """
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError(
                {"end_time": "종료 시간은 시작 시간 이후여야 합니다."}
            )

        # 캘린더 ID가 동일한 경우 시간 중복 검사
        overlapping_events = Event.objects.filter(
            calendar_id=data["calendar_id"],
            start_time__lt=data["end_time"],
            end_time__gt=data["start_time"],
        ).exclude(event_id=self.instance.event_id if self.instance else None)

        if overlapping_events.exists():
            raise serializers.ValidationError(
                {"start_time": "다른 이벤트와 시간이 겹칩니다."}
            )
        return data

    def create(self, validated_data):
        """
        Event 생성 시 기본 설정:
        - 요청 유저를 admin_id로 설정.
        """
        request_user = self.context["request"].user
        validated_data["admin_id"] = request_user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Event 업데이트:
        - 특정 필드는 업데이트하지 못하도록 제한 가능.
        """
        if "admin_id" in validated_data:
            raise serializers.ValidationError({"admin_id": "관리자를 변경할 수 없습니다."})
        return super().update(instance, validated_data)
