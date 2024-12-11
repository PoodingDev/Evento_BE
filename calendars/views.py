from django.db import models, transaction
from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Calendar, CalendarAdmin, Subscription
from .serializers import (
    AdminInvitationSerializer,
    CalendarCreateSerializer,
    CalendarDetailSerializer,
    SubscriptionSerializer,
    UpdateCalendarActiveSerializer,
)


class CalendarListCreateAPIView(ListCreateAPIView):
    """
    캘린더 목록 조회 및 생성
    """

    queryset = Calendar.objects.all()
    serializer_class = CalendarCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Calendar.objects.none()

        return Calendar.objects.filter(
            Q(creator=user)
            | Q(calendar_admins__user=user, calendar_admins__is_active=True)
        ).distinct()

    @extend_schema(
        summary="캘린더 목록 조회",
        description="현재 사용자가 생성한 캘린더 목록을 반환합니다.",
        responses={200: CalendarDetailSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="캘린더 생성",
        description="새로운 캘린더를 생성합니다.",
        request=CalendarCreateSerializer,
        responses={201: CalendarCreateSerializer(many=True)},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # 생성자 또는 관리자로 속한 캘린더 조회 가능
            return self.queryset.filter(
                models.Q(creator=self.request.user) | models.Q(admins=self.request.user)
            ).distinct()
        return Calendar.objects.none()  # 인증되지 않은 경우 빈 쿼리셋 반환

    def get_serializer_context(self):
        """
        Serializer에 request context 추가
        """
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)  # 캘린더 생성시 creator 설정


class CalendarRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    캘린더 상세 조회, 수정, 삭제
    """

    queryset = Calendar.objects.all()
    serializer_class = CalendarDetailSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="캘린더 상세 조회",
        description="특정 캘린더의 세부 정보를 반환합니다.",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "calendar": {"$ref": "#/components/schemas/CalendarDetail"},
                    "creator_id": {"type": "integer"},
                },
            }
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            calendar = self.get_object()  # URL에서 calendar_id로 캘린더 객체를 가져옴
            serializer = self.get_serializer(calendar)

            # 응답 데이터 생성
            data = {
                "calendar": serializer.data,
                "creator_id": calendar.creator_id,  # 생성자의 ID 추가
            }
            return Response(data, status=status.HTTP_200_OK)
        except Calendar.DoesNotExist:
            return Response(
                {"error": "캘린더를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def get_serializer_context(self):
        """
        Serializer에 request context 전달
        """
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    #
    # def get(self, request, *args, **kwargs):
    #     self.serializer_context = {"request": self.request}
    #     return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="캘린더 수정",
        description="특정 캘린더의 정보를 수정합니다.",
        request=CalendarDetailSerializer,
        responses={200: CalendarDetailSerializer},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="구독한 캘린더 목록 조회",
        description="현재 사용자가 구독한 캘린더 목록을 반환합니다.",
        responses={
            200: {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "subscription_id": {"type": "integer"},
                        "calendar_id": {"type": "integer"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "is_public": {"type": "boolean"},
                        "color": {"type": "string"},
                        "creator_id": {"type": "integer"},
                        "creator_nickname": {"type": "string"},
                        "is_active": {"type": "boolean"},
                    },
                },
            }
        },
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # 생성자 또는 관리자로 속한 캘린더 조회/수정 가능
            return self.queryset.filter(
                models.Q(creator=self.request.user) | models.Q(admins=self.request.user)
            ).distinct()
        return Calendar.objects.none()


class SubscriptionListCreateAPIView(ListCreateAPIView):
    """
    구독한 캘린더 조회 및 구독 추가
    """

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    @extend_schema(
        summary="구독한 캘린더 목록 조회",
        description="현재 사용자가 구독한 캘린더 목록을 반환합니다.",
        responses={200: SubscriptionSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        subscriptions = self.get_queryset()
        data = []

        for subscription in subscriptions:
            calendar = subscription.calendar
            subscription_data = {
                "subscription_id": subscription.id,
                "calendar_id": calendar.calendar_id,
                "name": calendar.name,
                "description": calendar.description,
                "is_public": calendar.is_public,
                "color": calendar.color,
                "creator_id": calendar.creator_id,
                "creator_nickname": calendar.creator.nickname,
                "is_active": subscription.is_active,  # Subscription 모델의 is_active 사용
            }
            data.append(subscription_data)

        return Response(data, status=200)

    @extend_schema(
        summary="캘린더 구독 추가",
        description="특정 캘린더를 구독합니다.",
        request=SubscriptionSerializer,
        responses={201: SubscriptionSerializer},
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        calendar_id = request.data.get("calendar_id")

        try:
            # 캘린더가 존재하고 공개 상태인지 확인
            calendar = Calendar.objects.get(calendar_id=calendar_id)
            if not calendar.is_public:
                return Response(
                    {"error": "비공개 캘린더는 구독할 수 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 중복 구독 체크
            if Subscription.objects.filter(user=user, calendar=calendar).exists():
                return Response(
                    {"error": "이미 구독된 캘린더입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 구독 생성 (is_active=True로 설정)
            subscription = Subscription.objects.create(
                user=user, calendar=calendar, is_active=True  # 구독 시 자동으로 활성화
            )

            serializer = self.get_serializer(subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Calendar.DoesNotExist:
            return Response(
                {"error": "캘린더를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            # 구독 생성 시 요청 사용자를 설정
            serializer.save(user=self.request.user)


class SubscriptionDeleteAPIView(APIView):
    """
    특정 캘린더 구독 취소
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="특정 캘린더 구독 취소",
        description="특정 캘린더의 구독을 취소합니다.",
        parameters=[
            OpenApiParameter(
                name="calendar_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="캘린더 ID",
                required=True,
            )
        ],
        responses={
            204: None,
            400: {"description": "잘못된 요청입니다."},
            404: {"description": "구독 정보를 찾을 수 없습니다."},
        },
    )
    def delete(self, request, calendar_id):
        if calendar_id == "undefined" or not calendar_id:
            return Response(
                {"error": "유효하지 않은 캘린더 ID입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            subscription = Subscription.objects.get(
                user=request.user, calendar_id=calendar_id
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Subscription.DoesNotExist:
            return Response(
                {"error": "구독 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


class CalendarSearchAPIView(ListAPIView):
    """
    닉네임으로 시작하는 사용자가 만든 공개 캘린더 검색 API
    """

    serializer_class = CalendarDetailSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="닉네임으로 시작하는 유저가 만든 공개 캘린더 검색",
        description="닉네임으로 시작하는 유저가 생성한 공개 캘린더를 검색합니다.",
        parameters=[
            OpenApiParameter(
                name="nickname",
                type=str,
                location=OpenApiParameter.PATH,
                description="검색할 닉네임",
                required=True,
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "calendar_id": {"type": "integer"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "creator_nickname": {"type": "string"},
                    "is_public": {"type": "boolean"},
                    "color": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "is_subscribed": {"type": "boolean"},
                },
            }
        },
    )
    def get(self, request, nickname):
        if not nickname:
            return Response({"error": "닉네임을 입력해주세요."}, status=400)

        calendars = (
            Calendar.objects.filter(
                is_public=True, creator__nickname__istartswith=nickname
            )
            .select_related("creator")
            .distinct()
        )

        data = []
        for calendar in calendars:
            is_subscribed = Subscription.objects.filter(
                user=request.user, calendar=calendar
            ).exists()

            calendar_data = {
                "calendar_id": calendar.calendar_id,
                "name": calendar.name,
                "description": calendar.description,
                "creator_nickname": calendar.creator.nickname,
                "is_public": calendar.is_public,
                "color": calendar.color,
                "created_at": calendar.created_at,
                "is_subscribed": is_subscribed,
            }
            data.append(calendar_data)

        return Response(data, status=200)


# 메모리 내 상태 저장소
calendar_admin_active_status = {}


class UpdateCalendarAdminActiveView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateCalendarActiveSerializer

    @extend_schema(
        summary="관리 캘린더 표시여부 업데이트",
        description="체크박스 상태에 따라 관리 캘린더의 표시 여부를 업데이트합니다.",
        request=UpdateCalendarActiveSerializer,
        responses={
            200: {
                "description": "성공",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "캘린더 표시 여부가 성공적으로 업데이트되었습니다."
                        }
                    }
                },
            },
            400: {
                "description": "잘못된 요청",
                "content": {
                    "application/json": {
                        "example": {"error": "요청 데이터가 유효하지 않습니다."}
                    }
                },
            },
            404: {
                "description": "찾을 수 없음",
                "content": {
                    "application/json": {
                        "example": {"error": "해당 구독을 찾을 수 없습니다."}
                    }
                },
            },
        },
    )
    def patch(self, request):
        serializer = UpdateCalendarActiveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "요청 데이터가 유효하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        calendar_id = serializer.validated_data["calendar_id"]
        is_active = serializer.validated_data["is_active"]

        # 사용자별로 캘린더의 is_active 상태 저장
        user_key = getattr(request.user, "id", request.user.username)
        calendar_admin_active_status[(user_key, calendar_id)] = is_active

        return Response(
            {"message": "캘린더 표시 여부가 성공적으로 업데이트되었습니다."},
            status=status.HTTP_200_OK,
        )


