from django.contrib import admin

from user.models import User


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "user_id",
        "username",
        "email",
        "nickname",
        "is_active",
        "is_staff",
        "is_superuser",
    )
