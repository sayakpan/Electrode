# accounts/serializers.py
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import GameProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name']

class GameProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameProfile
        fields = ['name', 'image', 'last_online', 'saved_rooms']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)  # Make sure first_name is provided

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name']  # Save first_name
        )
        # Create a token for the new user
        Token.objects.create(user=user)
        return user