class AdminCalendarsAPIView(ListAPIView):
    serializer_class = CalendarDetailSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="관리 권한이 있는 캘린더 조회",
        description="현재 사용자가 생성했거나 관리 권한을 부여받은 모든 캘린더를 반환합니다.",
        responses={
            200: {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "calendar_id": {"type": "integer"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "is_public": {"type": "boolean"},
                        "color": {"type": "string"},
                        "invitation_code": {"type": "string"},
                        "creator_id": {"type": "integer"},
                        "admins": {"type": "array", "items": {"type": "string"}},
                        "is_active": {"type": "boolean"},
                    },
                },
            }
        },
    )
    def get(self, request, *args, **kwargs):
        calendars = Calendar.objects.filter(
            Q(creator=request.user) | Q(admins=request.user)
        ).distinct()

        data = []
        user_key = getattr(request.user, "id", request.user.username)
        for calendar in calendars:
            # 메모리 내 상태에서 is_active 값 가져오기
            is_active = calendar_admin_active_status.get(
                (user_key, calendar.calendar_id), True
            )

            calendar_data = {
                "calendar_id": calendar.calendar_id,
                "name": calendar.name,
                "description": calendar.description,
                "is_public": calendar.is_public,
                "color": calendar.color,
                "invitation_code": calendar.invitation_code,
                "creator_id": calendar.creator_id,
                "admins": list(calendar.admins.values_list("nickname", flat=True)),
                "is_active": is_active,
            }
            data.append(calendar_data)

        return Response(data, status=200)


