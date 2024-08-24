# resources/urls.py

from django.urls import path
from .views import CardListView

urlpatterns = [
    path('get-all-cards/', CardListView.as_view(), name='get_all_cards'),
]