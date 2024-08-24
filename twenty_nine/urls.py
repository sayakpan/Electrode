# twenty_nine/urls.py

from django.urls import path
from .views import GameProfileAPIView

urlpatterns = [
    path('profile/', GameProfileAPIView.as_view(), name='profile'),
]