class CalendarMembersAPIView(ListAPIView):
    """
    캘린더에 속한 관리자 멤버 조회
    """

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]  # 인증 없이 접근 가능

    @extend_schema(
        summary="관리자 초대",
        description="초대 코드를 입력받아 해당 캘린더의 관리자로 추가합니다.",
        request={
            "type": "object",
            "properties": {
                "invitation_code": {
                    "type": "string",
                    "description": "캘린더 초대 코드",
                    "example": "ABC123",
                },
            },
            "required": ["invitation_code"],
        },
    )
    def get_queryset(self):
        calendar_id = self.kwargs.get("pk")
        if calendar_id:
            # 특정 캘린더에 속한 구독 사용자 조회
            return Subscription.objects.filter(calendar_id=calendar_id)
        return Subscription.objects.none()


class AdminInvitationView(APIView):
    """초대 코드를 통해 캘린더의 관리자로 추가하는 View"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="관리자 초대",
        description="초대 코드를 입력받아 해당 캘린더의 관리자로 추가합니다.",
        request=AdminInvitationSerializer,
        responses={
            200: CalendarDetailSerializer,
            400: {
                "description": "잘못된 요청 또는 이미 관리자",
                "content": {
                    "application/json": {
                        "example": {"error": "캘린더 생성자는 이미 관리자입니다."}
                    }
                },
            },
            404: {
                "description": "초대 코드가 유효하지 않음",
                "content": {
                    "application/json": {
                        "example": {"error": "유효하지 않은 초대 코드입니다."}
                    }
                },
            },
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = AdminInvitationSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        invitation_code = serializer.validated_data["invitation_code"]

        try:
            # 초대 코드에 해당하는 캘린더 찾기
            calendar = Calendar.objects.get(invitation_code=invitation_code)

            # 이미 관리자인지 확인
            if request.user == calendar.creator:
                return Response(
                    {"error": "캘린더 생성자는 이미 관리자입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if request.user in calendar.admins.all():
                return Response(
                    {"error": "이미 관리자로 추가된 캘린더입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 관리자로 추가
            calendar.admins.add(request.user)

            return Response(
                CalendarDetailSerializer(calendar).data, status=status.HTTP_200_OK
            )

        except Calendar.DoesNotExist:
            return Response(
                {"error": "유효하지 않은 초대 코드입니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


class ActiveSubscriptionsAPIView(ListAPIView):
    """
    활성화된 구독 캘린더 조회
    """

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user, is_active=True)

    @extend_schema(
        summary="활성화된 구독 캘린더 조회",
        description="사용자가 체크박스로 활성화한 구독 캘린더 목록을 반환합니다.",
        responses={200: SubscriptionSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UpdateActiveStatusAPIView(APIView):
    """
    캘린더 활성화 상태 변경
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="캘린더 활성화 상태 변경",
        description="사용자가 구독한 캘린더의 활성화 상태를 변경합니다.",
        request={
            "type": "object",
            "properties": {
                "subscription_id": {"type": "integer", "example": 1},
                "is_active": {"type": "boolean", "example": True},
            },
            "required": ["subscription_id", "is_active"],
        },
        responses={
            200: {
                "description": "성공적으로 활성화 상태가 변경되었습니다.",
                "content": {"application/json": {"example": {"message": "성공"}}},
            },
            400: {
                "description": "잘못된 요청입니다.",
                "content": {
                    "application/json": {
                        "example": {"error": "구독 정보를 찾을 수 없습니다."}
                    }
                },
            },
        },
    )
    def post(self, request, *args, **kwargs):
        subscription_id = request.data.get("subscription_id")
        is_active = request.data.get("is_active")

        try:
            subscription = Subscription.objects.get(
                id=subscription_id, user=request.user
            )
            subscription.is_active = is_active
            subscription.save()
            return Response({"message": "성공"}, status=200)
        except Subscription.DoesNotExist:
            return Response({"error": "구독 정보를 찾을 수 없습니다."}, status=404)


