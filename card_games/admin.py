from django.contrib import admin
from .models import Game, Card, GameConfig

class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    filter_horizontal = ['game_cards', 'extra_cards']
    list_filter = ['created_at', 'updated_at']

class CardAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'short_name', 'suit']
    search_fields = ['suit']

class GameConfigAdmin(admin.ModelAdmin):
    raw_id_fields = ['card', 'game']
    list_display = ['card', 'game', 'priority', 'point']

admin.site.register(Game, GameAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(GameConfig, GameConfigAdmin)
