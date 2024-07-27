# populate_cards.py
import sys
import os
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Electrode.settings')
django.setup()

from card_games.models import Card
from card_games.models import GameConfig,Game

def getPriority(short_name):
    rank_map = {
        'J': 1,
        '9': 2,
        'A': 3,
        '10': 4,
        'K': 5,
        'Q': 6,
        '8': 7,
        '7': 8,
    }
    return rank_map.get(short_name, 0)

def getPoints(short_name):
    point_map = {
        'J': 3,
        '9': 2,
        '10': 1,
        'A': 1
    }
    return point_map.get(short_name, 0)

game = Game.objects.get(id=1)

for card in Card.objects.all():
    if not GameConfig.objects.filter(card=card, game=game).exists():
        GameConfig.objects.create(
            card=card,
            game=game,
            priority=getPriority(card.short_name),
            point=getPoints(card.short_name)
        )


