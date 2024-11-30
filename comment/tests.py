from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from comment.models import Comment
from event.models import Calendar, Event
from user.models import User


class CommentTests(APITestCase):
    def setUp(self):
        # 테스트용 관리자 생성
        self.admin = User.objects.create_user(
            user_id="testadmin",
            email="testadmin@test.com",
            username="testadmin",
            birth=timezone.now(),
            password="testpass123",
            nickname="테스트관리자",
        )
        self.admin.is_staff = True
        self.admin.save()

        self.client.force_authenticate(user=self.admin)

        # 테스트용 캘린더 생성
        self.calendar = Calendar.objects.create(
            calendar_id=1,
            name="테스트캘린더",
            description="테스트설명",
            is_public=True,
            color="#000000",
            creator=self.admin,
        )

        # 테스트용 이벤트 생성
        self.event = Event.objects.create(
            event_id=1,
            title="테스트이벤트",
            description="테스트설명",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(days=1),
            calendar_id=self.calendar,
            admin_id=self.admin,
        )

        # 테스트용 댓글 생성
        self.comment = Comment.objects.create(
            content="테스트댓글", event_id=self.event, admin_id=self.admin
        )

    def test_create_comment(self):
        """댓글 생성 테스트"""
        url = reverse(
            "comment:comment-list-create", kwargs={"event_id": self.event.event_id}
        )
        data = {"content": "새로운 댓글"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(response.data["content"], "새로운 댓글")
        self.assertEqual(response.data["admin_nickname"], "테스트관리자")

    def test_get_comment_list(self):
        """댓글 목록 조회 테스트"""
        url = reverse(
            "comment:comment-list-create", kwargs={"event_id": self.event.event_id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("comments", response.data)
        self.assertEqual(len(response.data["comments"]), 1)
        self.assertEqual(response.data["comments"][0]["content"], "테스트댓글")

    def test_update_comment(self):
        """댓글 수정 테스트"""
        url = reverse(
            "comment:comment-detail",
            kwargs={
                "event_id": self.event.event_id,
                "comment_id": self.comment.comment_id,
            },
        )
        data = {"content": "수정된 댓글"}

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "수정된 댓글")

    def test_delete_comment(self):
        """댓글 삭제 테스트"""
        url = reverse(
            "comment:comment-detail",
            kwargs={
                "event_id": self.event.event_id,
                "comment_id": self.comment.comment_id,
            },
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_get_nonexistent_event(self):
        """존재하지 않는 이벤트의 댓글 조회 테스트"""
        url = reverse("comment:comment-list-create", kwargs={"event_id": 999})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "이벤트 없음")

    def test_unauthorized_user_cannot_access(self):
        """권한 없는 사용자 접근 테스트"""
        # 권한 없는 일반 사용자 생성
        normal_user = User.objects.create_user(
            user_id="normaluser",
            email="normal@test.com",
            username="normaluser",
            birth=timezone.now(),
            password="testpass123",
            nickname="일반사용자",
        )
        self.client.force_authenticate(user=normal_user)

        url = reverse(
            "comment:comment-list-create", kwargs={"event_id": self.event.event_id}
        )

        # GET 요청 테스트
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "권한 없음")

        # POST 요청 테스트
        data = {"content": "새로운 댓글"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["error"], "권한 없음")
