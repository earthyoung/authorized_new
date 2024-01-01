from django.db import models
from account.models import *


class PostManager(models.Manager):
    def filter_user(user):
        return Post.objects.filter(group__member=user)


# Create your models here.
class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


class Post(TimeStamp):
    name = models.CharField(max_length=100, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    objects = PostManager()


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    url = models.CharField(max_length=255)


class Comment(TimeStamp):
    content = models.TextField(null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)


class CommentImage(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    url = models.CharField(max_length=255)
