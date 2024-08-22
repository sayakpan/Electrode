from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from rooms.models import GameRoom


class GameProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    last_online = models.DateTimeField(default=timezone.now, null=True, blank=True)
    saved_rooms = models.ManyToManyField(GameRoom, related_name='saved_by', blank=True)

    def __str__(self):
        return f"{self.user.first_name}'s Profile"

    def update_last_online(self):
        self.last_online = timezone.now()
        self.save()
