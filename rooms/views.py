from django.forms import ValidationError
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.models import Profile
from .models import GameRoom
from .serializers import GameRoomSerializer, JoinGameRoomSerializer
from rest_framework.views import APIView


class GameRoomCreateView(generics.CreateAPIView):
    queryset = GameRoom.objects.all()
    serializer_class = GameRoomSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        profile = Profile.objects.get(user=self.request.user)
        serializer.save(created_by=profile)

class JoinGameRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = JoinGameRoomSerializer(data=request.data)
        if serializer.is_valid():
            game_room = serializer.validated_data['game_room']
            profile = Profile.objects.get(user=request.user)
            game_room.players.add(profile)

            # Serialize the game room with the new player added
            game_room_serializer = GameRoomSerializer(game_room)

            return Response(game_room_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetGameRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, unique_id):
        passkey = request.query_params.get('passkey')

        if not passkey:
            raise ValidationError("Passkey is required")

        try:
            # Validate unique_id and passkey
            game_room = GameRoom.objects.get(unique_id=unique_id, passkey=passkey)
        except GameRoom.DoesNotExist:
            return Response({"error": "Invalid unique_id or passkey"}, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the room data with full user info
        serializer = GameRoomSerializer(game_room)
        return Response(serializer.data, status=status.HTTP_200_OK)