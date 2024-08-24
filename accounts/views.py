# accounts/views.py
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from accounts.models import Profile
from .serializers import ProfileSerializer, RegisterSerializer, UserSerializer
from rest_framework.permissions import AllowAny


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        try:
            if serializer.is_valid():
                user = serializer.save()

                # Create Profile for the new user
                profile = Profile.objects.create(user=user, name=user.first_name)

                # Generate or retrieve token for the user
                token, created = Token.objects.get_or_create(user=user)

                # Serialize the user and profile data
                user_data = UserSerializer(user).data
                profile_data = ProfileSerializer(profile).data

                return Response({
                    'token': token.key,
                    'user': user_data,
                    'profile': profile_data
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({'error': 'A user with this username or email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        user_data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }

        profile = Profile.objects.get(user=user)

        profile_data = ProfileSerializer(profile).data

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key, 
            'user': user_data,
            'profile':profile_data,
        }, status=status.HTTP_200_OK)
