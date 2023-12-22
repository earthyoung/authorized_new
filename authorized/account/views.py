import os, requests, jwt, base64, json
from django.shortcuts import redirect
from rest_framework.views import APIView
from json.decoder import JSONDecodeError
from django.http import JsonResponse
from rest_framework import status, viewsets, mixins
from .models import *
from .serializers import *
from .permissions import IsGroupUser
from .dto import *
from datetime import datetime, timedelta
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated, AllowAny
from .exception import *
from rest_framework.throttling import UserRateThrottle
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.response import Response


BASE_URI = os.environ.get("HOST")
GOOGLE_CALLBACK_URI = BASE_URI + "account/google/callback/"
KAKAO_CALLBACK_URI = BASE_URI + "account/kakao/callback/"


def get_user(request):
    try:
        user = request.user
    except Exception:
        pass
    return user


def get_access_token_and_refresh_token(id, user_id, oauth_provider):
    secret = os.environ.get("SECRET_KEY")
    access_token_data = OAuthJwtDto(
        id=id,
        user_id=user_id,
        expire_at=(datetime.now() + timedelta(days=1)).strftime("%Y%m%dT%H:%M:%S"),
        auth_type=oauth_provider,
    )
    refresh_token_data = OAuthJwtDto(
        id=id,
        user_id=user_id,
        expire_At=(datetime.now() + timedelta(days=30)).strftime("%Y%m%dT%H:%M:%S"),
        auth_type=oauth_provider,
    )
    access_token = jwt.encode(access_token_data, secret, algorithm="HS256")
    refresh_token = jwt.encode(refresh_token_data, secret, algorithm="HS256")
    cache.set(id, refresh_token, timeout=None)
    return access_token, refresh_token


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return JsonResponse({"status": True})


class UserViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def retrieve(self, request):
        try:
            user = get_user(request)
            data = UserSerializer(user).data
        except Exception as e:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={"status": False, "msg": str(e)},
            )
        return JsonResponse({"status": True, "user": data})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = get_user(request)
            cache.delete(key=user.id)
        except Exception as e:
            return JsonResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data={"status": False, "msg": str(e)},
            )
        return JsonResponse(status=status.HTTP_200_OK, data={"status": True})


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]
    secret = os.environ.get("SECRET_KEY")

    def post(self, request):
        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            raise JwtNotExistException()
        token = token[7:]
        user_info = jwt.decode(token, self.secret, algorithms=["HS256"])
        try:
            id = user_info.get("id")
            user_id = user_info.get("user_id")
            expire_at = user_info.get("expire_at")
            auth_type = user_info.get("auth_type")
        except Exception:
            raise JwtInvalidException()

        try:
            user = User.objects.get(pk=id)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            raise JwtInvalidException()

        # 기간이 지났는지 확인
        expire_at = datetime.strptime(expire_at, "%Y%m%dT%H:%M:%S")
        if expire_at >= datetime.now():
            return JsonResponse(
                status=status.HTTP_400_BAD_REQUEST, data={"msg": "정상적인 접근입니다."}
            )

        refresh_token = request.data.get("refresh_token")
        refresh_token_from_cache = cache.get(user.id)
        if (not refresh_token_from_cache) or refresh_token_from_cache != refresh_token:
            raise RefreshTokenInvalidException()

        access_token, refresh_token = get_access_token_and_refresh_token(
            user.id, user_id, auth_type
        )
        user_data = UserSerializer(user).data
        return JsonResponse(
            {
                "access_token": access_token,
                "user": user_data,
                "refresh_token": refresh_token,
            }
        )
