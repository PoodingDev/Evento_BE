from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from calendars.models import Event
from favorites.models import FavoriteEvent
from django.urls import reverse  # reverse()를 사용하기 위한 임포트

class FavoriteEventApiTest(APITestCase):

    def setUp(self):
        # 테스트용 사용자 생성
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # 테스트용 이벤트 생성
        self.event = Event.objects.create(title='Test Event', start_time='2024-12-01T10:00:00Z')

        # 테스트용 로그인
        self.client.login(username='testuser', password='testpassword')

    def test_create_favorite_event(self):
        """
        즐겨찾기 이벤트를 생성하는 테스트
        """
        url = reverse('favorite-event-add', args=[self.event.id])  # 'favorite-event-add'로 수정

        # POST 요청 보내기
        response = self.client.post(url)

        # 응답 코드가 201 Created인지 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 데이터베이스에 FavoriteEvent가 하나 추가되었는지 확인
        self.assertEqual(FavoriteEvent.objects.count(), 1)
        favorite_event = FavoriteEvent.objects.first()
        self.assertEqual(favorite_event.user, self.user)
        self.assertEqual(favorite_event.event, self.event)

    def test_list_favorite_events(self):
        """
        즐겨찾기된 이벤트 목록을 조회하는 테스트
        """
        # 먼저 즐겨찾기 이벤트를 하나 생성
        FavoriteEvent.objects.create(user=self.user, event=self.event)

        # GET 요청 보내기
        url = reverse('favorite-events-list-create')  # 'favorite-events-list-create'로 수정
        response = self.client.get(url)

        # 응답 코드가 200 OK인지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 데이터 확인
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user'], self.user.id)
        self.assertEqual(data[0]['event'], self.event.id)

    def test_add_favorite_event_already_exists(self):
        """
        이미 즐겨찾기한 이벤트에 대해서 POST 요청 시 400 응답을 확인하는 테스트
        """
        # 이미 즐겨찾기된 이벤트 생성
        FavoriteEvent.objects.create(user=self.user, event=self.event)

        # 이미 즐겨찾기한 이벤트를 다시 추가하려고 시도
        url = reverse('favorite-event-add', args=[self.event.id])  # 'favorite-event-add'로 수정
        response = self.client.post(url)

        # 이미 즐겨찾기한 이벤트일 경우 400 Bad Request를 응답받아야 함
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
