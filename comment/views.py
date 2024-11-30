from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from comment.serializers import CommentCreateSerializer, CommentSerializer
from comment.services import (
    CommentNotFoundException,
    CommentService,
    EventNotFoundException,
)


class CommentListCreateView(APIView):
    @extend_schema(tags=["댓글"], responses={200: CommentSerializer(many=True)})
    def get(self, request, event_id):
        try:
            event = CommentService.get_event(event_id)
            comments, error = CommentService.get_comments(request, event)
            if error:
                return Response(error, status=403)
            return Response({"comments": CommentSerializer(comments, many=True).data})
        except EventNotFoundException as e:
            return Response({"error": e.error, "message": e.message}, status=404)

    @extend_schema(
        tags=["댓글"],
        request=CommentCreateSerializer,
        responses={201: CommentSerializer},
    )
    def post(self, request, event_id):
        try:
            event = CommentService.get_event(event_id)
            return CommentService.create_comment(request, event)
        except EventNotFoundException as e:
            return Response({"error": e.error, "message": e.message}, status=404)


class CommentDetailView(APIView):
    @extend_schema(
        tags=["댓글"],
        request=CommentCreateSerializer,
        responses={200: CommentSerializer},
    )
    def put(self, request, event_id, comment_id):
        try:
            return CommentService.update_comment(request, comment_id)
        except CommentNotFoundException as e:
            return Response(
                {"error": e.error, "message": e.message},
                status=status.HTTP_404_NOT_FOUND,
            )

    @extend_schema(tags=["댓글"], responses={204: None})
    def delete(self, request, event_id, comment_id):
        try:
            return CommentService.delete_comment(comment_id)
        except CommentNotFoundException as e:
            return Response(
                {"error": e.error, "message": e.message},
                status=status.HTTP_404_NOT_FOUND,
            )
