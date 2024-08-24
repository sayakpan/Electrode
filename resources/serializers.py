# resources/serializers.py

from rest_framework import serializers
from .models import Card

class CardSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    svg_url = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = ['suit', 'name', 'code', 'short_name', 'image_url', 'svg_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image_url.url) if obj.image_url else None

    def get_svg_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.svg_url.url) if obj.svg_url else None