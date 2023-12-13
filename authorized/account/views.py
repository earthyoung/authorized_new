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
from google.auth.transport import requests
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
    throttle_classes = [UserRateThrottle]

    def retrieve(self, request):
        user = get_user(request)
        data = UserSerializer(user).data
        return JsonResponse({"status": True, "user": data})


class KakaoLoginView(APIView):
    client_id = os.environ.get("KAKAO_REST_API_KEY")
    redirect_uri = KAKAO_CALLBACK_URI

    def get(self, request):
        url = f"https://kauth.kakao.com/oauth/authorize?client_id={self.client_id}&redirect_uri={self.redirect_uri}&response_type=code"
        return redirect(url)


class KakaoCallbackView(APIView):
    client_id = os.environ.get("KAKAO_REST_API_KEY")
    callback_uri = KAKAO_CALLBACK_URI

    def get(self, request):
        if request.GET.get("error"):
            return JsonResponse({"status": "error"})
        code = request.GET.get("code")
        access_token_request_uri = "https://kauth.kakao.com/oauth/token"
        header = {"Content-type": "application/x-www-form-urlencoded"}
        body = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "redirect_uri": self.callback_uri,
            "code": code,
        }
        response = requests.post(
            url=access_token_request_uri, headers=header, data=body
        )
        response_data = response.json()
        access_token = response_data.get("access_token")
        if not access_token:
            raise KakaoNotExistAccessTokenException()
        user_info_request_uri = "https://kapi.kakao.com/v2/user/me"
        header = {
            "Authorization": f"Bearer {access_token}",
            "Content-type": "application/x-www-form-urlencoded",
        }
        response = requests.get(url=user_info_request_uri, headers=header)
        response_data = response.json()
        user_id = response_data.get("id")

        # Signin or Signup
        try:
            user = User.objects.get(username=user_id)
        except User.DoesNotExist:
            user = User.signup_manager.create_kakao_user(
                user_id=user_id, username=user_id
            )

        access_token, refresh_token = get_access_token_and_refresh_token(
            user.id, user_id, "kakao"
        )
        user_data = UserSerializer(user).data
        return JsonResponse(
            {
                "access_token": access_token,
                "user": user_data,
                "refresh_token": refresh_token,
            }
        )


class LogoutView(APIView):
    def post(self, request):
        user = get_user(request)
        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            return JsonResponse(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    "status": "error",
                },
            )
        cache.delete(key=user.id)
        return JsonResponse(status=status.HTTP_200_OK, data={})


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


class GoogleLoginView(APIView):
    client_id = os.environ.get("GOOGLE_CLIENT_ID")

    def post(self, request):
        data = json.loads(request.body)
        token = data.get("token")
        try:
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), self.client_id
            )
        except Exception as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"status": False, "msg": e}
            )
        return JsonResponse(
            {
                "access_token": "12312313123",
                "refresh_token": "456456456",
            }
        )
