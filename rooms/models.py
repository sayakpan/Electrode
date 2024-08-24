# models.py
from django.db import models
from django.conf import settings
import string
import random

def generate_unique_id(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_passkey(length=6):
    return ''.join(random.choices(string.digits, k=length))

class GameRoom(models.Model):
    unique_id = models.CharField(max_length=8, unique=True, default=generate_unique_id, null=True)
    passkey = models.CharField(max_length=6, default=generate_passkey, null=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_rooms', on_delete=models.CASCADE)
    players = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='game_rooms')
    game_playing = models.OneToOneField('twenty_nine.GameProfile', on_delete=models.DO_NOTHING, null=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Game Room'
        verbose_name_plural = 'Game Rooms'
