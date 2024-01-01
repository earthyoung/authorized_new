from .views import *
from django.urls import path
from rest_framework import routers


urlpatterns = [
    path("post/me/", MyPostView.as_view()),
    path(
        "post/",
        PostViewSet.as_view({"get": "list", "post": "create", "patch": "update"}),
    ),
    path("post/group/", GroupPostViewSet.as_view({"get": "list"})),
]
