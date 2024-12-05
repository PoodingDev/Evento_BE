from drf_spectacular.utils import extend_schema
from rest_framework.filters import SearchFilter
from rest_framework.generics import (
    DestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.models import User
from .models import Calendar, Subscription
from .serializers import CalendarSerializer, SubscriptionSerializer

class CalendarListCreateAPIView(ListCreateAPIView):
    """
    캘린더 목록 조회 및 생성
    """

    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]  # 인증 없이 접근 가능

    @extend_schema(
        summary="캘린더 목록 조회",
        description="현재 사용자가 생성한 캘린더 목록을 반환합니다.",
        responses={200: CalendarSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="캘린더 생성",
        description="새로운 캘린더를 생성합니다.",
        request=CalendarSerializer,
        responses={201: CalendarSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # 현재 사용자가 생성한 캘린더만 조회
            return self.queryset.filter(creator=self.request.user)
        return Calendar.objects.none()  # 인증되지 않은 경우 빈 쿼리셋 반환

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            # 캘린더 생성 시 요청 사용자를 소유자로 설정
            serializer.save(creator=self.request.user)

class CalendarRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    캘린더 상세 조회, 수정, 삭제
    """

    queryset = Calendar.objects.all()
    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]  # 인증 없이 접근 가능

    @extend_schema(
        summary="캘린더 상세 조회",
        description="특정 캘린더의 세부 정보를 반환합니다.",
        responses={200: CalendarSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="캘린더 수정",
        description="특정 캘린더의 정보를 수정합니다.",
        request=CalendarSerializer,
        responses={200: CalendarSerializer},
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
            # 현재 사용자가 생성한 캘린더만 접근 가능
            return self.queryset.filter(creator=self.request.user)
        return Calendar.objects.none()

class SubscriptionListCreateAPIView(ListCreateAPIView):
    """
    구독한 캘린더 조회 및 구독 추가
    """

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]  # 인증 없이 접근 가능

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
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # 현재 사용자가 구독한 캘린더 목록 반환
            return Subscription.objects.filter(user=self.request.user)
        return Subscription.objects.none()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            # 구독 생성 시 요청 사용자를 설정
            serializer.save(user=self.request.user)

class SubscriptionDeleteAPIView(DestroyAPIView):
    """
    구독 삭제
    """

    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]  # 인증 없이 접근 가능

    @extend_schema(
        summary="구독 삭제",
        description="특정 캘린더 구독을 삭제합니다.",
        responses={204: None},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # 현재 사용자가 구독한 캘린더만 삭제 가능
            return Subscription.objects.filter(user=self.request.user)
        return Subscription.objects.none()

class CalendarSearchAPIView(ListAPIView):
    """
    공개된 캘린더 검색
    """

    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name", "creator__nickname"]

    @extend_schema(
        summary="공개된 캘린더 검색",
        description="닉네임 또는 캘린더 이름으로 공개된 캘린더를 검색합니다.",
        responses={200: CalendarSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # 공개된 캘린더만 검색 가능
        return Calendar.objects.filter(is_public=True)

class AdminCalendarsAPIView(ListAPIView):
    """
    관리 권한이 있는 캘린더 목록 조회
    """

    serializer_class = CalendarSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]  # 인증 없이 접근 가능

    @extend_schema(
        summary="관리 권한이 있는 캘린더 조회",
        description="현재 사용자가 관리할 수 있는 캘린더를 반환합니다.",
        responses={200: CalendarSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # 사용자가 관리자인 캘린더만 반환
            return Calendar.objects.filter(creator=self.request.user)
        return Calendar.objects.none()

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
        responses={
            200: {
                "description": "관리자 추가 성공",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "캘린더의 관리자로 성공적으로 추가되었습니다.",
                            "calendar": {
                                "calendar_id": 1,
                                "name": "Test Calendar",
                                "description": "테스트 캘린더입니다.",
                                "is_public": True,
                                "color": "#FFFFFF",
                                "creator": 1,
                                "invitation_code": "ABC123",
                            },
                        }
                    }
                },
            },
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

    def get_queryset(self):
        calendar_id = self.kwargs.get("pk")
        if calendar_id:
            # 특정 캘린더에 속한 구독 사용자 조회
            return Subscription.objects.filter(calendar_id=calendar_id)
        return Subscription.objects.none()


class AdminInvitationView(APIView):
    """
    초대 코드를 통해 캘린더의 관리자로 추가하는 View
    """

    permission_classes = [IsAuthenticated]

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
        responses={
            200: {
                "description": "관리자 추가 성공",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "캘린더의 관리자로 성공적으로 추가되었습니다.",
                            "calendar": {
                                "calendar_id": 1,
                                "name": "Test Calendar",
                                "description": "테스트 캘린더입니다.",
                                "is_public": True,
                                "color": "#FFFFFF",
                                "creator": 1,
                                "invitation_code": "ABC123",
                            },
                        }
                    }
                },
            },
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
        invitation_code = request.data.get("invitation_code")
        if not invitation_code:
            return Response(
                {"error": "초대 코드를 입력하세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 초대 코드에 해당하는 캘린더 찾기
            calendar = Calendar.objects.get(invitation_code=invitation_code)
        except Calendar.DoesNotExist:
            return Response(
                {"error": "유효하지 않은 초대 코드입니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user = request.user

        # 생성자가 이미 관리자 상태인 경우 처리
        if user == calendar.creator:
            return Response(
                {"error": "캘린더 생성자는 이미 관리자입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 이미 관리자인지 확인
        if calendar in user.created_calendars.all():
            return Response(
                {"message": "이미 해당 캘린더의 관리자입니다."},
                status=status.HTTP_200_OK,
            )

        # 관리자로 추가
        user.created_calendars.add(calendar)
        return Response(
            {
                "message": f"{calendar.name} 캘린더의 관리자로 성공적으로 추가되었습니다.",
                "calendar": CalendarSerializer(calendar).data,
            },
            status=status.HTTP_200_OK,
        )