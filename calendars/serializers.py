from rest_framework import serializers

from .models import Calendar, Subscription



class CalendarCreateSerializer(serializers.ModelSerializer):
    """
    캘린더 생성용 Serializer (초대 코드 포함)
    """
    class Meta:
        model = Calendar
        fields = [
            # "calendar_id",
            "name",
            "description",
            "is_public",
            "color",
            "created_at",
            "invitation_code",  # 초대 코드 포함
            "creator",
            "admins",
        ]
        # exclude = ['calendar_id']  # 생성 시 캘린더 ID 제외

    def to_representation(self, instance):
        """
        사용자 권한에 따라 invitation_code를 동적으로 제외
        """
        representation = super().to_representation(instance)
        request = self.context.get("request")

        # 관리자 권한이 없는 경우 초대 코드 제거
        if request and not instance.has_admin_permission(request.user):
            representation.pop("invitation_code", None)

        return representation

class CalendarSearchResultSerializer(serializers.ModelSerializer):
    creator_nickname = serializers.CharField(source="creator.nickname", read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Calendar
        fields = ["name", "creator_nickname", "is_subscribed"]

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        return Subscription.objects.filter(user=user, calendar=obj).exists()


class CalendarDetailSerializer(serializers.ModelSerializer):
    """
    캘린더 조회용 Serializer (초대 코드 제외)
    """
    class Meta:
        model = Calendar
        fields = [
            "calendar_id",
            "name",
            "description",
            "is_public",
            "color",
            "created_at",
            "creator",
            "admins",
        ]
        # 초대 코드는 포함하지 않음


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    구독 데이터를 직렬화하는 Serializer
    """

    # 읽기 전용 캘린더 정보
    calendar = CalendarDetailSerializer(read_only=True)

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
    calendar = CalendarCreateSerializer(read_only=True)

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

class AdminCalendarSerializer(serializers.ModelSerializer):
    creator_id = serializers.IntegerField(source="creator.id", read_only=True)
    admin_members = serializers.SerializerMethodField()

    class Meta:
        model = Calendar
        fields = ["name", "creator_id", "admin_members"]

    def get_admin_members(self, obj):
        return list(obj.admins.values_list("nickname", flat=True))

class CalendarSearchSerializer(serializers.ModelSerializer):
    creator_nickname = serializers.CharField(source='creator.nickname', read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Calendar
        fields = ['calendar_id', 'name', 'creator_nickname', 'is_subscribed']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                calendar=obj
            ).exists()
        return False
