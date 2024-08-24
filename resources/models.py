# resources/models.py

from django.db import models
from django.conf import settings

class Card(models.Model):
    suit = models.CharField(max_length=8, null=True)
    name = models.CharField(max_length=5, null=True)
    code = models.CharField(max_length=2, null=True)
    short_name = models.CharField(max_length=2, null=True)
    image_url = models.ImageField(upload_to='cards/png/', null=True)  # PNG image
    svg_url = models.FileField(upload_to='cards/svg/', null=True)  # SVG file

    def __str__(self):
        return f'{self.name} of {self.suit}'

    class Meta:
        verbose_name = 'Card'
        verbose_name_plural = 'Cards'
        unique_together = ['suit', 'name']