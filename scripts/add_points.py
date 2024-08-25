import sys
import os
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Electrode.settings')
django.setup()

from resources.models import Card
from twenty_nine.models import CardConfiguration, GameProfile

def get_priority(short_name):
    rank_map = {
        'J': 8,
        '9': 7,
        'A': 6,
        '10': 5,
        'K': 4,
        'Q': 3,
        '8': 2,
        '7': 1,
    }
    return rank_map.get(short_name, 0)

def get_points(short_name):
    point_map = {
        'J': 3,
        '9': 2,
        '10': 1,
        'A': 1
    }
    return point_map.get(short_name, 0)

# Retrieve the game profile
game = GameProfile.objects.get(id=1)

# Get the short names for cards that are present in the rank_map
valid_card_short_names = ['J', '9', 'A', '10', 'K', 'Q', '8', '7']

# Filter and create CardConfiguration only for valid cards
for card in Card.objects.filter(short_name__in=valid_card_short_names):
    if not CardConfiguration.objects.filter(card=card, game=game).exists():
        print(card,game,get_priority(card.short_name),get_points(card.short_name))
        CardConfiguration.objects.create(
            card=card,
            game=game,
            power=get_priority(card.short_name),
            point=get_points(card.short_name)
        )

print("Card configurations populated.")
