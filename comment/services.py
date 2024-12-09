import uuid

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response

from calendars.models import Calendar
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


class CalendarNotFoundException(CommentException):
    def __init__(self):
        super().__init__("캘린더 없음", "해당 캘린더를 찾을 수 없습니다.")


class CommentService:
    @staticmethod
    def check_comment_permission(user, event_id):
        """
        댓글 작성 권한 확인
        - 캘린더의 creator나 admin만 댓글 작성 가능
        """
        try:
            event = Event.objects.get(event_id=event_id)
            calendar = event.calendar_id  # 이벤트가 속한 캘린더

            # 캘린더의 creator이거나 admin인 경우에만 허용
            if user == calendar.creator or user in calendar.admins.all():
                return True
            raise CommentPermissionDeniedException()

        except Event.DoesNotExist:
            raise EventNotFoundException()
        except Calendar.DoesNotExist:
            raise CalendarNotFoundException()

    @staticmethod
    def get_event(event_id):
        try:
            # UUID 문자열을 그대로 사용
            event_uuid = uuid.UUID(event_id)
            return Event.objects.get(event_id=event_id)
        except ObjectDoesNotExist:
            raise EventNotFoundException()
        except ValueError:
            raise ValidationError("유효한 UUID 형식이 아닙니다.")

    @staticmethod
    def get_comment(comment_id):
        try:
            return Comment.objects.get(comment_id=comment_id)
        except ObjectDoesNotExist:
            raise CommentNotFoundException()

    @classmethod
    def get_comments(cls, request, event_id):
        try:
            cls.check_comment_permission(request.user, event_id)
            comments = Comment.objects.filter(event_id=event_id)
            return comments, None
        except CommentPermissionDeniedException as e:
            return None, {"error": e.error, "message": e.message}

    @classmethod
    def create_comment(cls, request, event_id):
        """댓글 생성"""
        # 권한 확인 - event_id 전달
        cls.check_comment_permission(request.user, event_id)

        # 이벤트 확인
        event = cls.get_event(event_id)

        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(event=event, admin_id=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
