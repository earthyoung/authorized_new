from .views import *
from django.urls import path
from rest_framework import routers


router = routers.SimpleRouter()
router.register("post/", PostViewSet)
router.register("post/me/", MyPostViewSet)
router.register("post/group/", GroupPostViewSet)

urlpatterns = router.urls
