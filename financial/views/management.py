from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from ..models import FinancialAccount, WithdrawalRequest

class AccountManagementView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'financial.manage_accounts'
    model = FinancialAccount
    template_name = 'financial/management/account_list.html'

class WithdrawalManagementView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'financial.manage_withdrawals'
    model = WithdrawalRequest
    template_name = 'financial/management/withdrawal_list.html' 