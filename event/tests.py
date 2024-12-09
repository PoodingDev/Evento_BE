from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import datetime, timedelta
from django.utils import timezone

from user.models import User
from calendars.models import Calendar
from .models import Event


class EventTests(APITestCase):
    def setUp(self):
        """테스트 데이터 설정"""
        # 테스트 유저 생성
        self.user1 = User.objects.create_user(
            email="test1@test.com",
            password="testpass123",
            nickname="테스트유저1"
        )
        self.user2 = User.objects.create_user(
            email="test2@test.com",
            password="testpass123",
            nickname="테스트유저2"
        )

        # 테스트 캘린더 생성
        self.calendar = Calendar.objects.create(
            name="테스트 캘린더",
            creator=self.user1
        )

        # 기본 이벤트 데이터
        self.event_data = {
            'calendar_id': self.calendar.id,
            'title': '테스트 이벤트',
            'description': '테스트 설명',
            'start_time': timezone.now(),
            'end_time': timezone.now() + timedelta(hours=2),
            'location': '테스트 장소'
        }

        # 인증 설정
        self.client.force_authenticate(user=self.user1)

    def test_create_public_event(self):
        """공개 이벤트 생성 테스트"""
        url = reverse('event-list-create')
        data = {
            **self.event_data,
            'event_type': 'public'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Event.objects.get(event_id=response.data['event_id']).is_public)

    def test_create_private_event(self):
        """비공개 이벤트 생성 테스트"""
        url = reverse('event-list-create')
        data = {
            **self.event_data,
            'event_type': 'private'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(Event.objects.get(event_id=response.data['event_id']).is_public)

    def test_list_public_events(self):
        """공개 이벤트 목록 조회 테스트"""
        # 공개 이벤트 생성
        Event.objects.create(
            **self.event_data,
            is_public=True,
            admin_id=self.user1
        )

        url = reverse('event-list-create')
        response = self.client.get(f'{url}?type=public')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_private_events(self):
        """비공개 이벤트 목록 조회 테스트"""
        # 비공개 이벤트 생성
        Event.objects.create(
            **self.event_data,
            is_public=False,
            admin_id=self.user1
        )

        url = reverse('event-list-create')
        response = self.client.get(f'{url}?type=private')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_other_user_cannot_see_private_events(self):
        """다른 사용자의 비공개 이벤트 접근 제한 테스트"""
        # 비공개 이벤트 생성
        event = Event.objects.create(
            **self.event_data,
            is_public=False,
            admin_id=self.user1
        )

        # 다른 사용자로 인증 변경
        self.client.force_authenticate(user=self.user2)

        # 상세 조회 시도
        url = reverse('event-detail', kwargs={'event_id': event.event_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_event_visibility(self):
        """이벤트 공개 여부 수정 테스트"""
        # 공개 이벤트 생성
        event = Event.objects.create(
            **self.event_data,
            is_public=True,
            admin_id=self.user1
        )

        url = reverse('event-detail', kwargs={'event_id': event.event_id})
        data = {
            **self.event_data,
            'event_type': 'private'
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Event.objects.get(event_id=event.event_id).is_public)

    def test_delete_event(self):
        """이벤트 삭제 테스트"""
        # 이벤트 생성
        event = Event.objects.create(
            **self.event_data,
            is_public=True,
            admin_id=self.user1
        )

        url = reverse('event-detail', kwargs={'event_id': event.event_id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(event_id=event.event_id).exists())

    def test_event_date_validation(self):
        """이벤트 날짜 유효성 검사 테스트"""
        url = reverse('event-list-create')
        data = {
            **self.event_data,
            'event_type': 'public',
            'start_time': timezone.now(),
            'end_time': timezone.now() - timedelta(hours=1)  # 종료 시간이 시작 시간보다 이전
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)