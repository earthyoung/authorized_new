import jwt, os, requests
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from account.permissions import *
from rest_framework.permissions import IsAuthenticated, AllowAny


BASE_URI = os.environ.get("HOST")


# Create your views here.


class PostViewSet(ModelViewSet):
    queryset = Post.objects.order_by("-created_at")
    permission_classes = [AllowAny, IsWriter]
    serializer_class = PostSerializer

    def check_permissions(self, request):
        if request.method not in ["GET", "POST", "DELETE"]:
            self.permission_denied(request)
        super().check_permissions(request)

    def check_object_permissions(self, request, obj):
        if request.method == "GET":
            pass
        else:
            if request.method in ["POST", "PATCH", "PUT", "DELETE"]:
                super().check_object_permissions(request, obj)
            else:
                self.permission_denied(request)

    def create(self, request, *args, **kwargs):
        data = request.data
        data["user_id"] = request.user.id
        serializer = PostCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyPostView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):
        request_user = self.request.user
        return Post.objects.filter(user=request_user)


class GroupPostViewSet(ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        request_user = self.request.user
        groups = Group.objects.filter(members=request_user)
        return Post.objects.filter(group__in=groups)
