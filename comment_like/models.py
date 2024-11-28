from django.db import models


from comment.models import Comment
from user.models import User


class CommentLike(models.Model):
    like_id = models.BigAutoField(primary_key=True)
    comment_id = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

