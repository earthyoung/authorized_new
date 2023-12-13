import os, requests, jwt, base64, json
from django.shortcuts import redirect
from rest_framework.views import APIView
from json.decoder import JSONDecodeError
from django.http import JsonResponse
from rest_framework import status, viewsets
from .models import *
from .serializers import *
from .dto import *
from datetime import datetime, timedelta
from django.core.cache import cache
from .exception import *
from rest_framework.throttling import UserRateThrottle
from google.oauth2 import id_token

from rest_framework.response import Response


BASE_URI = "http://localhost:8000/"
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
    def get(self, request):
        return JsonResponse({"status": True})


class UserViewSet(viewsets.ModelViewSet):
    def retrieve(self, request):
        user = get_user(request)
        data = UserSerializer(user).data
        return JsonResponse({"status": True, "user": data})


class GoogleLoginView(APIView):
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    from google.auth.transport import requests

    def generate_token(self, data):
        data["provider"] = "google"
        access_token_data = data
        refresh_token_data = data
        access_token_data["expire_at"] = datetime.strftime(
            datetime.now() + timedelta(days=1), "%Y%m%dT%H:%M:%S"
        )
        refresh_token_data["expire_at"] = datetime.strftime(
            datetime.now() + timedelta(weeks=1), "%Y%m%dT%H:%M:%S"
        )
        secret = os.environ.get("SECRET_KEY")
        access_token = jwt.encode(access_token_data, secret, algorithm="HS256")
        refresh_token = jwt.encode(refresh_token_data, secret, algorithm="HS256")
        return access_token, refresh_token

    def create_or_signup_user(self, data):
        email = data.get("email")
        try:
            user = User.objects.get(email=email)
            return user
        except User.DoesNotExist:
            sub = data.get("sub")
            picture = data.get("picture")
            name = data.get("name")
            user = User.signup_manager.create_google_user(email, sub, name, picture)
            return user
        except Exception:
            return None

    def post(self, request):
        data = json.loads(request.body)
        token = data.get("token")
        user_data = None
        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), self.client_id
            )
            user = self.create_or_signup_user(idinfo)
            user_data = UserSerializer(user).data
            access_token, refresh_token = self.generate_token(user_data)
        except Exception as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"status": False, "msg": str(e)},
            )
        return Response(
            status=status.HTTP_200_OK,
            data={
                "user": user_data,
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
        )


class KakaoLoginView(APIView):
    client_id = os.environ.get("KAKAO_REST_API_KEY")
    verify_url = "https://kapi.kakao.com/v1/user/access_token_info"
    info_url = "https://kapi.kakao.com/v2/user/me?property_keys=kakao_account.profile,kakao_account.email,kakao_account.name"

    def generate_token(self, data):
        data["provider"] = "kakao"
        access_token_data = data
        refresh_token_data = data
        access_token_data["expire_at"] = datetime.strftime(
            datetime.now() + timedelta(days=1), "%Y%m%dT%H:%M:%S"
        )
        refresh_token_data["expire_at"] = datetime.strftime(
            datetime.now() + timedelta(weeks=1), "%Y%m%dT%H:%M:%S"
        )
        secret = os.environ.get("SECRET_KEY")
        access_token = jwt.encode(access_token_data, secret, algorithm="HS256")
        refresh_token = jwt.encode(refresh_token_data, secret, algorithm="HS256")
        return access_token, refresh_token

    def create_or_signup_user(self, data):
        email = data.get("email")
        try:
            user = User.objects.get(email=email)
            return user
        except User.DoesNotExist:
            user_id = data.get("id")
            name = data.get("name")
            profile_image_url = data.get("profile").get("profile_image_url")
            user = User.signup_manager.create_kakao_user(
                email, user_id, name, profile_image_url
            )
            return user
        except Exception:
            return None

    def post(self, request):
        access_token = json.loads(request.body)["access_token"]
        try:
            verify_response = requests.get(
                self.verify_url, headers={"Authorization": "Bearer " + access_token}
            )
            if verify_response.status_code != 200:
                raise KakaoAccessTokenInvalidException()
            info_response = requests.get(
                self.verify_url,
                headers={
                    "Authorization": "Bearer " + access_token,
                    "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
                },
            )
            if info_response.status_code != 200:
                raise KakaoAccessTokenInvalidException()
            info_data = info_response.json()
            user = self.create_or_signup_user(info_data)
            user_data = UserSerializer(user).data
            access_token, refresh_token = self.generate_token(user_data)
        except Exception as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"status": False, "msg": str(e)},
            )
        return Response(
            status=status.HTTP_200_OK,
            data={
                "user": user_data,
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
        )


class LogoutView(APIView):
    def post(self, request):
        user = get_user(request)
        if user.is_anonymous:
            return JsonResponse(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "status": False,
                },
            )
        cache.delete(key=user.id)
        return JsonResponse(status=status.HTTP_200_OK, data={"status": True})


class TokenRefreshView(APIView):
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
