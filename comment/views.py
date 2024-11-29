from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from comment.services import (
    get_event, create_comment, get_comment, 
    update_comment, delete_comment,
    EventNotFoundException, CommentNotFoundException
)
from comment.serializers import CommentSerializer, CommentCreateSerializer
from comment.models import Comment


class CommentListCreateView(APIView):
    #댓글 목록 조회 및 생성 View
    @extend_schema(responses={200: CommentSerializer(many=True)})
    def get(self, request, event_id):
        #댓글 목록 조회
        try:
            event = get_event(event_id)
            comments = Comment.objects.filter(event_id=event)
            comment_serializer = CommentSerializer(comments, many=True)
            response_data = {
                'comments': comment_serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except EventNotFoundException as e:
            return Response(
                {"error": e.error, "message": e.message}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(request=CommentCreateSerializer, responses={201: CommentSerializer})
    def post(self, request, event_id):
        #댓글 생성
        try:
            event = get_event(event_id)
            return create_comment(request, event)
        except EventNotFoundException as e:
            return Response(
                {"error": e.error, "message": e.message}, 
                status=status.HTTP_404_NOT_FOUND
            )

class CommentDetailView(APIView):
    #개별 댓글 조회, 수정, 삭제 View
    @extend_schema(responses={200: CommentSerializer})
    def get(self, request, event_id, comment_id):
        #개별 댓글 조회
        try:
            comment = get_comment(comment_id)
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        except CommentNotFoundException as e:
            return Response(
                {"error": e.error, "message": e.message}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(request=CommentSerializer, responses={200: CommentSerializer})
    def put(self, request, event_id, comment_id):
        #댓글 수정
        try:
            return update_comment(request, comment_id)
        except CommentNotFoundException as e:
            return Response(
                {"error": e.error, "message": e.message}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(responses={204: None})
    def delete(self, request, event_id, comment_id):
        #댓글 삭제
        try:
            return delete_comment(comment_id)
        except CommentNotFoundException as e:
            return Response(
                {"error": e.error, "message": e.message}, 
                status=status.HTTP_404_NOT_FOUND
            )