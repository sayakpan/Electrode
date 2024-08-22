# urls.py
from django.urls import path
from .views import CardListView, GameListAPIView

urlpatterns = [
    path('get-all-cards/', CardListView.as_view(), name='get_all_cards'),
    path('all-card-games/', GameListAPIView.as_view(), name='all-card-game-list'),
]