class UpdateSubscriptionVisibilityAPIView(APIView):
    """
    구독 캘린더 표시 여부 업데이트
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="구독 캘린더 표시 여부 업데이트",
        description="체크박스 상태에 따라 구독 캘린더의 표시 여부를 업데이트합니다.",
        request={
            "type": "object",
            "properties": {
                "subscription_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                },
                "is_on_calendar": {
                    "type": "boolean",
                    "description": "캘린더 표시 여부",
                },
            },
        },
        responses={
            200: {"type": "object", "properties": {"message": {"type": "string"}}},
        },
    )
    def put(self, request):
        subscription_ids = request.data.get("subscription_ids", [])
        is_on_calendar = request.data.get("is_on_calendar", True)  # 기본값 True

        user = request.user
        # 트랜잭션으로 모든 작업 처리
        with transaction.atomic():
            # 모든 구독 캘린더를 비활성화
            Subscription.objects.filter(user=user).update(
                is_visible=False, is_on_calendar=False
            )

            # 요청한 ID들만 활성화
            if subscription_ids:
                Subscription.objects.filter(user=user, id__in=subscription_ids).update(
                    is_visible=True, is_on_calendar=is_on_calendar
                )

        return Response(
            {"message": "구독 캘린더 표시 상태가 업데이트되었습니다."}, status=200
        )


class UpdateSubscriptionActiveView(APIView):
    """
    구독 캘린더의 활성화 상태 업데이트
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UpdateCalendarActiveSerializer

    @extend_schema(
        summary="구독 캘린더 표시여부 업데이트",
        description="체크박스 상태에 따라 구독 캘린더의 표시 여부를 업데이트합니다.",
        request=UpdateCalendarActiveSerializer,
        responses={
            200: {
                "description": "성공",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "캘린더 활성화 상태가 성공적으로 변경되었습니다."
                        }
                    }
                },
            },
            400: {
                "description": "잘못된 요청",
                "content": {
                    "application/json": {
                        "example": {"error": "요청 데이터가 유효하지 않습니다."}
                    }
                },
            },
            404: {
                "description": "찾을 수 없음",
                "content": {
                    "application/json": {
                        "example": {"error": "해당 구독 정보를 찾을 수 없습니다."}
                    }
                },
            },
        },
    )
    def patch(self, request):
        serializer = UpdateCalendarActiveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "요청 데이터가 유효하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        calendar_id = serializer.validated_data["calendar_id"]
        is_active = serializer.validated_data["is_active"]

        try:
            subscription = Subscription.objects.get(
                calendar_id=calendar_id, user_id=request.user
            )
            subscription.is_active = is_active
            subscription.save()

            return Response(
                {"message": "캘린더 활성화 상태가 성공적으로 변경되었습니다."},
                status=status.HTTP_200_OK,
            )

        except Subscription.DoesNotExist:
            return Response(
                {"error": "해당 구독 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
