import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Electrode.settings')
django.setup()

from resources.models import Card

# Fetch all Card objects
cards = Card.objects.all()

for card in cards:
    # Determine the short name and suit initial
    short_name = card.short_name
    suit_initial = card.suit[0].upper()

    # Handle the case for 10
    if short_name == '10':
        short_name = '0'

    # Create the code
    card.code = f'{short_name}{suit_initial}'

    # Save the updated card
    card.save()

    # Output success message
    print(f'Successfully updated {card.name} of {card.suit} with code {card.code}')