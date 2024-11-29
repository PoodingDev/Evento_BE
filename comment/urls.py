from django.urls import path

from comment.views import CommentDetailView, CommentListCreateView

urlpatterns = [
    path("comments/", CommentListCreateView.as_view(), name="comment-list"),
    path(
        "comments/<int:comment_id>/", CommentDetailView.as_view(), name="comment-detail"
    ),
]
