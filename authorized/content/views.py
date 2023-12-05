from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny


# Create your views here.
class AllContentView(RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]


class MyContentView(RetrieveAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset)
