from django.urls import path

from comment.views import CommentDetailView, CommentListCreateView

app_name = "comment"

urlpatterns = [
    path("comments/", CommentListCreateView.as_view(), name="comment-list-create"),
    path(
        "comments/<int:comment_id>/", CommentDetailView.as_view(), name="comment-detail"
    ),
]
