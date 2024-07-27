from django.db import models
from django.conf import settings

class GameRoom(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_rooms', on_delete=models.CASCADE)
    players = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='game_rooms')
    game_playing = models.OneToOneField('card_games.Game', on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Game Room'
        verbose_name_plural = 'Game Rooms'
