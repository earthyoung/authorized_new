import jwt, os, requests
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.generics import (
    RetrieveAPIView,
    ListAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
)
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny


# Create your views here.
class AllPostView(ListAPIView):
    queryset = Post.manager.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]


class MyPostView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, user):
        return Post.manager.filter_user(user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset(request.user))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GroupPostView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def filter_queryset(self, queryset, group_id):
        qs = super().filter_queryset(queryset)
        return qs.filter(group__id=group_id)

    def list(self, request, group_id, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset(), group_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PostDetailView(RetrieveAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]


class PostCreateView(CreateAPIView):
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]


class PostUpdateView(UpdateAPIView):
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]


class PostDestroyView(DestroyAPIView):
    serializer_class = PostDestroySerializer
    permission_classes = [IsAuthenticated]


class AuthConsentView(APIView):
    def get(self, request):
        return Response({"status": True})


class FriendListView(APIView):
    secret = os.environ.get("SECRET_KEY")
    rest_api_key = os.environ.get("KAKAO_REST_API_KEY")
    redirect_url = "http://localhost:8000/content/consent/"
    # redirect_url = "http://localhost:3000/"
    consent_url = f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={redirect_url}&response_type=code&scope=friends"
    friend_url = "https://kapi.kakao.com/v1/api/talk/friends"

    def get(self, request):
        access_token = request.META.get("HTTP_AUTHORIZATION")[7:]
        access_token_oauth = jwt.decode(
            access_token, self.secret, algorithms="HS256"
        ).get("access_token")
        friend_response = requests.get(
            self.friend_url, headers={"Authorization": "Bearer " + access_token_oauth}
        )
        if friend_response.status_code != 200:
            if friend_response.json().get("code") == -402:
                consent_response = requests.post(self.consent_url)
                friend_response = requests.get(
                    self.friend_url,
                    headers={"Authorization": "Bearer " + access_token_oauth},
                )
            else:
                raise Exception()

        return Response(data={"status": "ok"})
