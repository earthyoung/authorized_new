from .views import *
from django.urls import path


urlpatterns = [
    path("post/me/", MyPostView.as_view()),
    path(
        "post/<int:pk>",
        PostViewSet.as_view(
            {"get": "retrieve", "patch": "update", "delete": "destroy"}
        ),
    ),
    path(
        "post/",
        PostViewSet.as_view(
            {
                "post": "create",
            }
        ),
    ),
    path("post/group/", GroupPostViewSet.as_view({"get": "list"})),
]
