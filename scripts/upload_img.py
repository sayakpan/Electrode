import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Electrode.settings')
django.setup()

from card_games.models import Card

# Paths to the directories containing the images
png_dir = 'cards/png/'
svg_dir = 'cards/svg/'

# Fetch all Card objects
cards = Card.objects.all()

for card in cards:
    code = card.code

    # Construct file paths
    png_path = os.path.join(png_dir, f'{code}.png')
    svg_path = os.path.join(svg_dir, f'{code}.svg')

    # Check if the files exist
    if os.path.exists(png_path) and os.path.exists(svg_path):
        # Open the files in binary mode
        with open(png_path, 'rb') as png_file:
            card.image_url.save(f'{code}.png', png_file, save=False)

        with open(svg_path, 'rb') as svg_file:
            card.svg_url.save(f'{code}.svg', svg_file, save=False)

        # Save the Card object
        card.save()

        print(f'Successfully updated {card.name} of {card.suit} with images.')
    else:
        print(f'Files for {code} not found.')

print("All cards updated!")