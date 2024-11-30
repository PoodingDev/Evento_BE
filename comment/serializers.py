from rest_framework import serializers

from comment.models import Comment
from user.models import User


class CommentBaseSerializer(serializers.ModelSerializer):
    """기본 댓글 시리얼라이저"""

    admin_nickname = serializers.CharField(source="admin_id.nickname", read_only=True)

    class Meta:
        model = Comment
        fields = ["content"]


class CommentSerializer(CommentBaseSerializer):
    """댓글 조회/응답용 시리얼라이저"""

    class Meta(CommentBaseSerializer.Meta):
        fields = [
            "comment_id",
            "content",
            "created_at",
            "updated_at",
            "event_id",
            "admin_id",
            "admin_nickname",
        ]


class CommentCreateSerializer(CommentBaseSerializer):
    """댓글 생성 요청용 시리얼라이저"""

    class Meta(CommentBaseSerializer.Meta):
        fields = ["content"]
