# twenty_nine/views.py

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import GameProfileSerializer
from twenty_nine.models import GameProfile

class GameProfileAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        games = GameProfile.objects.all()
        serializer = GameProfileSerializer(games, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)