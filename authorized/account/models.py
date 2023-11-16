from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class UserSignupManager(models.Manager):
    def create_google_user(self, email, user_id, photo_url=None):
        user = User.objects.create(
            email=email,
            user_id=user_id,
            provider=User.Provider.GOOGLE,
            photo_url=photo_url,
        )
        return user


class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


# Create your models here.
class User(AbstractUser, TimeStamp):
    class Provider(models.TextChoices):
        GOOGLE = "GOOGLE", _("GOOGLE")
        COMMON = "COMMON", _("COMMON")

    email = models.CharField(max_length=255, unique=True)
    photo_url = models.CharField(max_length=255, null=True, blank=True)
    provider = models.CharField(
        max_length=10, choices=Provider.choices, default=Provider.COMMON
    )
    password = models.CharField(max_length=128, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    signup_manager = UserSignupManager()
