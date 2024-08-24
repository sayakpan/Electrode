from django.db import models
from resources.models import Card

# Create your models here.
class GameProfile(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    cover = models.ImageField(upload_to='game_images/', null=True, blank=True)
    players_required = models.IntegerField(default=4, blank=True, null=True)

    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        verbose_name = 'Game Profile'
        verbose_name_plural = 'Game Profiles'