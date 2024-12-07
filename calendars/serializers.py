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
        queryset=Calendar.objects.all(),
        source="calendar",
        write_only=True,
    )

    class Meta:
        model = Subscription
        fields = ["id", "user", "calendar", "calendar_id", "created_at"]
        read_only_fields = ["user", "created_at"]  # 사용자는 서버에서 설정

    def create(self, validated_data):
        """
        구독 생성 시 현재 요청 사용자를 user로 설정
        """
        user = self.context["request"].user  # 요청 사용자 가져오기
        subscription = Subscription.objects.create(user=user, **validated_data)
        return subscription

    def update(self, instance, validated_data):
        """
        구독 데이터 업데이트 (is_active, is_on_calendar 상태 변경)
        """
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.is_on_calendar = validated_data.get("is_on_calendar", instance.is_on_calendar)
        instance.save()
        return instance

class AdminInvitationSerializer(serializers.Serializer):
    """
    관리자 초대 코드 처리 Serializer
    """

    invitation_code = serializers.CharField(max_length=255, help_text="초대 코드", write_only=True)
    calendar = CalendarSerializer(read_only=True)

    def validate_invitation_code(self, value):
        """
        초대 코드를 검증하여 캘린더를 확인
        """
        try:
            calendar = Calendar.objects.get(invitation_code=value)
        except Calendar.DoesNotExist:
            raise serializers.ValidationError("유효하지 않은 초대 코드입니다.")
        if self.context["request"].user in calendar.admins.all():
            raise serializers.ValidationError("이미 캘린더 관리자로 추가되었습니다.")
        self.calendar = calendar
        return value

    def save(self):
        """
        초대 코드를 사용해 사용자를 캘린더 관리자에 추가
        """
        user = self.context["request"].user  # 요청 사용자
        if not hasattr(self, "calendar"):
            raise serializers.ValidationError("초대 코드가 유효하지 않습니다.")
        self.calendar.admins.add(user)  # 관리자로 추가
        return self.calendar
