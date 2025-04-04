from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from user_notifications import routing
from django.urls import re_path
from financial.consumers import BalanceConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})

websocket_urlpatterns = [
    re_path(r'ws/balance/$', BalanceConsumer.as_asgi()),
] 