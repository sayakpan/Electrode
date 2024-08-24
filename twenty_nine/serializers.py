#twenty_nine/serializers.py

from rest_framework import serializers
from .models import GameProfile

class GameProfileSerializer(serializers.ModelSerializer):
    cover = serializers.SerializerMethodField()
    
    class Meta:
        model = GameProfile
        fields = ['id', 'name', 'cover', 'players_required']

    def get_cover(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.cover.url) if obj.cover else None