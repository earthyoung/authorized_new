from .views import *
from django.urls import path

urlpatterns = [
    path("google/login/", GoogleLoginView.as_view()),
    path("google/callback/", GoogleCallbackView.as_view()),
]
