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
        fields = ["name", "content", "user_id", "group_id"]

    def to_internal_value(self, data):
        for key in data.keys():
            if key not in self.Meta.fields:
                raise Exception("invalid key in PostCreateSerializer")
        return data

    def create(self, validated_data):
        user, group = None, None
        if user_id := validated_data.get("user_id"):
            user = User.objects.get(pk=user_id)

        if group_id := validated_data.get("group_id"):
            group = Group.objects.get(pk=group_id)

        name = validated_data.get("name")
        content = validated_data.get("content")
        post = Post.objects.create(name=name, content=content, user=user, group=group)
        post.save()
        return post


class PostDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id"]
