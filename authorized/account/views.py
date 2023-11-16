import os, requests
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from json.decoder import JSONDecodeError
from django.http import JsonResponse
from rest_framework import status
from .models import *


BASE_URI = "http://localhost:8000/"
GOOGLE_CALLBACK_URI = BASE_URI + "account/google/callback/"


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

        # Signin or Signup
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user_id = email_req_json.get("user_id")
            user = User.signup_manager.create_google_user(email=email, user_id=user_id)

        # Generate JWT token
        return JsonResponse({"status": True})
