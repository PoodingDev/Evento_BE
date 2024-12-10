import csv

import pandas as pd

from django.db.models import Q
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListCreateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.exceptions import NotAuthenticated

from .models import Event, Calendar
from .serializers import EventSerializer, PublicEventSerializer, PrivateEventSerializer


with open("event_schedule.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["title", "description", "start_time", "end_time", "is_public"])
    writer.writerow(
        ["Event 1", "Description 1", "2024-12-01T10:00:00", "2024-12-01T12:00:00", True]
    )
    writer.writerow(
        [
            "Event 2",
            "Description 2",
            "2024-12-02T14:00:00",
            "2024-12-02T16:00:00",
            False,
        ]
    )

class PublicEventListAPIView(ListAPIView):
    """
    공개 이벤트 목록 조회
    - GET: 공개된 모든 이벤트를 조회합니다.
    """

    serializer_class = PublicEventSerializer
    permission_classes = [IsAuthenticated]  # JWT 인증 필수

    @extend_schema(
        # tags=["공개 이벤트"],
        summary="공개 이벤트 목록 조회",
        description="공개된 모든 이벤트를 반환합니다.",
        responses={200: PublicEventSerializer(many=True)},
    )
    def get_queryset(self):
        # 사용자가 관리자이거나 구독한 캘린더의 이벤트만 조회
        return Event.objects.filter(
            calendar_id__in=Calendar.objects.filter(
                Q(creator=self.request.user)  # 캘린더 생성자
                | Q(admins=self.request.user)  # 캘린더 관리자
                | Q(
                    subscriptions__user=self.request.user, subscriptions__is_active=True
                )  # 구독자
            )
            .distinct()
            .values_list("calendar_id", flat=True),
            is_public=True,
        )


class PublicEventCreateAPIView(CreateAPIView):
    """
    공개 이벤트 생성
    - POST: 새로운 공개 이벤트를 생성합니다.
    """

    serializer_class = PublicEventSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        # tags=["공개 이벤트"],
        summary="공개 이벤트 생성",
        description="새로운 공개 이벤트를 생성합니다.",
        request=PublicEventSerializer,
        responses={201: PublicEventSerializer},
    )
    def perform_create(self, serializer):
        serializer.save()


class PrivateEventListAPIView(ListAPIView):
    """
    비공개 이벤트 목록 조회
    - GET: 요청한 사용자가 관리하는 비공개 이벤트만 조회합니다.
    """

    serializer_class = PrivateEventSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        # tags=["비공개 이벤트"],
        summary="비공개 이벤트 목록 조회",
        description="사용자가 관리하는 비공개 이벤트를 반환합니다.",
        responses={200: PrivateEventSerializer(many=True)},
    )
    def get_queryset(self):
        # 요청 사용자가 관리하는 비공개 이벤트만 반환
        return Event.objects.filter(admin_id=self.request.user, is_public=False)


class PrivateEventCreateAPIView(CreateAPIView):
    """
    비공개 이벤트 생성
    - POST: 새로운 비공개 이벤트를 생성합니다.
    """

    serializer_class = PrivateEventSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="비공개 이벤트 생성",
        description="새로운 비공개 이벤트를 생성합니다.",
        request=PrivateEventSerializer,
        responses={201: PrivateEventSerializer},
    )
    def perform_create(self, serializer):
        serializer.save()


class EventRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    이벤트 상세 조회, 수정, 삭제
    """

    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "event_id"

    def get_queryset(self):
        return Event.objects.all()

    def perform_destroy(self, instance):
        """이벤트 삭제 전 권한 확인"""
        try:
            calendar_id = instance.calendar_id_id  # ForeignKey 필드의 ID 접근
            calendar = Calendar.objects.get(calendar_id=calendar_id)

            if (
                self.request.user == calendar.creator
                or self.request.user in calendar.admins.all()
            ):
                instance.delete()
            else:
                raise PermissionDenied("이 이벤트를 삭제할 권한이 없습니다.")
        except Calendar.DoesNotExist:
            raise Http404("캘린더를 찾을 수 없습니다.")

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response(
                {"error": "해당 이벤트나 캘린더를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        elif isinstance(exc, PermissionDenied):
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        return super().handle_exception(exc)

    @extend_schema(
        summary="이벤트 삭제",
        description="특정 이벤트를 삭제합니다. 캘린더 관리자만 삭제할 수 있습니다.",
        responses={
            204: None,
            403: {"description": "이 이벤트를 삭제할 권한이 없습니다."},
            404: {"description": "해당 이벤트를 찾을 수 없습니다."},
        },
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

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
                                {
                                    "title": "Event 1",
                                    "start_time": "2024-12-01T10:00:00",
                                    "is_public": True,
                                },
                            ],
                            "updated_events": [
                                {
                                    "title": "Event 2",
                                    "start_time": "2024-12-02T14:00:00",
                                    "is_public": False,
                                },
                            ],
                        }
                    }
                },
            },
            400: {
                "description": "잘못된 요청",
                "content": {
                    "application/json": {
                        "example": {
                            "error": "지원하지 않는 파일 형식입니다. CSV 또는 Excel 파일을 사용하세요."
                        }
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
            return Response(
                {"error": "파일을 업로드하세요."}, status=status.HTTP_400_BAD_REQUEST
            )

        # 2. 파일 형식 확인 및 데이터 로드
        try:
            if file.name.endswith(".csv"):
                data = pd.read_csv(file)
            elif file.name.endswith(".xlsx"):
                data = pd.read_excel(file)
            else:
                return Response(
                    {
                        "error": "지원하지 않는 파일 형식입니다. CSV 또는 Excel 파일을 사용하세요."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"error": f"파일 처리 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. 필수 필드 확인
        required_fields = [
            "calendar_id",
            "title",
            "description",
            "start_time",
            "end_time",
            "is_public",
        ]
        missing_fields = [
            field for field in required_fields if field not in data.columns
        ]
        if missing_fields:
            return Response(
                {"error": f"누락된 필드: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
                    serializer = PublicEventSerializer(data=row.to_dict())
                    if serializer.is_valid():
                        serializer.save(admin_id=request.user)
                        created_events.append(serializer.data)
                    else:
                        return Response(
                            serializer.errors, status=status.HTTP_400_BAD_REQUEST
                        )
            except Event.DoesNotExist:
                return Response(
                    {"error": f"ID {event_id} 이벤트를 찾을 수 없습니다."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # 5. 응답 반환
        return Response(
            {
                "created_events": created_events,
                "updated_events": [
                    PublicEventSerializer(event).data for event in updated_events
                ],
            },
            status=status.HTTP_200_OK,
        )
