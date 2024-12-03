from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

from .models import Calendar, Subscription

User = get_user_model()


class CalendarAPITestCase(APITestCase):
    def setUp(self):
        # 테스트용 User 생성
        self.user = get_user_model().objects.create_user(
            user_id="123456",
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            birth="1990-01-01",
            nickname="Tester"
        )
        self.client = APIClient()

        # 사용자 인증 설정
        self.client.force_authenticate(user=self.user)

        # 캘린더 생성
        self.calendar = Calendar.objects.create(
            calendar_id=1,
            name="Test Calendar",
            description="A calendar for testing",
            is_public=True,
            color="#FF5733",
            creator=self.user
        )
        self.base_url = "/api/calendars/"

    def test_create_calendar(self):
        """캘린더 생성 테스트"""
        url = reverse("calendar-list-create")
        data = {
            "name": "New Test Calendar",
            "description": "A new calendar",
            "is_public": True,
            "color": "#FFFFFF",
        }
        response = self.client.post(self.base_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], data['name'])

    def test_get_calendars(self):
        """캘린더 목록 조회 테스트"""
        response = self.client.get("/calendars/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_calendar(self):
        """캘린더 수정 테스트"""
        update_data = {
            "name": "Updated Calendar",
            "description": "Updated description",
            "is_public": True,
        }
        response = self.client.put(
            f"/calendars/{self.calendar.id}/", update_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Calendar")

    def test_delete_calendar(self):
        """캘린더 삭제 테스트"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"{self.base_url}{self.calendar.calendar_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Calendar.objects.filter(calendar_id=self.calendar.calendar_id).exists())

        # 삭제된 캘린더가 존재하지 않는지 확인
        response = self.client.get(f"/calendars/{self.calendar.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# 캘린더 구독
class SubscriptionAPITestCase(APITestCase):
    def setUp(self):
        # 테스트용 User 및 캘린더 생성
        self.user = get_user_model().objects.create_user(
            user_id="123456",
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            birth="1990-01-01",
            nickname="Tester"
        )
        self.calendar = Calendar.objects.create(
            calendar_id=2,
            name="Subscription Test Calendar",
            description="A calendar for subscription testing",
            is_public=True,
            color="#123456",
            creator=self.user
        )
        self.base_url = "/api/subscriptions/"
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_subscribe_calendar(self):
        """캘린더 구독 테스트"""
        data = {"calendar_id": self.calendar.calendar_id}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.base_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_subscriptions(self):
        """구독한 캘린더 목록 조회 테스트"""
        Subscription.objects.create(user=self.user, calendar=self.calendar)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_delete_subscription(self):
        """구독 삭제 테스트"""
        subscription = Subscription.objects.create(user=self.user, calendar=self.calendar)
        response = self.client.delete(f"{self.base_url}{subscription.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

