from rest_framework import serializers

from favorite_event.models import FavoriteEvent


class FavoriteEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteEvent
        fields = [
            "favorite_event_id",
            "user_id",
            "event_id",
            "easy_insidebar",
            "d_day",
        ]


class FavoriteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteEvent
        fields = ["event_id"]
