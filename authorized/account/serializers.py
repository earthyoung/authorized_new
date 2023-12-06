from rest_framework import serializers
from account.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "provider"]


class GroupSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "type", "name"]


class GroupSerializer(serializers.ModelSerializer):
    member = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ["id", "type", "name", "member"]
