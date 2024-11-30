from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response

from comment.models import Comment
from comment.serializers import CommentCreateSerializer, CommentSerializer
from event.models import Event


class CommentException(Exception):
    """기본 댓글 예외 클래스"""

    def __init__(self, error, message):
        self.error = error
        self.message = message


class EventNotFoundException(CommentException):
    def __init__(self):
        super().__init__("이벤트 없음", "해당 이벤트를 찾을 수 없습니다.")


class CommentNotFoundException(CommentException):
    def __init__(self):
        super().__init__("댓글 없음", "해당 댓글을 찾을 수 없습니다.")


class CommentPermissionDeniedException(CommentException):
    def __init__(self):
        super().__init__("권한 없음", "이 이벤트에 댓글을 작성할 권한이 없습니다.")


class CommentService:
    @staticmethod
    def check_comment_permission(user):
        if not user.is_authenticated or not (user.is_superuser or user.is_staff):
            raise CommentPermissionDeniedException()

    @staticmethod
    def get_event(event_id):
        try:
            return Event.objects.get(event_id=event_id)
        except ObjectDoesNotExist:
            raise EventNotFoundException()

    @staticmethod
    def get_comment(comment_id):
        try:
            return Comment.objects.get(comment_id=comment_id)
        except ObjectDoesNotExist:
            raise CommentNotFoundException()

    @classmethod
    def get_comments(cls, request, event):
        try:
            cls.check_comment_permission(request.user)
            comments = Comment.objects.filter(event_id=event)
            return comments, None
        except CommentPermissionDeniedException as e:
            return None, {"error": e.error, "message": e.message}

    @classmethod
    def create_comment(cls, request, event):
        try:
            cls.check_comment_permission(request.user)
            serializer = CommentCreateSerializer(data=request.data)
            if serializer.is_valid():
                comment = serializer.save(admin_id=request.user, event_id=event)
                return Response(
                    CommentSerializer(comment).data, status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CommentPermissionDeniedException as e:
            return Response(
                {"error": e.error, "message": e.message},
                status=status.HTTP_403_FORBIDDEN,
            )

    @classmethod
    def update_comment(cls, request, comment_id):
        comment = cls.get_comment(comment_id)
        serializer = CommentCreateSerializer(comment, data=request.data, partial=True)

        if serializer.is_valid():
            updated_comment = serializer.save()
            return Response(CommentSerializer(updated_comment).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @classmethod
    def delete_comment(cls, comment_id):
        comment = cls.get_comment(comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
