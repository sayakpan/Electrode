from django.http import JsonResponse
from django.views import View
from .models import Card
from .serializers import CardSerializer

class CardListView(View):
    def get(self, request, *args, **kwargs):
        cards = Card.objects.all()
        serializer = CardSerializer(cards, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False)