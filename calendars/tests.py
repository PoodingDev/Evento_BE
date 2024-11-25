from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from calendars.models import Calendar
from django.contrib.auth.models import User

# Create your tests here.

class CalendarAPITestCase(TestCase):
    def setUp(self):
        # 테스트 사용자 생성
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client = APIClient()

        # 사용자 인증 설정
        self.client.login(username="testuser", password="testpassword")

        # 초기 캘린더 데이터
        self.calendar_data = {
            "name": "Work Calendar",
            "description": "Calendar for work-related events",
            "is_public": True,
            "owner": self.user.id,
        }

        # 캘린더 생성
        self.calendar = Calendar.objects.create(**self.calendar_data)

    def test_create_calendar(self):
        """캘린더 생성 테스트"""
        data = {
            "name": "Personal Calendar",
            "description": "My personal calendar",
            "is_public": False,
            "owner": self.user.id,
        }
        response = self.client.post('/calendars/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], "Personal Calendar")

    def test_get_calendars(self):
        """캘린더 목록 조회 테스트"""
        response = self.client.get('/calendars/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_calendar(self):
        """캘린더 수정 테스트"""
        update_data = {
            "name": "Updated Calendar",
            "description": "Updated description",
            "is_public": True,
        }
        response = self.client.put(f'/calendars/{self.calendar.id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Updated Calendar")

    def test_delete_calendar(self):
        """캘린더 삭제 테스트"""
        response = self.client.delete(f'/calendars/{self.calendar.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
