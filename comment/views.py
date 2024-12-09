from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from comment.serializers import CommentCreateSerializer, CommentSerializer
from comment.services import (
    CalendarNotFoundException,
    CommentNotFoundException,
    CommentPermissionDeniedException,
    CommentService,
    EventNotFoundException,
)


class CommentListCreateView(APIView):
    @extend_schema(tags=["댓글"], responses={200: CommentSerializer(many=True)})
    def get(self, request, event_id):
        try:
            comments, error = CommentService.get_comments(request, event_id)
            if error:
                return Response(error, status=status.HTTP_403_FORBIDDEN)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (
            EventNotFoundException,
            CalendarNotFoundException,
            CommentPermissionDeniedException,
        ) as e:
            return Response(
                {"error": e.error, "message": e.message},
                status=status.HTTP_404_NOT_FOUND,
            )

    @extend_schema(
        tags=["댓글"],
        parameters=[
            OpenApiParameter(
                name="event_id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
                description="이벤트 UUID",
                required=True,
            )
        ],
        request=CommentCreateSerializer,
        responses={201: CommentSerializer},
    )
    def post(self, request, event_id):
        try:
            return CommentService.create_comment(request, event_id)
        except (
            EventNotFoundException,
            CalendarNotFoundException,
            CommentPermissionDeniedException,
        ) as e:
            return Response(
                {"error": e.error, "message": e.message},
                status=status.HTTP_404_NOT_FOUND,
            )


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
