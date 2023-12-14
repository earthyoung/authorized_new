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


class KakaoLoginView(APIView):
    client_id = os.environ.get("KAKAO_REST_API_KEY")
    verify_url = "https://kapi.kakao.com/v1/user/access_token_info"
    info_url = "https://kapi.kakao.com/v2/user/me"

    def generate_token(self, data, access_token, refresh_token):
        data["provider"] = "kakao"
        access_token_data = data
        refresh_token_data = data
        access_token_data["access_token"] = access_token
        refresh_token_data["refresh_token"] = refresh_token
        access_token_data["expire_at"] = datetime.strftime(
            datetime.now() + timedelta(days=1), "%Y%m%dT%H:%M:%S"
        )
        refresh_token_data["expire_at"] = datetime.strftime(
            datetime.now() + timedelta(days=30), "%Y%m%dT%H:%M:%S"
        )
        secret = os.environ.get("SECRET_KEY")
        access_token = jwt.encode(access_token_data, secret, algorithm="HS256")
        refresh_token = jwt.encode(refresh_token_data, secret, algorithm="HS256")
        return access_token, refresh_token

    def create_or_signup_user(self, data):
        email = data.get("kakao_account").get("email")
        try:
            user = User.objects.get(email=email)
            return user
        except User.DoesNotExist:
            user_id = data.get("id")
            name = data.get("properties").get("nickname")
            profile_image_url = data.get("properties").get("profile_image")
            user = User.signup_manager.create_kakao_user(
                email, user_id, name, profile_image_url
            )
            return user
        except Exception:
            return None

    def post(self, request):
        body = json.loads(request.body)
        access_token = body["access_token"]
        refresh_token = body["refresh_token"]
        try:
            verify_response = requests.get(
                self.verify_url, headers={"Authorization": "Bearer " + access_token}
            )
            if verify_response.status_code != 200:
                raise KakaoAccessTokenInvalidException()
            info_response = requests.get(
                self.info_url,
                headers={"Authorization": "Bearer " + access_token},
            )
            if info_response.status_code != 200:
                raise KakaoAccessTokenInvalidException()
            info_data = info_response.json()
            user = self.create_or_signup_user(info_data)
            user_data = UserSerializer(user).data
            new_access_token, new_refresh_token = self.generate_token(
                user_data, access_token, refresh_token
            )
            user_data.pop("access_token")
            user_data.pop("refresh_token")
            user_data.pop("expire_at")
        except Exception as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"status": False, "msg": str(e)},
            )
        return Response(
            status=status.HTTP_200_OK,
            data={
                "user": user_data,
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
            },
        )
