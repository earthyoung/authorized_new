from .views import *
from django.urls import path


urlpatterns = [
    path("health/", HealthView.as_view()),
    path("user/", UserViewSet.as_view({"get": "retrieve", "post": "destroy"})),
    path("google/login/", GoogleLoginView.as_view()),
    path("google/callback/", GoogleCallbackView.as_view()),
    path("kakao/login/", KakaoLoginView.as_view()),
    path("kakao/callback/", KakaoCallbackView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
]
