from django.urls import path
from ..views.management import (
    AccountManagementView,
    WithdrawalManagementView
)

app_name = 'management'

urlpatterns = [
    path('accounts/', 
         AccountManagementView.as_view(), 
         name='accounts'),
    path('withdrawals/', 
         WithdrawalManagementView.as_view(), 
         name='withdrawals'),
    path('withdrawals/<int:pk>/approve/', 
         WithdrawalManagementView.as_view(), 
         name='approve_withdrawal'),
    path('withdrawals/<int:pk>/reject/', 
         WithdrawalManagementView.as_view(), 
         name='reject_withdrawal'),
] 