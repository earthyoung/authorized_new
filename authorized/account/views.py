import os, requests, jwt
from django.shortcuts import redirect
from rest_framework.views import APIView
from json.decoder import JSONDecodeError
from django.http import JsonResponse
from rest_framework import status
from .models import *
from .serializers import *
from .dto import *
from datetime import datetime, timedelta
from django.core.cache import cache
from .exception import *


BASE_URI = "http://localhost:8000/"
GOOGLE_CALLBACK_URI = BASE_URI + "account/google/callback/"
KAKAO_CALLBACK_URI = BASE_URI + "account/kakao/callback/"


def get_user(request):
    try:
        user = request.user
    except Exception:
        pass
    return user


class HealthView(APIView):
    def get(self, request):
        return JsonResponse({"status": True})


class UserView(APIView):
    def get(self, request):
        user = get_user(request)
        data = UserSerializer(user).data
        return JsonResponse({"status": True, "user": data})


class GoogleLoginView(APIView):
    def get(self, request):
        scope = "https://www.googleapis.com/auth/userinfo.email"
        client_id = os.environ.get("GOOGLE_CLIENT_ID")
        url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}"
        return redirect(url)


class GoogleCallbackView(APIView):
    def get(self, request):
        client_id = os.environ.get("GOOGLE_CLIENT_ID")
        client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
        code = request.GET.get("code")
        state = os.environ.get("STATE")
        token_req = requests.post(
            f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}"
        )
        token_req_json = token_req.json()
        error = token_req_json.get("error")
        if error is not None:
            raise JSONDecodeError(error)
        access_token = token_req_json.get("access_token")

        email_req = requests.get(
            f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
        )
        email_req_status = email_req.status_code
        if email_req_status != 200:
            return JsonResponse(
                {"err_msg": "failed to get email"}, status=status.HTTP_400_BAD_REQUEST
            )
        email_req_json = email_req.json()
        email = email_req_json.get("email")
        user_id = email_req_json.get("user_id")

        # Signin or Signup
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            username = f"{email}_{user_id}"
            user = User.signup_manager.create_google_user(
                email=email, user_id=user_id, username=username
            )

        # Generate JWT token
        secret = os.environ.get("SECRET_KEY")
        access_token_data = OAuthJwtDto(
            id=user.id,
            user_id=user_id,
            expire_at=(datetime.now() + timedelta(days=1)).strftime("%Y%m%dT%H:%M:%S"),
            auth_type="google",
        )
        refresh_token_data = OAuthJwtDto(
            id=user.id,
            user_id=user_id,
            expire_At=(datetime.now() + timedelta(days=30)).strftime("%Y%m%dT%H:%M:%S"),
            auth_type="google",
        )
        access_token = jwt.encode(access_token_data, secret, algorithm="HS256")
        refresh_token = jwt.encode(refresh_token_data, secret, algorithm="HS256")
        cache.set(user.id, refresh_token, timeout=None)
        user_data = UserSerializer(user).data
        return JsonResponse(
            {
                "access_token": access_token,
                "user": user_data,
                "refresh_token": refresh_token,
            }
        )


class KakaoLoginView(APIView):
    def get(self, request):
        client_id = os.environ.get("KAKAO_REST_API_KEY")
        redirect_uri = KAKAO_CALLBACK_URI
        url = f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
        return redirect(url)


class KakaoCallbackView(APIView):
    def get(self, request):
        if request.GET.get("error"):
            return JsonResponse({"status": "error"})
        code = request.GET.get("code")
        access_token_request_uri = "https://kauth.kakao.com/oauth/token"
        header = {"Content-type": "application/x-www-form-urlencoded"}
        client_id = os.environ.get("KAKAO_REST_API_KEY")
        body = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "redirect_uri": KAKAO_CALLBACK_URI,
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

        secret = os.environ.get("SECRET_KEY")
        access_token_data = OAuthJwtDto(
            id=user.id,
            user_id=user_id,
            expire_at=(datetime.now() + timedelta(days=1)).strftime("%Y%m%dT%H:%M:%S"),
            auth_type="kakao",
        )
        refresh_token_data = OAuthJwtDto(
            id=user.id,
            user_id=user_id,
            expire_At=(datetime.now() + timedelta(days=30)).strftime("%Y%m%dT%H:%M:%S"),
            auth_type="kakao",
        )
        access_token = jwt.encode(access_token_data, secret, algorithm="HS256")
        refresh_token = jwt.encode(refresh_token_data, secret, algorithm="HS256")
        cache.set(user.id, refresh_token, timeout=None)
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
