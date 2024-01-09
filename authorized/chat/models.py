from django.db import models
from account.models import User


class Channel(models.Model):
    members = models.ManyToManyField(User)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        ordering = ["-id"]


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    content = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-id"]
