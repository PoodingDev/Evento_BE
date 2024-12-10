from django.db import models, transaction
from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import (
    DestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Calendar, Subscription
from .serializers import (
    AdminCalendarSerializer,
    AdminInvitationSerializer,
    CalendarCreateSerializer,
    CalendarDetailSerializer,
    CalendarSearchResultSerializer,
    CalendarSearchSerializer,
    SubscriptionSerializer, ActiveEventSerializer,
)


class CalendarListCreateAPIView(ListCreateAPIView):
    """
    캘린더 목록 조회 및 생성
    """

    queryset = Calendar.objects.all()
    serializer_class = CalendarCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            # 생성 시 초대 코드 포함 Serializer
            return CalendarCreateSerializer
        # 조회 시 초대 코드 제외 Serializer
        return CalendarDetailSerializer

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

    def perform_create(self, serializer):
        calendar = serializer.save(creator=self.request.user)  # 캘린더 생성


        if self.request.user.is_authenticated:
            # 캘린더 생성 시 요청 사용자를 소유자로 설정
            serializer.save(creator=self.request.user)


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
        summary="캘린더 삭제",
        description="특정 캘린더를 삭제합니다.",
        responses={204: None},
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
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="캘린더 구독 추가",
        description="특정 캘린더를 구독합니다.",
        request=SubscriptionSerializer,
        responses={201: SubscriptionSerializer},
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        calendar_id = request.data.get("calendar_id")

        # 중복 체크
        if Subscription.objects.filter(
            user_id=user.pk, calendar_id=calendar_id
        ).exists():
            return Response(
                {"error": "이미 구독된 캘린더입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Serializer 생성 시 context에 request 추가
        serializer = SubscriptionSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


class AdminCalendarsAPIView(ListAPIView):
    """
    관리 권한이 있는 캘린더 목록 조회
    """

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
                        "calendar": {"$ref": "#/components/schemas/CalendarDetail"},
                    },
                },
            }
        },
    )
    def get(self, request, *args, **kwargs):
        # 관리 권한이 있는 캘린더
        calendars = Calendar.objects.filter(
            Q(creator=request.user) | Q(admins=request.user)
        ).distinct()

        # 응답 데이터 생성
        data = [
            {
                "calendar_id": calendar.calendar_id,
                "name": calendar.name,
                "description": calendar.description,
                "is_public": calendar.is_public,
                "color": calendar.color,
                "invitation_code": calendar.invitation_code,
                "creator_id": calendar.creator_id,  # 생성자의 ID
                "admins": list(
                    calendar.admins.values_list("nickname", flat=True)
                ),  # 관리자 멤버 리스트
            }
            for calendar in calendars
        ]

        return Response(data, status=200)

    # def get_queryset(self):
    #     if self.request.user.is_authenticated:
    #         return Calendar.objects.filter(
    #             # 생성자이거나 관리자로 초대된 캘린더
    #             models.Q(creator=self.request.user) |
    #             models.Q(admins=self.request.user)
    #         ).distinct().select_related('creator')
    #     return Calendar.objects.none()

    def get_queryset(self):
        return Calendar.objects.filter(
            models.Q(creator=self.request.user) | models.Q(admins=self.request.user)
        ).distinct()


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


class ActiveCalendarEventListAPIView(ListAPIView):
    """
    내가 관리자인 is_active 캘린더의 이벤트
    + 내가 구독자인 is_active 공개 캘린더 이벤트
    """
    serializer_class = ActiveEventSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="활성화된 캘린더 이벤트 조회",
        description=
        "1. 사용자가 관리자로 등록된 캘린더 중 is_active=True인 이벤트"
        "2. 사용자가 구독한 캘린더 중 is_active=True, is_public=True인 이벤트를 조회합니다.",
        responses={
            200: OpenApiResponse(
                response=ActiveEventSerializer(many=True),
                description="성공적으로 이벤트 목록을 조회했습니다."
            ),
            401: OpenApiResponse(
                description="인증되지 않은 사용자"
            ),
            403: OpenApiResponse(
                description="권한이 없는 사용자"
            )
        },
        tags=['이벤트']  # 선택적: 스웨거 UI에서 그룹화
    )
    def get_queryset(self):
        # 내가 관리자인 캘린더 (is_active=True)
        admin_calendar_ids = Calendar.objects.filter(
            admins=self.request.user,
            subscriptions__is_active=True  # is_active=True 필터
        ).values_list("id", flat=True)

        # 내가 구독자로 등록된 공개 캘린더 (is_active=True, is_public=True)
        subscribed_calendar_ids = Subscription.objects.filter(
            user=self.request.user,
            is_active=True,
            calendar__is_public=True  # 공개 캘린더만
        ).values_list("calendar_id", flat=True)

        # 이벤트 필터링
        return Event.objects.filter(
            calendar_id__in=admin_calendar_ids.union(subscribed_calendar_ids)
        )
