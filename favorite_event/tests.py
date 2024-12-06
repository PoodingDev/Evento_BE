import uuid  # uuid 모듈 임포트
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from event.models import Calendar, Event
from favorite_event.models import FavoriteEvent
from user.models import User


class FavoriteEventTests(APITestCase):
    def setUp(self):
        # 테스트용 사용자 생성
        self.user = User.objects.create_user(
            email="test@test.com",
            username="testuser",
            birth=timezone.now(),
            password="testpass123",
            nickname="테스트유저",
        )

        # 다른 테스트용 사용자 생성
        self.other_user = User.objects.create_user(
            email="other@test.com",
            username="otheruser",
            birth=timezone.now(),
            password="testpass123",
            nickname="다른유저",
        )

        # 테스트용 캘린더 생성
        self.calendar = Calendar.objects.create(
            calendar_id=1,  # 정수로 설정
            name="테스트캘린더",
            description="테스트설명",
            is_public=True,
            color="#000000",
            creator=self.user,
        )

        # 테스트용 이벤트 생성
        self.event = Event.objects.create(
            event_id=uuid.uuid4(),  # UUID로 생성
            title="테스트이벤트",
            description="테스트설명",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(days=1),
            calendar_id=self.calendar,
            admin_id=self.user,
        )

        # 클라이언트 인증
        self.client.force_authenticate(user=self.user)

    def test_get_favorite_events(self):
        # 즐겨찾기 목록 조회 테스트
        # 즐겨찾기 생성
        FavoriteEvent.objects.create(user_id=self.user, event_id=self.event)

        url = reverse("favorites:favorite-list", kwargs={"user_id": self.user.user_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("favorite_events", response.data)
        self.assertEqual(len(response.data["favorite_events"]), 1)
        self.assertEqual(
            response.data["favorite_events"][0]["event_title"], "테스트이벤트"
        )

    def test_create_favorite(self):
        # 즐겨찾기 생성 테스트
        url = reverse("favorites:favorite-list", kwargs={"user_id": self.user.user_id})
        data = {"event_id": self.event.event_id}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FavoriteEvent.objects.count(), 1)
        self.assertEqual(int(response.data["event_id"]), int(self.event.event_id))

    def test_delete_favorite(self):
        # 즐겨찾기 삭제 테스트
        # 먼저 즐겨찾기 생성
        favorite_event = FavoriteEvent.objects.create(
            user_id=self.user, event_id=self.event
        )

        url = reverse(
            "favorites:favorite-delete",
            kwargs={"user_id": self.user.user_id, "event_id": self.event.event_id},
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FavoriteEvent.objects.count(), 0)

    def test_delete_nonexistent_favorite(self):
        # 존재하지 않는 즐겨찾기 삭제 테스트
        url = reverse(
            "favorites:favorite-delete",
            kwargs={
                "user_id": self.user.user_id,
                "event_id": uuid.uuid4(),
            },  # UUID 사용
        )
        response = self.client.delete(url)

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )  # 존재하지 않는 경우 404 응답 확인

    def test_get_nonexistent_user(self):
        # 존재하지 않는 사용자의 즐겨찾기 조회 테스트
        # 슈퍼유저로 변경하여 권한 문제 해결
        self.user.is_superuser = True
        self.user.save()

        # 존재하지 않는 사용자 ID로 수정
        url = reverse("favorites:favorite-list", kwargs={"user_id": 999})  # 숫자로 변경
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "사용자 없음")

    def test_unauthorized_access(self):
        # 권한 없는 접근 테스트
        # 일반 사용자로 변경
        self.user.is_superuser = False
        self.user.save()

        # 다른 사용자의 즐겨찾기 목록 접근 시도
        url = reverse(
            "favorites:favorite-list", kwargs={"user_id": self.other_user.user_id}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 다른 사용자의 즐겨찾기 삭제 시도
        url = reverse(
            "favorites:favorite-delete",
            kwargs={
                "user_id": self.other_user.user_id,
                "event_id": self.event.event_id,  # UUID 사용
            },
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_duplicate_favorite(self):
        # 중복 즐겨찾기 생성 시도 테스트
        # 첫 번째 즐겨찾기 생성
        FavoriteEvent.objects.create(user_id=self.user, event_id=self.event)

        # 중복 생성 시도
        url = reverse("favorites:favorite-list", kwargs={"user_id": self.user.user_id})
        data = {"event_id": self.event.event_id}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "중복 등록")
