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
        game_room = serializer.save(created_by=profile)
        profile.active_room_id = game_room.id
        profile.save()

class JoinGameRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = JoinGameRoomSerializer(data=request.data)
        if serializer.is_valid():
            game_room = serializer.validated_data['game_room']
            profile = Profile.objects.get(user=request.user)
            game_room.players.add(profile)

            profile.active_room_id = game_room.id
            profile.save()

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
    
class GetRoomByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        try:
            # Get the profile of the requesting user
            profile = Profile.objects.get(user=request.user)

            # Get the room by ID
            game_room = GameRoom.objects.get(id=room_id)

            # Check if the player is in the room
            if not game_room.players.filter(id=profile.id).exists():
                return Response({"error": "You are not part of this room"}, status=status.HTTP_403_FORBIDDEN)

            # Serialize and return the room details
            serializer = GameRoomSerializer(game_room)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except GameRoom.DoesNotExist:
            return Response({"error": "GameRoom not found"}, status=status.HTTP_404_NOT_FOUND)
        except Profile.DoesNotExist:
            return Response({"error": "Player profile not found"}, status=status.HTTP_404_NOT_FOUND)