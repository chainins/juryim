from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    FinancialAccount, Transaction, WithdrawalRequest,
    DepositAddress, PaymentProvider, DepositRequest
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
    list_display = ['get_user', 'transaction_type', 'amount', 'status', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['user__username', 'transaction_hash']
    fields = ['user', 'transaction_type', 'amount', 'transaction_hash', 'status', 'created_at']

    def get_user(self, obj):
        return obj.user.username
    get_user.short_description = 'User'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'amount', 'get_wallet_address', 'status', 'created_at', 'get_processed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'wallet_address']
    fields = ['user', 'amount', 'wallet_address', 'transaction_hash', 'status', 'created_at', 'processed_at']

    def get_user(self, obj):
        return obj.user.username
    get_user.short_description = 'User'

    def get_wallet_address(self, obj):
        return obj.wallet_address
    get_wallet_address.short_description = 'Wallet Address'

    def get_processed_at(self, obj):
        return obj.processed_at
    get_processed_at.short_description = 'Processed At'

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data and obj.status == 'approved':
            obj.process_withdrawal()
        super().save_model(request, obj, form, change)

@admin.register(DepositRequest)
class DepositRequestAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'amount', 'status', 'created_at', 'get_processed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'transaction_hash']
    fields = ['user', 'amount', 'transaction_hash', 'status', 'created_at', 'processed_at']

    def get_user(self, obj):
        return obj.user.username
    get_user.short_description = 'User'

    def get_processed_at(self, obj):
        return obj.processed_at
    get_processed_at.short_description = 'Processed At'

    def has_add_permission(self, request):
        return False

@admin.register(DepositAddress)
class DepositAddressAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'account_link', 'network', 'address', 'created_at'
    ]
    list_filter = ['network', 'created_at']
    search_fields = [
        'account__user__username',
        'address'
    ]
    readonly_fields = [
        'account',
        'network',
        'address',
        'created_at'
    ]
    
    def account_link(self, obj):
        url = reverse('admin:users_user_change', args=[obj.account.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.account.user.username)
    account_link.short_description = 'Account'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    actions = ['generate_new_address']

    @admin.action(description='Generate new address for selected accounts')
    def generate_new_address(self, request, queryset):
        from .services import DepositService
        service = DepositService()
        
        success = 0
        for deposit_address in queryset:
            try:
                service.create_deposit_address(
                    deposit_address.account.user,
                    deposit_address.network
                )
                success += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Error generating address for {deposit_address.account.user}: {str(e)}",
                    level='ERROR'
                )
        
        self.message_user(
            request,
            f"Successfully generated {success} new addresses"
        )

@admin.register(PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'provider_type', 'is_active',
        'fee_percentage', 'min_amount', 'max_amount'
    ]
    list_filter = ['provider_type', 'is_active']
    search_fields = ['name', 'provider_type']
    readonly_fields = ['created_at', 'updated_at'] 