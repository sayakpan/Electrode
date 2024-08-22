# urls.py
from django.urls import path
from .views import GameRoomCreateView, GetGameRoomView, JoinGameRoomView

urlpatterns = [
    path('create/', GameRoomCreateView.as_view(), name='game_room_create'),
    path('join/', JoinGameRoomView.as_view(), name='game_room_join'),
    path('<str:unique_id>/', GetGameRoomView.as_view(), name='get_game_room'),
]
