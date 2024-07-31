# serializers.py
from rest_framework import serializers
from .models import GameRoom

class GameRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameRoom
        fields = ['id', 'unique_id', 'passkey', 'name', 'created_at', 'created_by', 'players', 'game_playing']
        read_only_fields = ['id', 'unique_id', 'passkey', 'created_at', 'created_by', 'players']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            validated_data['created_by'] = user
        game_room = super().create(validated_data)
        game_room.players.add(user)
        return game_room
    
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
