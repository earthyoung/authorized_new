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


BASE_URI = "http://localhost:8000/"
GOOGLE_CALLBACK_URI = BASE_URI + "account/google/callback/"


class HealthView(APIView):
    def get(self, request):
        return JsonResponse({"status": True})


# Create your views here.
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
        access_token_data = UserJwtDto(
            id=user.id,
            user_id=user_id,
            email=email,
            expire_at=(datetime.now() + timedelta(days=1)).strftime("%Y%m%dT%H:%M:%S"),
        )
        refresh_token_data = UserJwtDto(
            id=user.id,
            user_id=user_id,
            email=email,
            expire_At=(datetime.now() + timedelta(days=30)).strftime("%Y%m%dT%H:%M:%S"),
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
