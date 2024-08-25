# twenty_nine/views.py

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, views
from utils import get_absolute_url
from .serializers import GameProfileSerializer
from rooms.models import GameRoom
from resources.models import Card
from accounts.models import Profile
from .models import Bid, CardConfiguration, GameFlow, GameProfile, Instances, PlayerHand


class GameProfileAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        games = GameProfile.objects.all()
        serializer = GameProfileSerializer(games, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class StartGameAPIView(views.APIView):
    def post(self, request, room_id):
        game_id = request.data.get('game_id')
        try:
            room = GameRoom.objects.get(unique_id=room_id)
            game = GameProfile.objects.get(id=game_id)
        except GameRoom.DoesNotExist:
            return Response({'error': 'GameRoom not found'}, status=status.HTTP_404_NOT_FOUND)
        except GameProfile.DoesNotExist:
            return Response({'error': 'GameProfile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create Instance
        instance = Instances.objects.create(game=game, room=room)

        # Create PlayerHand objects and distribute 4 cards to each player
        players = room.players.all()  
        for player in players:
            player_hand = PlayerHand.objects.create(instance=instance, player=player)
            cards = CardConfiguration.objects.order_by('?')[:4]  # Get 4 random cards
            player_hand.cards_in_hand.add(*cards)
        
        return Response({
            'message': 'Game started and 4 cards distributed',
            'instance_id': instance.id
        }, status=status.HTTP_201_CREATED)

class GetGameStatusAPIView(views.APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, instance_id):
        try:
            # Get the player's profile from the authenticated user
            player = Profile.objects.get(user=request.user)
            instance = Instances.objects.get(id=instance_id)
            player_hand = PlayerHand.objects.get(instance=instance, player=player)

            # Get details of the game instance
            game_data = {
                'game': instance.game.name,
                'room': instance.room.name,
                'team_1_points': instance.team_1_points,
                'team_2_points': instance.team_2_points,
                'team_1_status': instance.team_1_status,
                'team_2_status': instance.team_2_status,
                'bid': instance.game_bid,
                'bid_won_by': str(instance.bid_won_by),
                'trump_card': self.get_card_details(instance.trump_card) if instance.trump_card else None,
            }

            # Get only the requesting player's cards with full details
            player_cards = {
                'cards_in_hand': [self.get_complete_card_details(request, card) for card in player_hand.cards_in_hand.all()],
                'cards_played': [self.get_complete_card_details(request, card) for card in player_hand.cards_played.all()],
            }

            return Response({
                'game_data': game_data,
                'player_cards': player_cards
            }, status=status.HTTP_200_OK)

        except Instances.DoesNotExist:
            return Response({'error': 'Game instance not found'}, status=status.HTTP_404_NOT_FOUND)
        except PlayerHand.DoesNotExist:
            return Response({'error': 'Player not part of this game'}, status=status.HTTP_404_NOT_FOUND)

    def get_card_details(self, request, card):
        if card:
            return {
                'name': card.name,
                'suit': card.suit,
                'code': card.code,
                'short_name': card.short_name,
                'image_url': get_absolute_url(request, card.image_url) if card.image_url else None,
                'svg_url': get_absolute_url(request, card.svg_url) if card.svg_url else None
            }
        return None
    
    def get_complete_card_details(self, request, card_config):
        if card_config:
            try:
                card = Card.objects.get(id=card_config.card.id)

                return {
                    'suit': card.suit,
                    'name': card.name,
                    'code': card.code,
                    'short_name': card.short_name,
                    'image_url': get_absolute_url(request, card.image_url) if card.image_url else None,
                    'svg_url': get_absolute_url(request, card.svg_url) if card.svg_url else None,
                    'point': card_config.point,
                    'power': card_config.power,
                }
            except CardConfiguration.DoesNotExist:
                return None
        return None

class BidAPIView(views.APIView):
    def post(self, request, instance_id):
        instance = Instances.objects.get(id=instance_id)
        profile = Profile.objects.get(id=request.data['profile_id'])
        points_bid = request.data['points_bid']

        # Create Bid object
        Bid.objects.create(instance=instance, bid_winner=profile, points_bid=points_bid)

        return Response({'message': f'Bid of {points_bid} by {profile}'}, status=status.HTTP_201_CREATED)

class DistributeRemainingCardsAPIView(views.APIView):
    def post(self, request, instance_id):
        instance = Instances.objects.get(id=instance_id)
        for player_hand in instance.hands.all():
            cards = Card.objects.order_by('?')[:4]  # Get 4 random cards
            player_hand.cards_in_hand.add(*cards)
        
        return Response({'message': 'Remaining 4 cards distributed'}, status=status.HTTP_200_OK)

class PlayCardAPIView(views.APIView):
    def post(self, request, instance_id, player_id):
        instance = Instances.objects.get(id=instance_id)
        player = Profile.objects.get(id=player_id)
        card = Card.objects.get(id=request.data['card_id'])

        # Get or create the active GameFlow (trick) object
        gameflow, created = GameFlow.objects.get_or_create(
            instance=instance, hand_status='Active', defaults={'trick_number': 1}
        )

        # Play the card
        success = gameflow.throw_card(player, card)
        
        if success:
            return Response({'message': 'Card played successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Failed to play card'}, status=status.HTTP_400_BAD_REQUEST)

class EndRoundAPIView(views.APIView):
    def post(self, request, instance_id):
        instance = Instances.objects.get(id=instance_id)
        gameflow = instance.gameflow.filter(hand_status='Active').first()
        
        if gameflow:
            # End the current round
            gameflow.hand_status = 'Played'
            gameflow.save()
            
            # Update points and determine if a new round should start
            instance.team_1_points += gameflow.points_taken  # Example
            instance.save()

            if gameflow.trick_number < 8:
                # Start a new GameFlow
                GameFlow.objects.create(instance=instance, trick_number=gameflow.trick_number + 1)
            
            return Response({'message': 'Round ended, points updated'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'No active round found'}, status=status.HTTP_400_BAD_REQUEST)

class EndRoundAPIView(views.APIView):
    def post(self, request, instance_id):
        instance = Instances.objects.get(id=instance_id)
        gameflow = instance.gameflow.filter(hand_status='Active').first()
        
        if gameflow:
            # End the current round
            gameflow.hand_status = 'Played'
            gameflow.save()
            
            # Update points and determine if a new round should start
            instance.team_1_points += gameflow.points_taken  # Example
            instance.save()

            if gameflow.trick_number < 8:
                # Start a new GameFlow
                GameFlow.objects.create(instance=instance, trick_number=gameflow.trick_number + 1)
            
            return Response({'message': 'Round ended, points updated'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'No active round found'}, status=status.HTTP_400_BAD_REQUEST)

class CheckGameStatusAPIView(views.APIView):
    def get(self, request, instance_id):
        instance = Instances.objects.get(id=instance_id)

        # Check if game has ended
        if instance.team_1_points >= instance.game_bid or instance.team_2_points >= instance.game_bid:
            return Response({'winner': 'Team 1' if instance.team_1_points >= instance.game_bid else 'Team 2'}, status=status.HTTP_200_OK)
        
        return Response({'status': 'Game still in progress'}, status=status.HTTP_200_OK)
