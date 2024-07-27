from django.db import models
from django.conf import settings

class Card(models.Model):
    suit = models.CharField(max_length=8, null=True)
    name = models.CharField(max_length=5, null=True)
    short_name = models.CharField(max_length=2, null=True)
    image_url = models.ImageField(upload_to='cards/', null=True)

    def __str__(self):
        return f'{self.name} of {self.suit}'

    class Meta:
        verbose_name = 'Card'
        verbose_name_plural = 'Cards'
        unique_together = ['suit', 'name']


class Game(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    game_state = models.JSONField(default=dict, blank=True, null=True)
    minimum_number_of_players = models.IntegerField(default=0)
    game_cards = models.ManyToManyField(Card, related_name='game_cards')
    extra_cards = models.ManyToManyField(Card, related_name='extra_cards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        verbose_name = 'Game'
        verbose_name_plural = 'Games'


class GameConfig(models.Model):
    card = models.ForeignKey(Card, on_delete=models.DO_NOTHING, null=True)
    game = models.ForeignKey(Game, on_delete=models.DO_NOTHING, null=True)
    priority = models.IntegerField(default=0)
    point = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.card}-{self.game}'
    
    class Meta:
        verbose_name = 'Game Config'
        verbose_name_plural = 'Game Configs'
        unique_together = ['card', 'game']
