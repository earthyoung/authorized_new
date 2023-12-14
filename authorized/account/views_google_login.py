import os, jwt, json
from rest_framework.views import APIView
from rest_framework import status
from .models import *
from .serializers import *
from .dto import *
from datetime import datetime, timedelta
from .exception import *
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.response import Response


class GoogleLoginView(APIView):
    client_id = os.environ.get("GOOGLE_CLIENT_ID")

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
