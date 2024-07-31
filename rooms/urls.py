# urls.py
from django.urls import path
from .views import GameRoomCreateView, JoinGameRoomView

urlpatterns = [
    path('create/', GameRoomCreateView.as_view(), name='game_room_create'),
    path('join/', JoinGameRoomView.as_view(), name='game_room_join'),
]
