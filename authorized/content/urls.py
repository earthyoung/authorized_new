from .views import *
from django.urls import path


urlpatterns = [
    path("all/", AllPostView.as_view()),
    path("me/", MyPostView.as_view()),
    path("group/<int:group_id>/", GroupPostView.as_view()),
]
