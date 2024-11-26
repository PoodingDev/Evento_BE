from django.db import models

# Create your models here.
class Event(models.Model):
    calendar = models.ForeignKey('calendars.Calendar', on_delete=models.CASCADE, related_name='events', null=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    is_all_day = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




    def __str__(self):
        return self.title