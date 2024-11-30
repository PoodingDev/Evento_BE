from django.contrib import admin

from favorite_event.models import FavoriteEvent


@admin.register(FavoriteEvent)
class FavoriteEventAdmin(admin.ModelAdmin):
    list_display = (
        "favorite_event_id",
        "user_id",
        "event_id",
        "d_day",
        "easy_insidebar",
    )

