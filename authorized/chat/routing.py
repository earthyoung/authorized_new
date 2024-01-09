from django.urls import path
from chat.consumers import EchoConsumer

websocket_urlpatterns = [path("ws/echo/", EchoConsumer.as_asgi())]
