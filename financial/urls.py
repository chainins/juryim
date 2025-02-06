from django.urls import path
from . import views

app_name = 'financial'

urlpatterns = [
    path('dashboard/', 
         views.FinancialViews.dashboard, 
         name='dashboard'),
         
    path('transactions/', 
         views.FinancialViews.transaction_history, 
         name='transactions'),
         
    path('withdrawal/', 
         views.FinancialViews.withdrawal, 
         name='withdrawal'),
         
    path('withdrawal/<int:withdrawal_id>/status/', 
         views.FinancialViews.withdrawal_status, 
         name='withdrawal_status'),
         
    path('deposit/', 
         views.FinancialViews.deposit, 
         name='deposit'),
         
    path('balance/', 
         views.FinancialViews.get_balance, 
         name='get_balance'),
] 