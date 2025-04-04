from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'financial'

urlpatterns = [
    # Account management
    path('account/', views.account_overview, name='account_overview'),
    path('deposit/', views.deposit_request, name='deposit_request'),
    path('withdraw/', views.withdrawal_request, name='withdrawal_request'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('test-balance-update/', views.test_balance_update, name='test_balance_update'),
    
    # Keep any existing URLs...
] 