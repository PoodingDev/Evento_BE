from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response

from comment.models import Comment
from comment.serializers import CommentSerializer
from event.models import Event


class EventNotFoundException(Exception):
    def __init__(self):
        self.error = "이벤트 없음"
        self.message = "해당 이벤트를 찾을 수 없습니다."


class CommentNotFoundException(Exception):
    def __init__(self):
        self.error = "댓글 없음"
        self.message = "해당 댓글을 찾을 수 없습니다."


def get_event(event_id):
    # 이벤트 조회
    try:
        return Event.objects.get(event_id=event_id)
    except ObjectDoesNotExist:
        raise EventNotFoundException()


def get_comment(comment_id):
    # 댓글 조회
    try:
        return Comment.objects.get(comment_id=comment_id)
    except ObjectDoesNotExist:
        raise CommentNotFoundException()


def create_comment(request, event):
    # 댓글 생성
    serializer = CommentSerializer(
        data={
            "content": request.data.get("content"),
            "event_id": event.event_id,
            "admin_id": request.user.id,
        }
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def update_comment(request, comment_id):
    # 댓글 수정
    comment = get_comment(comment_id)
    serializer = CommentSerializer(comment, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def delete_comment(comment_id):
    # 댓글 삭제
    comment = get_comment(comment_id)
    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
