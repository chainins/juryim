from django.urls import path
from financial.views import dashboard, deposit, withdraw, transactions

app_name = 'financial'

urlpatterns = [
    path('dashboard/', dashboard, name='financial_dashboard'),
    path('deposit/', deposit, name='deposit'),
    path('withdraw/', withdraw, name='withdraw'),
    path('transactions/', transactions, name='transactions'),
] 