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
        order = request.data.get('order')

        # Check if 'order' array is provided and has the same number of players
        if not order or len(order) != GameRoom.objects.get(unique_id=room_id).players.count():
            return Response({'error': 'Invalid or missing order array'}, status=status.HTTP_400_BAD_REQUEST)
        
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
            try:
                player_order = order.index(player.id)
            except ValueError:
                return Response({'error': f'Player {player.id} not found in order array'}, status=status.HTTP_400_BAD_REQUEST)

            player_hand = PlayerHand.objects.create(instance=instance, player=player,order=player_order)
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

            # Serialize team_1 and team_2 profiles
            team_1_profiles = self.serialize_profiles(instance.team_1.all())
            team_2_profiles = self.serialize_profiles(instance.team_2.all())

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

            # Determine which team the player belongs to
            if player in instance.team_1.all():
                your_team = 'team_1'
                opponent_team = 'team_2'
            elif player in instance.team_2.all():
                your_team = 'team_2'
                opponent_team = 'team_1'
            else:
                your_team = None
                opponent_team = None

            team_info = {
                'your_team': your_team,
                'opponent_team': opponent_team,
                'your_profile': self.serialize_profile(player),
                'team_1': team_1_profiles,
                'team_2': team_2_profiles,
            }

            # Get only the requesting player's cards with full details
            player_cards = {
                'cards_in_hand': [self.get_complete_card_details(request, card) for card in player_hand.cards_in_hand.all()],
                'cards_played': [self.get_complete_card_details(request, card) for card in player_hand.cards_played.all()],
            }

            return Response({
                'game_data': game_data,
                'team_info': team_info,
                'player_cards': player_cards
            }, status=status.HTTP_200_OK)

        except Instances.DoesNotExist:
            return Response({'error': 'Game instance not found'}, status=status.HTTP_404_NOT_FOUND)
        except PlayerHand.DoesNotExist:
            return Response({'error': 'Player not part of this game'}, status=status.HTTP_404_NOT_FOUND)

    def serialize_profiles(self, profiles):
        return [
            {
                'id': profile.id,
                'name': profile.user.first_name,
                'email': profile.user.email,
            }
            for profile in profiles
        ]
    
    def serialize_profile(self, profile):
        return {'id': profile.id,'name': profile.user.first_name,'email': profile.user.email,}
           
    
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

class StartBiddingAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, instance_id):
        try:
            instance = Instances.objects.get(id=instance_id)
            player_hands = PlayerHand.objects.filter(instance=instance).order_by('order')

            # Determine the starting bidder and the next bidder
            if instance.last_round_started_from:
                # Find the player hand of the player who started the last round
                last_starting_hand = PlayerHand.objects.get(instance=instance, player=instance.last_round_started_from)
                # Start bidding from the next player in order
                current_bidder_order = (last_starting_hand.order + 1) % len(player_hands)
            else:
                # If no last round, start bidding from the first player in order
                current_bidder_order = 0

            # Determine the current bidder and the next bidder
            current_bidder_hand = player_hands[current_bidder_order]
            next_bidder_order = (current_bidder_order + 1) % len(player_hands)
            next_bidder_hand = player_hands[next_bidder_order]

            # Set up the first bid
            bid = Bid.objects.create(
                instance=instance,
                current_bidder=current_bidder_hand.player,  # The player who is starting the bid
                next_bidder=next_bidder_hand.player,        # The player who will bid next
                points_bid=0  # Start with 0 or minimum bid
            )

            # Update the instance with the starting bidder and next bidder
            instance.last_round_started_from = current_bidder_hand.player
            instance.save()

            return Response({
                'message': 'Bidding started',
                'current_bidder': current_bidder_hand.player.id,  
                'next_bidder': next_bidder_hand.player.id,
            }, status=status.HTTP_201_CREATED)

        except Instances.DoesNotExist:
            return Response({'error': 'Game instance not found'}, status=status.HTTP_404_NOT_FOUND)
        except PlayerHand.DoesNotExist:
            return Response({'error': 'Player hand not found'}, status=status.HTTP_404_NOT_FOUND)

class PlaceBidAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, instance_id):
        try:
            instance = Instances.objects.get(id=instance_id)
            player_profile = Profile.objects.get(user=request.user)

            # Get the player's current hand
            player_hand = PlayerHand.objects.get(instance=instance, player=player_profile)

            # Get the latest bid
            latest_bid = Bid.objects.filter(instance=instance).last()

            if not latest_bid:
                return Response({'error': 'No active bidding round'}, status=status.HTTP_400_BAD_REQUEST)

            # Extract bid details from request
            bid_points = request.data.get('points_bid')
            if bid_points is not None:
                bid_points = int(bid_points)
            else:
                return Response({'error': 'Bid points not provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the player is the current bidder
            if latest_bid.current_bidder != player_profile :
                return Response({'error': 'Not your turn to bid'}, status=status.HTTP_400_BAD_REQUEST)

            # Handle pass case
            if bid_points == 0:
                # Player passes
                next_bidder_order = (player_hand.order + 1) % len(instance.room.players.all())
                next_bidder_hand = PlayerHand.objects.filter(instance=instance).order_by('order')[next_bidder_order]
                latest_bid.next_bidder = next_bidder_hand.player
                latest_bid.save()

                # Check if all players have passed
                all_passed = not Bid.objects.filter(instance=instance, points_bid__gt=0).exists()
                if all_passed:
                    # End bidding, determine winner
                    winning_bid = Bid.objects.filter(instance=instance).order_by('-points_bid').first()
                    if winning_bid:
                        instance.bid_won_by = winning_bid.bid_winner
                        instance.highest_bid = winning_bid.points_bid
                        instance.save()
                    return Response({'message': 'Bidding ended. Winner determined.'}, status=status.HTTP_200_OK)

                return Response({'message': 'Player passed. Next player is up.'}, status=status.HTTP_200_OK)

            # Validate and update the bid
            if bid_points <= latest_bid.points_bid:
                return Response({'error': 'Bid must be higher than the current bid'}, status=status.HTTP_400_BAD_REQUEST)

            # Update current bid
            latest_bid.points_bid = bid_points
            latest_bid.bid_winner = player_profile
            # latest_bid.next_bidder = PlayerHand.objects.filter(instance=instance).order_by('order')[(player_hand.order + 1) % len(instance.room.players.all())].player
            # Swapping Current and Next after a bid
            current = latest_bid.current_bidder
            latest_bid.current_bidder = latest_bid.next_bidder
            latest_bid.next_bidder = current
            latest_bid.save()

            return Response({
                'message': 'Bid placed successfully',
                'current_bidder': latest_bid.current_bidder.id,
                'next_bidder': latest_bid.next_bidder.id,
                'points_bid': latest_bid.points_bid
            }, status=status.HTTP_200_OK)

        except Instances.DoesNotExist:
            return Response({'error': 'Game instance not found'}, status=status.HTTP_404_NOT_FOUND)
        except PlayerHand.DoesNotExist:
            return Response({'error': 'Player hand not found'}, status=status.HTTP_404_NOT_FOUND)
        except Profile.DoesNotExist:
            return Response({'error': 'Player profile not found'}, status=status.HTTP_404_NOT_FOUND)

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
