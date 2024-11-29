from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from calendars.models import Event
from favorites.models import FavoriteEvent


class FavoriteEventApiTest(APITestCase):

    def setUp(self):
        # 테스트용 사용자 및 이벤트 생성
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.event = Event.objects.create(title="Test Event", start_time="2024-12-01T10:00:00Z")

        # 로그인
        self.client.login(username="testuser", password="testpassword")

    def test_create_favorite_event(self):
        """
        즐겨찾기 이벤트를 생성하는 테스트
        """
        url = reverse("favorites:favorite-event-add", args=[self.event.id])  # 'favorite-event-add'를 사용
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FavoriteEvent.objects.count(), 1)

    def test_list_favorite_events(self):
        """
        즐겨찾기된 이벤트 목록을 조회하는 테스트
        """
        # 즐겨찾기 이벤트 생성
        FavoriteEvent.objects.create(user=self.user, event=self.event)

        url = reverse("favorite:favorite-events-list")  # 'favorite-events-list'를 사용
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_favorite_event_already_exists(self):
        """
        이미 즐겨찾기한 이벤트에 대해서 POST 요청 시 400 응답을 확인하는 테스트
        """
        # 이미 즐겨찾기된 이벤트 생성
        FavoriteEvent.objects.create(user=self.user, event=self.event)

        url = reverse("favorite:favorite-event-add", args=[self.event.id])  # 'favorite-event-add'를 사용
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
