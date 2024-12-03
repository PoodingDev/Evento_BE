from django.contrib.auth import get_user_model  # Import 추가
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Calendar, Subscription


class CalendarAPITestCase(TestCase):
    def setUp(self):
        # 테스트용 User 생성
        self.user = get_user_model().objects.create_user(
            username="testuser", email="testuser@example.com", password="testpassword"
        )
        self.client = APIClient()

        # 사용자 인증 설정
        self.client.force_authenticate(user=self.user)

        # 초기 캘린더 데이터
        self.calendar_data = {
            "name": "Work Calendar",
            "description": "Calendar for work-related events",
            "is_public": True,
            "owner": self.user,  # User 인스턴스 전달
        }

        # 캘린더 생성
        self.calendar = Calendar.objects.create(**self.calendar_data)

    def test_create_calendar(self):
        url = reverse("calendar-list-create")
        """캘린더 생성 테스트"""
        data = {
            "name": "Personal Calendar",
            "description": "My personal calendar",
            "is_public": False,
        }
        response = self.client.post("/calendars/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Personal Calendar")

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
        response = self.client.delete(f"/calendars/{self.calendar.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 삭제된 캘린더가 존재하지 않는지 확인
        response = self.client.get(f"/calendars/{self.calendar.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# 캘린더 구독
class SubscriptionAPITestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client = APIClient()
        self.client.login(username="testuser", password="testpassword")

        self.calendar = Calendar.objects.create(
            name="Public Calendar",
            description="Test public calendar",
            is_public=True,
            owner=self.user,
        )

    def test_subscribe_calendar(self):
        """캘린더 구독 테스트"""
        data = {"calendar_id": self.calendar.id}
        response = self.client.post("/subscriptions/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_subscriptions(self):
        """구독한 캘린더 목록 조회 테스트"""
        Subscription.objects.create(user=self.user, calendar=self.calendar)
        response = self.client.get("/subscriptions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_subscription(self):
        """구독 삭제 테스트"""
        subscription = Subscription.objects.create(
            user=self.user, calendar=self.calendar
        )
        response = self.client.delete(f"/subscriptions/{subscription.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
