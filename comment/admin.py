from django.contrib import admin

from comment.models import Comment


# Register your models here.
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "comment_id",
        "content",
        "created_at",
        "updated_at",
        "event_id",
        "admin_id",
    )
