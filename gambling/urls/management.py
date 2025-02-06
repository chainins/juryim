from django.urls import path
from ..views.management import (
    GameManagementView,
    BetManagementView,
    TransactionManagementView
)

app_name = 'management'

urlpatterns = [
    path('games/', 
         GameManagementView.as_view(), 
         name='games'),
    path('games/<int:pk>/', 
         GameManagementView.as_view(), 
         name='game_detail'),
    path('games/<int:pk>/edit/', 
         GameManagementView.as_view(), 
         name='game_edit'),
    path('bets/', 
         BetManagementView.as_view(), 
         name='bets'),
    path('transactions/', 
         TransactionManagementView.as_view(), 
         name='transactions'),
] 