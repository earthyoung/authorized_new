from rest_framework import serializers
from .models import *
from account.serializers import *


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = "__all__"


class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True)
    group = GroupSimpleSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ["id", "name", "content", "images", "user", "group"]


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["name", "content"]


class PostDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id"]
