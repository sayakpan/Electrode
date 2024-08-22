# accounts/admin.py
from django.contrib import admin
from .models import GameProfile

@admin.register(GameProfile)
class GameProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'last_online') 
    search_fields = ('user__username', 'name')
    list_filter = ('last_online',) 
    filter_horizontal = ['saved_rooms']

    raw_id_fields = ('user',)
