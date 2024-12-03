from django.test import TestCase

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Event
from calendars.models import Calendar

User = get_user_model()


class EventAPITestCase(APITestCase):
    def setUp(self):
        # 테스트 사용자 및 캘린더 생성
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword"
        )
        self.calendar = Calendar.objects.create(
            calendar_id=1,
            name="Test Calendar",
            description="Test Description",
            is_public=True,
            creator=self.user,
        )
        self.event_data = {
            "calendar_id": self.calendar,
            "title": "Test Event",
            "description": "This is a test event",
            "start_time": "2024-01-01T12:00:00Z",
            "end_time": "2024-01-01T14:00:00Z",
            "admin_id": self.user,
        }
        self.event = Event.objects.create(**self.event_data)
        self.client.login(username="testuser", password="testpassword")
        self.base_url = "/api/events/"

    def test_create_event(self):
        """이벤트 생성 테스트"""
        data = {
            "calendar_id": self.calendar.id,
            "title": "New Event",
            "description": "This is a new event",
            "start_time": "2024-02-01T12:00:00Z",
            "end_time": "2024-02-01T14:00:00Z",
        }
        response = self.client.post(self.base_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], data['title'])

    def test_read_event(self):
        """이벤트 조회 테스트"""
        response = self.client.get(f"{self.base_url}{self.event.event_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.event.title)

    def test_update_event(self):
        """이벤트 수정 테스트"""
        update_data = {"title": "Updated Event Title"}
        response = self.client.patch(f"{self.base_url}{self.event.event_id}/", update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], update_data['title'])

    def test_delete_event(self):
        """이벤트 삭제 테스트"""
        response = self.client.delete(f"{self.base_url}{self.event.event_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(event_id=self.event.event_id).exists())
