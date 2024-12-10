from django.utils import timezone
from rest_framework import serializers

from favorite_event.models import FavoriteEvent


class FavoriteEventBaseSerializer(serializers.ModelSerializer):
    """기본 즐겨찾기 시리얼라이저"""

    user_id = serializers.CharField(source="user_id.user_id", read_only=True)

    class Meta:
        model = FavoriteEvent
        fields = ["event_id"]


class FavoriteEventListSerializer(FavoriteEventBaseSerializer):
    """즐겨찾기 목록 조회용 시리얼라이저"""

    event_title = serializers.CharField(source="event_id.title", read_only=True)
    d_day = serializers.DateField(format="%Y-%m-%d")

    class Meta(FavoriteEventBaseSerializer.Meta):
        fields = [
            "favorite_event_id",
            "event_id",
            "event_title",
            "d_day",
            "easy_insidebar",
        ]


class FavoriteEventSerializer(serializers.ModelSerializer):
    """즐겨찾기 상세 조회 시리얼라이저"""

    d_day = serializers.SerializerMethodField()

    class Meta(FavoriteEventBaseSerializer.Meta):
        fields = [
            "favorite_event_id",
            "user_id",
            "event_id",
            "easy_insidebar",
            "d_day",
        ]

    def get_d_day(self, obj):
        """
        현재 날짜와 이벤트 시작 날짜의 차이를 계산하여 D-day 반환
        """
        try:
            today = timezone.localtime().date()
            event_date = obj.event_id.start_time.date()

            diff = (event_date - today).days

            if diff > 0:
                return f"D-{diff}"
            elif diff < 0:
                return f"D+{abs(diff)}"
            else:
                return "D-Day"
        except Exception as e:
            print(f"Error calculating d_day: {str(e)}")
            return None


class FavoriteEventResponseSerializer(serializers.Serializer):
    """즐겨찾기 목록 응답용 시리얼라이저"""

    favorite_events = FavoriteEventListSerializer(many=True)


# 요청 시리얼라이저들은 단순하므로 BaseSerializer 상속 불필요
class FavoriteCreateSerializer(serializers.Serializer):
    """즐겨찾기 생성 요청용 시리얼라이저"""

    event_id = serializers.IntegerField(required=True, help_text="추가할 이벤트 ID")


class FavoriteDeleteSerializer(serializers.Serializer):
    """즐겨찾기 삭제 요청용 시리얼라이저"""

    event_id = serializers.IntegerField(required=True, help_text="삭제할 이벤트 ID")
