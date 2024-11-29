from rest_framework import serializers

from calendars.models import Event

from favorites.models import FavoriteEvent


class FavoriteEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteEvent
        fields = ["id", "user", "event", "created_at"]


from rest_framework import serializers

from favorites.models import FavoriteEvent


class FavoriteEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteEvent
        fields = "__all__"  # 모든 필드를 직렬화


class FavoriteEventSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())


from rest_framework import serializers

from favorites.models import FavoriteEvent


class FavoriteEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteEvent
        fields = ["id", "user", "event"]
