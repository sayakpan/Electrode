# twenty_nine/urls.py

from django.urls import path
from django.urls import path
from .views import (
    GameProfileAPIView,
    GetGameStatusAPIView,
    PlaceBidAPIView,
    StartGameAPIView,
    StartBiddingAPIView,
    DistributeRemainingCardsAPIView,
    PlayCardAPIView,
    EndRoundAPIView,
    CheckGameStatusAPIView
)

urlpatterns = [
    path('profile/', GameProfileAPIView.as_view(), name='profile'),
    path('start/<slug:room_id>/', StartGameAPIView.as_view(), name='start_game'),
    path('get-game/<int:instance_id>/',GetGameStatusAPIView.as_view(), name='get_game'),
    path('bid/<int:instance_id>/', StartBiddingAPIView.as_view(), name='bid'),
    path('bidding/place/<int:instance_id>/', PlaceBidAPIView.as_view(), name='place_bid'),
    path('distribute_cards/<int:instance_id>/', DistributeRemainingCardsAPIView.as_view(), name='distribute_cards'),
    path('play_card/<int:instance_id>/<int:player_id>/', PlayCardAPIView.as_view(), name='play_card'),
    path('end_round/<int:instance_id>/', EndRoundAPIView.as_view(), name='end_round'),
    path('status/<int:instance_id>/', CheckGameStatusAPIView.as_view(), name='check_game_status'),
]

