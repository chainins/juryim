from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import (
    FinancialAccount, Transaction, WithdrawalRequest,
    DepositAddress, PaymentProvider
)

class FinancialService:
    @staticmethod
    @transaction.atomic
    def create_transaction(account, transaction_type, amount, fee=Decimal('0'), 
                          reference_id='', description='', metadata=None):
        """Create a new financial transaction"""
        transaction = Transaction.objects.create(
            account=account,
            transaction_type=transaction_type,
            amount=amount,
            fee=fee,
            reference_id=reference_id,
            description=description,
            metadata=metadata or {}
        )
        
        # Update account balance based on transaction type
        if transaction_type in ['deposit', 'bet_win', 'refund']:
            account.balance += amount
        elif transaction_type in ['withdrawal', 'bet_loss', 'fee']:
            account.balance -= amount
            
        if transaction_type == 'deposit':
            account.total_deposited += amount
        elif transaction_type == 'withdrawal':
            account.total_withdrawn += amount
            
        account.save()
        return transaction

    @staticmethod
    @transaction.atomic
    def process_withdrawal(withdrawal_request):
        """Process a withdrawal request"""
        if withdrawal_request.status != 'pending':
            raise ValueError("Invalid withdrawal status")
            
        account = withdrawal_request.account
        total_amount = withdrawal_request.amount + withdrawal_request.fee
        
        if account.balance < total_amount:
            raise ValueError("Insufficient funds")
            
        withdrawal_request.status = 'processing'
        withdrawal_request.save()
        
        # Create withdrawal transaction
        FinancialService.create_transaction(
            account=account,
            transaction_type='withdrawal',
            amount=withdrawal_request.amount,
            fee=withdrawal_request.fee,
            reference_id=f'WD-{withdrawal_request.id}',
            description=f'Withdrawal to {withdrawal_request.address}'
        )
        
        return withdrawal_request

    @staticmethod
    def get_deposit_address(account, network):
        """Get or create deposit address for user"""
        address, created = DepositAddress.objects.get_or_create(
            account=account,
            network=network,
            defaults={'is_active': True}
        )
        return address

    @staticmethod
    def get_account_balance(user):
        """Get user's available and total balance"""
        account = FinancialAccount.objects.get(user=user)
        return {
            'available': account.balance,
            'frozen': account.frozen_balance,
            'total': account.balance + account.frozen_balance
        }

    @staticmethod
    def get_transaction_history(account, transaction_type=None):
        """Get transaction history for account"""
        transactions = Transaction.objects.filter(account=account)
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
        return transactions

    @staticmethod
    def get_withdrawal_history(account):
        """Get withdrawal history for account"""
        return WithdrawalRequest.objects.filter(account=account)

    @staticmethod
    def calculate_withdrawal_fee(amount, provider):
        """Calculate withdrawal fee based on provider"""
        fee_percentage = provider.fee_percentage
        fee = (amount * fee_percentage / Decimal('100')).quantize(Decimal('0.00000001'))
        return max(fee, provider.min_amount)

    @staticmethod
    @transaction.atomic
    def freeze_balance(account, amount):
        """Freeze balance for pending operations"""
        if account.balance < amount:
            return False
            
        account.balance -= amount
        account.frozen_balance += amount
        account.save()
        return True

    @staticmethod
    @transaction.atomic
    def unfreeze_balance(account, amount):
        """Unfreeze previously frozen balance"""
        if account.frozen_balance < amount:
            return False
            
        account.frozen_balance -= amount
        account.balance += amount
        account.save()
        return True 