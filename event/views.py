import csv

with open("event_schedule.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["title", "description", "start_time", "end_time", "is_public"])
    writer.writerow(["Event 1", "Description 1", "2024-12-01T10:00:00", "2024-12-01T12:00:00", True])
    writer.writerow(["Event 2", "Description 2", "2024-12-02T14:00:00", "2024-12-02T16:00:00", False])

import pandas as pd

from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .models import Event
from .serializers import EventSerializer


class PublicEventListAPIView(ListAPIView):
    """
    공개 이벤트 목록 조회
    - GET: 공개된 모든 이벤트를 조회합니다.
    """
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]  # JWT 인증 필수

    @extend_schema(
        # tags=["공개 이벤트"],
        summary="공개 이벤트 목록 조회",
        description="공개된 모든 이벤트를 반환합니다.",
        responses={200: EventSerializer(many=True)},
    )
    def get_queryset(self):
        # 공개된 이벤트만 반환
        return Event.objects.filter(is_public=True)


class PublicEventListCreateAPIView(CreateAPIView):
    """
    공개 이벤트 생성
    - POST: 새로운 공개 이벤트를 생성합니다.
    """
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        # tags=["공개 이벤트"],
        summary="공개 이벤트 생성",
        description="새로운 공개 이벤트를 생성합니다.",
        request=EventSerializer,
        responses={201: EventSerializer},
    )
    def perform_create(self, serializer):
        # 생성 시 요청 유저를 admin_id로 설정
        serializer.save(admin_id=self.request.user, is_public=True)


class PrivateEventListAPIView(ListAPIView):
    """
    비공개 이벤트 목록 조회
    - GET: 요청한 사용자가 관리하는 비공개 이벤트만 조회합니다.
    """
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        # tags=["비공개 이벤트"],
        summary="비공개 이벤트 목록 조회",
        description="사용자가 관리하는 비공개 이벤트를 반환합니다.",
        responses={200: EventSerializer(many=True)},
    )
    def get_queryset(self):
        # 요청 사용자가 관리하는 비공개 이벤트만 반환
        return Event.objects.filter(admin_id=self.request.user, is_public=False)


class PrivateEventListCreateAPIView(CreateAPIView):
    """
    비공개 이벤트 생성
    - POST: 새로운 비공개 이벤트를 생성합니다.
    """
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        # tags=["비공개 이벤트"],
        summary="비공개 이벤트 생성",
        description="새로운 비공개 이벤트를 생성합니다.",
        request=EventSerializer,
        responses={201: EventSerializer},
    )
    def perform_create(self, serializer):
        # 생성 시 요청 유저를 admin_id로 설정
        serializer.save(admin_id=self.request.user, is_public=False)


class EventRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    이벤트 상세 조회, 수정, 삭제
    - GET: 특정 이벤트의 상세 정보를 반환합니다.
    - PUT: 특정 이벤트 정보를 수정합니다.
    - DELETE: 특정 이벤트를 삭제합니다.
    """
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        # tags=["이벤트"],
        summary="이벤트 상세 조회",
        description="특정 이벤트의 상세 정보를 반환합니다.",
        responses={200: EventSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        # tags=["이벤트"],
        summary="이벤트 수정",
        description="특정 이벤트의 정보를 수정합니다.",
        request=EventSerializer,
        responses={200: EventSerializer},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        # tags=["이벤트"],
        summary="이벤트 삭제",
        description="특정 이벤트를 삭제합니다.",
        responses={204: None},
    )
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": f"'{instance.title}' 이벤트가 삭제되었습니다."},
            status=status.HTTP_204_NO_CONTENT,
        )

class EventUploadView(APIView):
    """
    CSV 또는 Excel 파일로 이벤트 일괄 업로드/업데이트
    - POST: 파일을 업로드하여 이벤트를 생성하거나 업데이트합니다.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        # tags=["이벤트"],
        summary="이벤트 일괄 업로드/업데이트",
        description="CSV 또는 Excel 파일을 사용하여 이벤트를 생성하거나 업데이트합니다.",
        request={
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "format": "binary",
                    "description": "업로드할 CSV 또는 Excel 파일",
                },
            },
            "required": ["file"],
        },
        responses={
            200: {
                "description": "업로드 성공",
                "content": {
                    "application/json": {
                        "example": {
                            "created_events": [
                                {"title": "Event 1", "start_time": "2024-12-01T10:00:00", "is_public": True},
                            ],
                            "updated_events": [
                                {"title": "Event 2", "start_time": "2024-12-02T14:00:00", "is_public": False},
                            ],
                        }
                    }
                },
            },
            400: {
                "description": "잘못된 요청",
                "content": {
                    "application/json": {
                        "example": {"error": "지원하지 않는 파일 형식입니다. CSV 또는 Excel 파일을 사용하세요."}
                    }
                },
            },
            404: {
                "description": "이벤트를 찾을 수 없음",
                "content": {
                    "application/json": {
                        "example": {"error": "ID 123 이벤트를 찾을 수 없습니다."}
                    }
                },
            },
        },
    )
    def post(self, request, *args, **kwargs):
        # 1. 파일 가져오기
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "파일을 업로드하세요."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. 파일 형식 확인 및 데이터 로드
        try:
            if file.name.endswith(".csv"):
                data = pd.read_csv(file)
            elif file.name.endswith(".xlsx"):
                data = pd.read_excel(file)
            else:
                return Response({"error": "지원하지 않는 파일 형식입니다. CSV 또는 Excel 파일을 사용하세요."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"파일 처리 중 오류가 발생했습니다: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # 3. 필수 필드 확인
        required_fields = ["calendar_id", "title", "description", "start_time", "end_time", "is_public"]
        missing_fields = [field for field in required_fields if field not in data.columns]
        if missing_fields:
            return Response({"error": f"누락된 필드: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)

        # 4. 데이터 처리
        created_events = []
        updated_events = []
        for _, row in data.iterrows():
            try:
                # 업데이트 처리
                event_id = row.get("event_id")
                if event_id:
                    event = Event.objects.get(event_id=event_id, admin_id=request.user)
                    for attr, value in row.items():
                        setattr(event, attr, value)
                    event.save()
                    updated_events.append(event)
                else:
                    # 생성 처리
                    serializer = EventSerializer(data=row.to_dict())
                    if serializer.is_valid():
                        serializer.save(admin_id=request.user)
                        created_events.append(serializer.data)
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Event.DoesNotExist:
                return Response({"error": f"ID {event_id} 이벤트를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 5. 응답 반환
        return Response({
            "created_events": created_events,
            "updated_events": [EventSerializer(event).data for event in updated_events],
        }, status=status.HTTP_200_OK)
