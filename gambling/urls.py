from django.urls import path
from . import views

app_name = 'gambling'

urlpatterns = [
    path('games/', views.game_list, name='game_list'),
    path('games/<int:game_id>/', views.place_bet, name='place_bet'),
    path('create/', views.create_game, name='create_game'),
    path('bets/', views.user_bets, name='user_bets'),
    path('api/game/<int:game_id>/bet/', views.place_bet_api, name='place_bet_api'),
] 