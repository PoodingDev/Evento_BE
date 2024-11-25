from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Event

class EventAPITestCase(APITestCase):
    def setUp(self):
        # 초기 데이터 설정
        self.event_data = {
            "title": "Test Event",
            "description": "This is a test event",
            "start_time": "2024-01-01T12:00:00",
            "end_time": "2024-01-01T14:00:00",
            "location": "Test Location"
        }
        self.event = Event.objects.create(**self.event_data)
        self.base_url = "/api/events/"

    def test_create_event(self):
        # Create 테스트
        response = self.client.post(self.base_url, self.event_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], self.event_data['title'])

    def test_read_event(self):
        # Read 테스트
        response = self.client.get(f"{self.base_url}{self.event.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.event.title)

    def test_update_event(self):
        # Update 테스트
        updated_data = {"title": "Updated Event Title"}
        response = self.client.put(f"{self.base_url}{self.event.id}/", updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], updated_data['title'])

    def test_delete_event(self):
        # Delete 테스트
        response = self.client.delete(f"{self.base_url}{self.event.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())

# Create your tests here.
