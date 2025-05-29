import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Electrode.settings')
django.setup()

from resources.models import Card

# Paths to the directories containing the images
back_img = 'cards/back.png'

# Fetch all Card objects
cards = Card.objects.all()

for card in cards:
    code = card.code

    # Check if the files exist
    if os.path.exists(back_img):
        # Open the files in binary mode
        with open(back_img, 'rb') as png_file:
            card.card_back.save(f'{code}_back.png', png_file, save=False)

        card.save()

        print(f'Successfully updated {card.name} of {card.suit} with images.')
    else:
        print(f'Files for {code} not found.')

print("All cards updated!")