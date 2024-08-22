from django.http import JsonResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Card, Game
from .serializers import CardSerializer, GameSerializer
from rest_framework.permissions import AllowAny


class CardListView(View):
    def get(self, request, *args, **kwargs):
        cards = Card.objects.all()
        serializer = CardSerializer(cards, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False)
    

class GameListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        games = Game.objects.all()
        serializer = GameSerializer(games, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)