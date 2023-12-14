from .views import *
from django.urls import path


urlpatterns = [
    path("all/", AllPostView.as_view()),
    path("me/", MyPostView.as_view()),
    path("group/<int:group_id>/", GroupPostView.as_view()),
    path("post/", PostDetailView.as_view()),
    path("new/", PostCreateView.as_view()),
    path("edit/", PostUpdateView.as_view()),
    path("delete/", PostDestroyView.as_view()),
    path("friends/", FriendListView.as_view(), name="friends"),
    path("consent/", AuthConsentView.as_view(), name="consent"),
]
