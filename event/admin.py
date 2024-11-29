from django.contrib import admin

from event.models import Event

# Register your models here.
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'title', 'start_time', 'end_time', 'calendar_id', 'admin_id')