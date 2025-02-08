from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r'ws/management/$',
        consumers.ManagementConsumer.as_asgi()
    ),
    re_path(r'ws/financial/deposit/$', consumers.DepositConsumer.as_asgi()),
    re_path(r'ws/financial/withdrawal/(?P<withdrawal_id>\d+)/$', 
            consumers.WithdrawalConsumer.as_asgi()),
] 