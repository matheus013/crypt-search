from rest_framework import serializers

from core.models.token import UserToken


class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToken
        fields = ['id', 'user', 'created_at', 'expires_at', 'token']
        read_only_fields = ['user', 'token', 'created_at', 'expires_at']
