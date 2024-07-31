from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import GameRoom
from .serializers import GameRoomSerializer, JoinGameRoomSerializer
from rest_framework.views import APIView


class GameRoomCreateView(generics.CreateAPIView):
    queryset = GameRoom.objects.all()
    serializer_class = GameRoomSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class JoinGameRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = JoinGameRoomSerializer(data=request.data)
        if serializer.is_valid():
            game_room = serializer.validated_data['game_room']
            game_room.players.add(request.user)
            return Response({'status': 'Player added'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)