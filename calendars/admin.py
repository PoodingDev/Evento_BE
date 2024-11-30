from django.contrib import admin

from calendars.models import Calendar


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = (
        "calendar_id",
        "name",
        "description",
        "is_public",
        "color",
        "creator",
    )
