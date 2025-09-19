
from rest_framework import serializers

from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'role']
        read_only_fields = ['id']


class CreatePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)