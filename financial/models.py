from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

class FinancialAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0'))
    frozen_balance = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0'))
    total_deposited = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0'))
    total_withdrawn = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'financial_accounts'

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('bet_win', 'Bet Win'),
        ('bet_loss', 'Bet Loss'),
        ('fee', 'Fee'),
        ('refund', 'Refund'),
        ('adjustment', 'Manual Adjustment')
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    )

    account = models.ForeignKey('FinancialAccount', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    fee = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference_id = models.CharField(max_length=100, blank=True)  # External reference
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.account.user.username} - {self.transaction_type} - {self.amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Send balance update through WebSocket if transaction is completed
        if self.status == 'completed':
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_balance_{self.account.user.id}',
                {
                    'type': 'balance_update',
                    'balance': str(self.account.user.balance)
                }
            )

class WithdrawalRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    )

    NETWORK_CHOICES = (
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'USDT-TRC20'),
        ('BSC', 'Binance Smart Chain'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        null=True,  # Allow null temporarily for migration
        blank=True
    )
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    address = models.CharField(max_length=100)
    network = models.CharField(max_length=10, choices=NETWORK_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown'} - {self.amount} {self.network}"
    
    def process_withdrawal(self):
        if self.status == 'approved' and not self.processed_at:
            # Add withdrawal processing logic here
            self.processed_at = timezone.now()
            self.save()

class DepositAddress(models.Model):
    account = models.ForeignKey(FinancialAccount, on_delete=models.CASCADE)
    address = models.CharField(max_length=100, unique=True)
    network = models.CharField(max_length=50)
    label = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'deposit_addresses'
        unique_together = ['account', 'network']

class PaymentProvider(models.Model):
    name = models.CharField(max_length=100)
    provider_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    config = models.JSONField(default=dict)
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'))
    min_amount = models.DecimalField(max_digits=18, decimal_places=8)
    max_amount = models.DecimalField(max_digits=18, decimal_places=8)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_providers'

class DepositRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    transaction_hash = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"
    
    def process_deposit(self):
        if self.status == 'approved' and not self.processed_at:
            # Add deposit processing logic here
            self.processed_at = timezone.now()
            self.save() 