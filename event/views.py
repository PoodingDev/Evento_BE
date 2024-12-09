import csv

with open("event_schedule.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["title", "description", "start_time", "end_time", "is_public"])
    writer.writerow(["Event 1", "Description 1", "2024-12-01T10:00:00", "2024-12-01T12:00:00", True])
    writer.writerow(["Event 2", "Description 2", "2024-12-02T14:00:00", "2024-12-02T16:00:00", False])

import pandas as pd

from django.db.models import Q
from rest_framework.views import APIView
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

from .models import Event, Calendar
from .serializers import EventSerializer, PublicEventSerializer, PrivateEventSerializer

class PublicEventViewSet(ListCreateAPIView):
    serializer_class = PublicEventSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="공개 이벤트 목록 조회",
        responses={
            200: OpenApiResponse(
                response=PublicEventSerializer(many=True),
                description="공개 이벤트 목록 조회 성공"
            )
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="공개 이벤트 생성",
        request=PublicEventSerializer,
        responses={
            201: OpenApiResponse(
                response=PublicEventSerializer,
                description="공개 이벤트 생성 성공"
            ),
            400: OpenApiResponse(description="잘못된 요청")
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return Event.objects.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(admin_id=self.request.user)

class PrivateEventViewSet(ListCreateAPIView):
    serializer_class = PrivateEventSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="비공개 이벤트 목록 조회",
        responses={
            200: OpenApiResponse(
                response=PrivateEventSerializer(many=True),
                description="비공개 이벤트 목록 조회 성공"
            )
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="비공개 이벤트 생성",
        request=PrivateEventSerializer,
        responses={
            201: OpenApiResponse(
                response=PrivateEventSerializer,
                description="비공개 이벤트 생성 성공"
            ),
            400: OpenApiResponse(description="잘못된 요청")
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return Event.objects.filter(
            is_public=False,
            admin_id=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(admin_id=self.request.user)

class EventDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'event_id'

    def get_serializer_class(self):
        event = self.get_object()
        return PublicEventSerializer if event.is_public else PrivateEventSerializer

    @extend_schema(
        summary="이벤트 상세 조회",
        responses={
            200: OpenApiResponse(
                response=EventSerializer,
                description="이벤트 조회 성공"
            ),
            404: OpenApiResponse(description="이벤트를 찾을 수 없음")
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="이벤트 수정",
        request=EventSerializer,
        responses={
            200: OpenApiResponse(
                response=EventSerializer,
                description="이벤트 수정 성공"
            ),
            400: OpenApiResponse(description="잘못된 요청"),
            404: OpenApiResponse(description="이벤트를 찾을 수 없음")
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="이벤트 삭제",
        responses={
            204: OpenApiResponse(description="이벤트 삭제 성공"),
            404: OpenApiResponse(description="이벤트를 찾을 수 없음")
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Event.objects.filter(
            Q(is_public=True) |
            Q(admin_id=self.request.user)
        )


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
    def perform_create(self, serializer):
        # is_public을 무조건 True로 설정
        serializer.save(admin_id=self.request.user, is_public=True)

    def get_queryset(self):
        # 공개된 이벤트만 반환
        return Event.objects.filter(is_public=True)

    def post(self, request):
        data = request.data.copy()

        # is_public 값을 명시적으로 처리
        # 요청 데이터의 is_public 값을 강제로 True로 설정
        data["is_public"] = True

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PublicEventListCreateAPIView(CreateAPIView):
    """
    공개 이벤트 생성
    - POST: 새로운 공개 이벤트를 생성합니다.
    """
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    # GET 요청: 전체 이벤트 조회
    def get(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # POST 요청: 새로운 이벤트 생성
    def post(self, request):
        # 요청 데이터에 is_public이 없으면 기본값 False로 설정
        data = request.data.copy()
        if 'is_public' not in data:
            data['is_public'] = True

        serializer = EventSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        # tags=["공개 이벤트"],
        summary="공개 이벤트 생성",
        description="새로운 공개 이벤트를 생성합니다.",
        request=EventSerializer,
        responses={201: EventSerializer},
    )
    def perform_create(self, serializer):
        # 생성 시 요청 유저를 admin_id로 설정
        # serializer.save(admin_id=self.request.user, is_public=True)
        serializer.save()


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

    # GET 요청: 전체 이벤트 조회
    def get(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        # tags=["비공개 이벤트"],
        summary="비공개 이벤트 생성",
        description="새로운 비공개 이벤트를 생성합니다.",
        request=EventSerializer,
        responses={201: EventSerializer},
    )
    def perform_create(self, serializer):
        # is_public을 무조건 False로 설정
        # serializer.save(admin_id=self.request.user, is_public=False)
        serializer.save()

    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        # 요청 데이터의 is_public 값을 강제로 False로 설정
        data["is_public"] = False

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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


class UserRelatedEventListAPIView(ListAPIView):
    """
    관리자로 등록된 캘린더의 이벤트와
    구독자로 등록된 공개 캘린더의 이벤트를 반환
    """
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="사용자 관련 이벤트 조회",
        description="관리자로 속한 캘린더의 이벤트와 구독 중인 공개 캘린더의 이벤트를 반환합니다.",
        responses={200: EventSerializer(many=True)},
    )
    def get_queryset(self):
        user = self.request.user

        # 내가 관리자로 속하고 is_active=True인 캘린더의 모든 이벤트
        admin_calendar_events = Event.objects.filter(
            calendar__admins=user,
            calendar__subscriptions__is_active=True,
        )

        # 내가 구독자로 속하고 is_active=True인 캘린더의 공개 이벤트
        subscriber_calendar_events = Event.objects.filter(
            calendar__subscriptions__user=user,
            calendar__subscriptions__is_active=True,
            is_public=True,
        )

        # 두 조건의 합집합 반환
        return admin_calendar_events | subscriber_calendar_events

