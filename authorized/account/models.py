from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class UserSignupManager(models.Manager):
    def create_google_user(self, email, user_id, username, photo_url=None):
        user = User.objects.create(
            email=email,
            user_id=user_id,
            username=username,
            provider=User.Provider.GOOGLE,
            photo_url=photo_url,
        )
        return user

    def create_kakao_user(self, user_id, username):
        user = User.objects.create(
            user_id=user_id,
            username=username,
            provider=User.Provider.KAKAO,
        )
        return user

    def get_by_natural_key(self, username):
        try:
            user = User.objects.get(username)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None
        return user


class GroupManager(models.Manager):
    pass


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
        KAKAO = "KAKAO", _("KAKAO")
        INSTAGRAM = "INSTAGRAM", _("INSTAGRAM")

    email = models.CharField(max_length=255, unique=True)
    photo_url = models.CharField(max_length=255, null=True, blank=True)
    provider = models.CharField(
        max_length=10, choices=Provider.choices, default=Provider.COMMON
    )
    password = models.CharField(max_length=128, null=True, blank=True)
    user_id = models.CharField(max_length=128, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    signup_manager = UserSignupManager()


class Group(TimeStamp):
    class GroupType(models.TextChoices):
        SINGLE = "SINGLE", _("SINGLE")
        MULTIPLE = "MULTIPLE", _("MULTIPLE")

    type = models.CharField(
        max_length=20, choices=GroupType.choices, default=GroupType.SINGLE
    )
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(User, through="MemberShip")
    manager = GroupManager()


class MemberShip(TimeStamp):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
