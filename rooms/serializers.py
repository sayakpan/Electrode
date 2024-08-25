# serializers.py
from rest_framework import serializers
from accounts.serializers import UserSerializer, ProfileSerializer
from .models import GameRoom
from accounts.models import Profile

class GameRoomSerializer(serializers.ModelSerializer):
    created_by = ProfileSerializer(read_only=True)  # Use UserSerializer to return full user details
    players = ProfileSerializer(many=True, read_only=True)  # Use UserSerializer to return details of players

    class Meta:
        model = GameRoom
        fields = ['id', 'unique_id', 'passkey', 'name', 'created_at', 'created_by', 'players']
        read_only_fields = ['id', 'unique_id', 'passkey', 'created_at', 'created_by', 'players']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user_profile = Profile.objects.get(user=request.user)
            validated_data['created_by'] = user_profile

        game_room = super().create(validated_data)
        
        # Add the creator to the players list
        game_room.players.add(user_profile)
        
        return game_room
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        created_by_id = instance.created_by.id

        # Add "(Admin)" to the created_by player and make sure they are the first in the list
        players = representation['players']
        admin_player = None

        for player in players:
            if player['id'] == created_by_id:
                admin_player = player

        if admin_player:
            admin_player['name'] += ' (Admin)'
            players.remove(admin_player)
            players.insert(0, admin_player)

        return representation

class JoinGameRoomSerializer(serializers.Serializer):
    unique_id = serializers.CharField(max_length=8)
    passkey = serializers.CharField(max_length=6)

    def validate(self, data):
        unique_id = data.get('unique_id')
        passkey = data.get('passkey')

        try:
            game_room = GameRoom.objects.get(unique_id=unique_id, passkey=passkey)
        except GameRoom.DoesNotExist:
            raise serializers.ValidationError("Invalid unique_id or passkey")

        data['game_room'] = game_room
        return data

