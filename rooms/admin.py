from django.contrib import admin
from .models import GameRoom

class GameRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'created_by']
    filter_horizontal = ['players']
    search_fields = ['name', 'created_by__username']
    list_filter = ['created_at']

admin.site.register(GameRoom, GameRoomAdmin)
