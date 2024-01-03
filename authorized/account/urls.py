from .views import *
from .views_kakao_login import *
from .views_google_login import *
from django.urls import path


urlpatterns = [
    path("health/", HealthView.as_view()),
    path("user/", UserViewSet.as_view({"get": "retrieve", "post": "destroy"})),
    path("group/", GroupViewSet.as_view({"get": "list"})),
    path("google/login/", GoogleLoginView.as_view()),
    path("kakao/login/", KakaoLoginView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
    path("logout/", LogoutView.as_view()),
]
