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

        # @extend_schema_field({'type': 'string', 'enum': ['public', 'private']})
        # def get_event_type(self, obj):
        #     return 'public' if obj.is_public else 'private'
        #
        read_only_fields = ["event_id", "admin_id"]  # ID 및 admin_id는 읽기 전용
        # extra_kwargs = {
        #     'is_public': {
        #         'default': False,
        #         'required':False,
        #     }
        # }

    def validate(self, data):
        """
        이벤트 유효성 검사:
        - 시작 시간(start_time)은 종료 시간(end_time)보다 빨라야 합니다.
        - 이벤트는 같은 시간대에 겹치면 안 됩니다.
        """
        """
            is_public 값을 강제로 False로 설정
        """
        data["is_public"] = False

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
        event_type = validated_data.pop('event_type')
        validated_data['is_public'] = (event_type == 'public')
        # is_public 값을 강제로 False로 설정
        # validated_data["is_public"] = False
        # is_public이 명시적으로 설정되지 않은 경우 False로 설정
        # if 'is_public' not in validated_data:
        #     validated_data['is_public'] = False
        validated_data["admin_id"] = request_user
        return super().create(validated_data)

    def validate_is_public(self, value):
        # 클라이언트가 is_public을 True로 요청한 경우 에러 처리
        if value is True:
            raise serializers.ValidationError("비공개 이벤트는 is_public을 True로 설정할 수 없습니다.")
        return value

    def update(self, instance, validated_data):
        """
        Event 업데이트:
        - 특정 필드는 업데이트하지 못하도록 제한 가능.
        """
        if "admin_id" in validated_data:
            raise serializers.ValidationError({"admin_id": "관리자를 변경할 수 없습니다."})
        return super().update(instance, validated_data)

class PublicEventSerializer(EventSerializer):
    def create(self, validated_data):
        validated_data['is_public'] = True
        return super().create(validated_data)

class PrivateEventSerializer(serializers.ModelSerializer):
    """
    비공개 이벤트 전용 Serializer
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

    def validate(self, data):
        """
        비공개 이벤트 요청에서 is_public 값 처리
        """
        if data.get("is_public", True):  # is_public이 True로 설정된 경우
            raise serializers.ValidationError(
                {"is_public": "비공개 이벤트는 is_public을 True로 설정할 수 없습니다."}
            )
        data["is_public"] = False  # 강제로 False 설정
        return data

    def create(self, validated_data):
        """
        비공개 이벤트 생성 시 요청 사용자를 admin_id로 설정
        """
        validated_data["admin_id"] = self.context["request"].user
        validated_data["is_public"] = False  # 강제로 False 설정
        return super().create(validated_data)

class EventUploadSerializer(serializers.Serializer):
    file = serializers.FileField(
        help_text="이벤트 데이터 파일 (.csv, .xlsx)",
        required=True
    )