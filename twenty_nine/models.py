from accounts.models import Profile
from django.db import models
from resources.models import Card
from rooms.models import GameRoom

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

class CardConfiguration(models.Model):
    game = models.ForeignKey(GameProfile,on_delete=models.CASCADE,related_name='card_configuration')
    card = models.ForeignKey(Card,on_delete=models.DO_NOTHING)
    point = models.IntegerField(default=0, null=True, blank=True)
    power = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return f'{self.card} - {self.point} Point - {self.game}'
    
    class Meta:
        verbose_name = 'Card Configuration'
        verbose_name_plural = 'Card Configurations'


class Instances(models.Model):
    game = models.ForeignKey(GameProfile,on_delete=models.CASCADE,related_name='instance')
    room = models.ForeignKey(GameRoom, on_delete=models.DO_NOTHING)
    team_1 = models.ManyToManyField(Profile,related_name='team_1', blank=True)
    team_2 = models.ManyToManyField(Profile,related_name='team_2', blank=True)
    team_1_points = models.IntegerField(default=0, null=True, blank=True)
    team_2_points = models.IntegerField(default=0, null=True, blank=True)
    team_1_status = models.CharField(max_length=255, null=True, blank=True)
    team_2_status = models.CharField(max_length=255, null=True, blank=True)
    bid_won_by = models.ForeignKey(Profile, related_name='won_bid',on_delete=models.CASCADE, null=True, blank=True)
    highest_bid = models.IntegerField(default=16, null=True, blank=True)
    last_round_started_from = models.ForeignKey(Profile,on_delete=models.CASCADE, null=True, blank=True)
    trump_card = models.ForeignKey(Card,on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'Instance {self.id} - {self.game} {self.room}'
    
class Bid(models.Model):
    instance = models.ForeignKey(Instances, related_name='game_bid', on_delete=models.CASCADE)
    current_bidder = models.ForeignKey(Profile,on_delete=models.CASCADE, related_name="current", null=True, blank=True)
    next_bidder = models.ForeignKey(Profile,on_delete=models.CASCADE, related_name="next", null=True, blank=True)
    bid_winner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    points_bid = models.IntegerField(default=16, null=True, blank=True)

    def __str__(self):
        return f"Bid of {self.points_bid} in Instance {self.instance.id}"
    
class PlayerHand(models.Model):
    instance = models.ForeignKey(Instances, on_delete=models.CASCADE, related_name='hands')
    player = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='player_hand')
    cards_in_hand = models.ManyToManyField(CardConfiguration, related_name='cards_in_hand', blank=True)
    cards_played = models.ManyToManyField(CardConfiguration, related_name='cards_played', blank=True)
    order = models.IntegerField(null=True, blank=True)

    def play_card(self, card):
        """Move a card from cards_in_hand to cards_played."""
        if card in self.cards_in_hand.all():
            self.cards_in_hand.remove(card)
            self.cards_played.add(card)
            return True
        return False

    def __str__(self):
        return f"{self.player}'s Hand"


class GameFlow(models.Model):
    instance = models.ForeignKey(Instances, on_delete=models.CASCADE, related_name='gameflow')
    trick_number = models.IntegerField(default=0, null=True, blank=True)
    hand_status = models.CharField(max_length=10, choices=[('Active', 'Active'), ('Played', 'Played')], default='Active', null=True, blank=True)
    points_taken = models.IntegerField(default=0, null=True, blank=True)
    cards_thrown = models.JSONField(null=True, blank=True)  # This field tracks cards thrown in each trick
    won_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='hand')
    won_by_team = models.CharField(max_length=10, null=True, blank=True)

    def throw_card(self, player, card):
        """Update the cards thrown in the current game flow."""
        player_hand = PlayerHand.objects.get(instance=self.instance, player=player)
        if player_hand.play_card(card):
            # Add the card to the cards_thrown for tracking purposes
            if not self.cards_thrown:
                self.cards_thrown = {}
            self.cards_thrown[player.id] = str(card)
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.instance} - Trick {self.trick_number}"

