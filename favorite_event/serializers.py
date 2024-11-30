from rest_framework import serializers

from favorite_event.models import FavoriteEvent


class FavoriteEventBaseSerializer(serializers.ModelSerializer):
    # 기본 즐겨찾기 시리얼라이저
    class Meta:
        model = FavoriteEvent
        fields = ["event_id"]


class FavoriteEventListSerializer(FavoriteEventBaseSerializer):
    # 즐겨찾기 목록 조회용 시리얼라이저
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


class FavoriteEventResponseSerializer(serializers.Serializer):
    # 즐겨찾기 목록 응답용 시리얼라이저
    favorite_events = FavoriteEventListSerializer(many=True)


class FavoriteEventSerializer(FavoriteEventBaseSerializer):
    # 즐겨찾기 상세 조회 시리얼라이저
    class Meta(FavoriteEventBaseSerializer.Meta):
        fields = [
            "favorite_event_id",
            "user_id",
            "event_id",
            "easy_insidebar",
            "d_day",
        ]


class FavoriteCreateSerializer(FavoriteEventBaseSerializer):
    # 즐겨찾기 생성 요청용 시리얼라이저
    event_id = serializers.IntegerField(required=True, help_text="추가할 이벤트 ID")


class FavoriteDeleteSerializer(serializers.Serializer):
    # 즐겨찾기 삭제 요청용 시리얼라이저
    event_id = serializers.IntegerField(required=True, help_text="삭제할 이벤트 ID")
