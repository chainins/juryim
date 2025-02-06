from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.api import WithdrawalViewSet

router = DefaultRouter()
router.register(r'withdrawals', WithdrawalViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 