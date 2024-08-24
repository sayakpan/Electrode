from django.contrib import admin
from .models import GameProfile

@admin.register(GameProfile)
class GameProfileAdmin(admin.ModelAdmin):
    list_display = ['name']
