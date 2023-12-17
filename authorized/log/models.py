from django.db import models
from account.models import User, Group


# Create your models here.
class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        abstract = True


class Channel(models.Model):
    members = models.ManyToManyField(User)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    content = models.TextField(null=True, blank=True)


class EmailLog(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="sender"
    )
    receiver = models.ManyToManyField(User, related_name="receiver")
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
