import sys
import os
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Electrode.settings')
django.setup()

from resources.models import Card

# Define the suits and card names
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
names = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
short_name = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
cards_created = 0

for suit in suits:
    for index, name in enumerate(names):
        # Skip creating the card if it already exists
        if not Card.objects.filter(suit=suit, name=name).exists():
            # Determine the short name and suit initial
            card_short_name = short_name[index]
            suit_initial = suit[0].upper()

            # Handle the case for 10
            if card_short_name == '10':
                card_short_name = '0'

            # Create the code
            code = f'{card_short_name}{suit_initial}'

            # Create the Card object with the code
            Card.objects.create(
                suit=suit,
                name=name,
                short_name=short_name[index],
                code=code,
            )
            cards_created += 1

print(f'Successfully created {cards_created} cards.')
