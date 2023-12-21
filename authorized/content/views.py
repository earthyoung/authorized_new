import jwt, os, requests
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny


BASE_URI = os.environ.get("HOST")


# Create your views here.


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()


class MyPostViewSet(RetrieveModelMixin, GenericAPIView):
    queryset = Post.objects.all()


class GroupPostViewSet(ListModelMixin, GenericAPIView):
    queryset = Post.objects.all()
