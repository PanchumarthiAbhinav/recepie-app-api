"""Serializers for the user API view"""

from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user object"""
    # confirm_password = serializers.CharField(write_only=True, min_length=5, max_length=10)

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create and return a user with encrypted pwd"""
        return get_user_model().objects.create_user(**validated_data)
