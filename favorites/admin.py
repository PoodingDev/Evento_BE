from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import FavoriteEvent

admin.site.register(FavoriteEvent) #관리자가 FavoriteEvent 관리