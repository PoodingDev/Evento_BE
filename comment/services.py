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
    def extract_uuid(event_id_str):
        """문자열에서 UUID 추출"""
        try:
            # UUID 패턴 찾기 (마지막 UUID 형식 문자열 추출)
            if isinstance(event_id_str, uuid.UUID):
                return event_id_str

            # 문자열에서 UUID 부분만 추출
            if "(ID:" in event_id_str:
                uuid_str = event_id_str.split("(ID:")[-1].strip(' )"')
            else:
                uuid_str = event_id_str.strip()

            return uuid.UUID(uuid_str)
        except (ValueError, AttributeError):
            raise ValidationError("유효한 UUID 형식이 아닙니다.")

    @staticmethod
    def check_comment_permission(user, event_id):
        """
        댓글 작성 권한 확인
        - 캘린더의 creator나 admin만 댓글 작성 가능
        """
        try:
            # UUID 추출 및 변환
            event_uuid = CommentService.extract_uuid(event_id)
            event = Event.objects.get(event_id=event_uuid)
            calendar = event.calendar_id

            if user == calendar.creator or user in calendar.admins.all():
                return True
            raise CommentPermissionDeniedException()

        except Event.DoesNotExist:
            raise EventNotFoundException()
        except Calendar.DoesNotExist:
            raise CalendarNotFoundException()

    @staticmethod
    def get_event(event_id):
        """이벤트 조회"""
        try:
            # UUID 추출 및 변환
            event_uuid = CommentService.extract_uuid(event_id)
            return Event.objects.get(event_id=event_uuid)
        except Event.DoesNotExist:
            raise EventNotFoundException()

    @staticmethod
    def get_comment(comment_id):
        try:
            return Comment.objects.get(comment_id=comment_id)
        except ObjectDoesNotExist:
            raise CommentNotFoundException()

    @classmethod
    def get_comments(cls, request, event_id):
        try:
            # 권한 확인
            cls.check_comment_permission(request.user, event_id)

            # UUID 추출 및 변환
            event_uuid = cls.extract_uuid(event_id)

            # 해당 이벤트의 댓글 조회
            comments = Comment.objects.filter(event__event_id=event_uuid)
            return comments, None

        except CommentPermissionDeniedException as e:
            return None, {"error": e.error, "message": e.message}

    @classmethod
    def create_comment(cls, request, event_id):
        """댓글 생성"""
        # 권한 확인
        cls.check_comment_permission(request.user, event_id)

        # 이벤트 조회
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
