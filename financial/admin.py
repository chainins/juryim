from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    FinancialAccount, Transaction, WithdrawalRequest,
    DepositAddress, PaymentProvider
)
from .services import FinancialService

@admin.register(FinancialAccount)
class FinancialAccountAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'balance', 'frozen_balance',
        'total_deposited', 'total_withdrawn', 'created_at'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'account_link', 'transaction_type',
        'amount', 'fee', 'status', 'created_at'
    ]
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = [
        'account__user__username',
        'account__user__email',
        'reference_id'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    def account_link(self, obj):
        url = reverse('admin:financial_financialaccount_change', args=[obj.account.id])
        return format_html('<a href="{}">{}</a>', url, obj.account.user.username)
    account_link.short_description = 'Account'

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'account_link', 'amount', 'fee',
        'network', 'status', 'created_at'
    ]
    list_filter = ['status', 'network', 'created_at']
    search_fields = [
        'account__user__username',
        'account__user__email',
        'address',
        'transaction_hash'
    ]
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_withdrawals', 'reject_withdrawals']
    
    def account_link(self, obj):
        url = reverse('admin:financial_financialaccount_change', args=[obj.account.id])
        return format_html('<a href="{}">{}</a>', url, obj.account.user.username)
    account_link.short_description = 'Account'
    
    def approve_withdrawals(self, request, queryset):
        for withdrawal in queryset.filter(status='pending'):
            try:
                withdrawal.status = 'processing'
                withdrawal.save()
                # Add admin note
                withdrawal.admin_notes += f'\nApproved by {request.user} at {timezone.now()}'
                withdrawal.save()
            except Exception as e:
                self.message_user(request, f'Error approving withdrawal {withdrawal.id}: {str(e)}')
    approve_withdrawals.short_description = 'Approve selected withdrawals'
    
    def reject_withdrawals(self, request, queryset):
        for withdrawal in queryset.filter(status='pending'):
            try:
                withdrawal.status = 'cancelled'
                withdrawal.save()
                # Add admin note
                withdrawal.admin_notes += f'\nRejected by {request.user} at {timezone.now()}'
                withdrawal.save()
                # Refund the amount
                FinancialService.create_transaction(
                    account=withdrawal.account,
                    transaction_type='refund',
                    amount=withdrawal.amount + withdrawal.fee,
                    description=f'Refund for rejected withdrawal #{withdrawal.id}'
                )
            except Exception as e:
                self.message_user(request, f'Error rejecting withdrawal {withdrawal.id}: {str(e)}')
    reject_withdrawals.short_description = 'Reject selected withdrawals'

@admin.register(DepositAddress)
class DepositAddressAdmin(admin.ModelAdmin):
    list_display = [
        'address', 'account_link', 'network',
        'is_active', 'created_at', 'last_used'
    ]
    list_filter = ['network', 'is_active', 'created_at']
    search_fields = [
        'account__user__username',
        'account__user__email',
        'address'
    ]
    readonly_fields = ['created_at']
    
    def account_link(self, obj):
        url = reverse('admin:financial_financialaccount_change', args=[obj.account.id])
        return format_html('<a href="{}">{}</a>', url, obj.account.user.username)
    account_link.short_description = 'Account'

@admin.register(PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'provider_type', 'is_active',
        'fee_percentage', 'min_amount', 'max_amount'
    ]
    list_filter = ['provider_type', 'is_active']
    search_fields = ['name', 'provider_type']
    readonly_fields = ['created_at', 'updated_at'] 