from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GamblingGameViewSet, GamblingBetViewSet

router = DefaultRouter()
router.register(r'games', GamblingGameViewSet, basename='game')
router.register(r'bets', GamblingBetViewSet, basename='bet')

app_name = 'gambling-api'

urlpatterns = [
    path('', include(router.urls)),
] 