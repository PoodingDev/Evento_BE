from rest_framework import serializers

from comment.models import Comment
from user.models import User


class CommentSerializer(serializers.ModelSerializer):
    admin_nickname = serializers.CharField(source="admin_id.nickname", read_only=True)

    class Meta:
        model = Comment
        fields = [
            "comment_id",
            "content",
            "created_at",
            "updated_at",
            "event_id",
            "admin_id",
            "admin_nickname",
        ]


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content"]
