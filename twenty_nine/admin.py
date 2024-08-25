from django.contrib import admin
from .models import GameProfile, CardConfiguration, Instances, Bid, PlayerHand, GameFlow

@admin.register(GameProfile)
class GameProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'players_required')

@admin.register(CardConfiguration)
class CardConfigurationAdmin(admin.ModelAdmin):
    list_display = ('game', 'card', 'point', 'power')

@admin.register(Instances)
class InstancesAdmin(admin.ModelAdmin):
    list_display = ('game', 'room', 'team_1_points', 'team_2_points', 'game_bid', 'bid_won_by', 'trump_card')
    filter_horizontal = ['team_1','team_2']
    raw_id_fields = ('game', 'room','bid_won_by')

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('instance', 'bid_winner', 'points_bid')
    raw_id_fields = ('instance',)

@admin.register(PlayerHand)
class PlayerHandAdmin(admin.ModelAdmin):
    list_display = ('instance', 'player')
    filter_horizontal = ['cards_in_hand','cards_played']
    raw_id_fields = ('instance', 'player')

@admin.register(GameFlow)
class GameFlowAdmin(admin.ModelAdmin):
    list_display = ('instance', 'trick_number', 'hand_status', 'points_taken', 'won_by', 'won_by_team')
    raw_id_fields = ('instance', 'won_by')
