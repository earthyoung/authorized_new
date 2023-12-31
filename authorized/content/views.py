import jwt, os, requests
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from account.permissions import *
from rest_framework.permissions import IsAuthenticated, AllowAny


BASE_URI = os.environ.get("HOST")


# Create your views here.


class PostViewSet(ModelViewSet):
    queryset = Post.manager.all()
    permission_classes = [AllowAny, IsWriter]

    def check_permissions(self, request):
        if request.method != "GET":
            self.permission_denied(request)

    def check_object_permissions(self, request, obj):
        if request.method != "POST":
            self.permission_denied(request)


class MyPostViewSet(RetrieveModelMixin, GenericViewSet):
    queryset = Post.manager.all()
    permission_classes = [IsAuthenticated]


class GroupPostViewSet(ListModelMixin, GenericViewSet):
    queryset = Post.manager.all()
    permission_classes = [IsGroupUser]
