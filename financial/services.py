from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import (
    FinancialAccount, Transaction, WithdrawalRequest,
    DepositAddress, PaymentProvider
)
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .blockchain import BlockchainAPI

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

class SecurityService:
    @staticmethod
    def validate_withdrawal(account, amount):
        """Validate if a withdrawal request is secure"""
        if amount <= 0:
            return False, "Invalid withdrawal amount"
            
        if amount > account.balance:
            return False, "Insufficient balance"
            
        # Check withdrawal limits
        daily_withdrawals = Transaction.objects.filter(
            account=account,
            transaction_type='withdrawal',
            created_at__date=timezone.now().date()
        ).count()
        
        if daily_withdrawals >= settings.MAX_DAILY_WITHDRAWALS:
            return False, "Daily withdrawal limit exceeded"
            
        return True, "Withdrawal validated"
    
    @staticmethod
    def check_account_security(account):
        """Check if account meets security requirements"""
        user = account.user
        
        if not user.email_verified:
            return False, "Email not verified"
            
        if not user.phone_verified:
            return False, "Phone not verified"
            
        # Add more security checks as needed
        return True, "Account security verified"
    
    @staticmethod
    def validate_transaction(account, amount, transaction_type):
        """Validate if a transaction is secure"""
        if amount <= 0:
            return False, "Invalid transaction amount"
            
        if transaction_type == 'withdrawal' and amount > account.balance:
            return False, "Insufficient balance"
            
        # Add more transaction validations
        return True, "Transaction validated"

class DepositService:
    def __init__(self):
        self.blockchain = BlockchainAPI()

    def create_deposit_address(self, user, network):
        """Create a new deposit address for user"""
        try:
            # Generate address using blockchain API
            address = self.blockchain.generate_deposit_address(network)
            
            # Create deposit address record
            deposit_address = DepositAddress.objects.create(
                account=user.financialaccount,
                network=network,
                address=address,
                min_deposit=settings.MIN_DEPOSIT[network],
                confirmations_required=settings.CONFIRMATIONS_REQUIRED[network]
            )
            
            return deposit_address
            
        except Exception as e:
            print(f"Error creating deposit address: {str(e)}")
            raise

    def check_deposit_confirmations(self, deposit):
        """Check deposit confirmations using blockchain API"""
        try:
            if deposit.network == 'BTC':
                confirmations = self.blockchain.get_btc_confirmations(deposit.transaction_hash)
            elif deposit.network == 'ETH':
                confirmations = self.blockchain.get_eth_confirmations(deposit.transaction_hash)
            elif deposit.network == 'USDT':
                confirmations = self.blockchain.get_usdt_confirmations(deposit.transaction_hash)
            else:
                raise ValueError(f"Unsupported network: {deposit.network}")
            
            return confirmations
            
        except Exception as e:
            print(f"Error checking confirmations: {str(e)}")
            return 0

    @staticmethod
    def notify_deposit_update(deposit):
        """Send deposit update notification through WebSocket"""
        channel_layer = get_channel_layer()
        
        # Prepare deposit data for notification
        deposit_data = {
            'id': deposit.id,
            'amount': str(deposit.amount),
            'network': deposit.network,
            'status': deposit.status,
            'confirmations': deposit.confirmations,
            'created_at': deposit.created_at.isoformat(),
        }
        
        # Send to user's deposit update group
        async_to_sync(channel_layer.group_send)(
            f"deposit_updates_{deposit.account.user.id}",
            {
                'type': 'deposit_update',
                'data': deposit_data
            }
        )
    
    @staticmethod
    def process_deposit_confirmation(deposit, confirmations):
        """Process deposit confirmation update"""
        deposit.confirmations = confirmations
        
        # Check if deposit is confirmed
        if confirmations >= settings.CONFIRMATIONS_REQUIRED[deposit.network]:
            deposit.status = 'completed'
            deposit.account.balance += deposit.amount
            deposit.account.save()
        
        deposit.save()
        DepositService.notify_deposit_update(deposit)

class WithdrawalService:
    def __init__(self):
        self.blockchain = BlockchainAPI()

    def create_withdrawal_request(self, user, network, amount, address):
        """Create a new withdrawal request"""
        try:
            # Validate withdrawal amount
            min_amount = Decimal(settings.MIN_DEPOSIT[network])
            if amount < min_amount:
                raise ValueError(f"Minimum withdrawal amount is {min_amount} {network}")

            # Calculate fee
            fee = Decimal(settings.NETWORK_FEES[network])
            total_amount = amount + fee

            # Check user balance
            if user.financialaccount.balance < total_amount:
                raise ValueError("Insufficient balance")

            # Create withdrawal request
            withdrawal = WithdrawalRequest.objects.create(
                account=user.financialaccount,
                network=network,
                amount=amount,
                fee=fee,
                address=address,
                status='pending'
            )

            # Freeze the withdrawal amount
            user.financialaccount.balance -= total_amount
            user.financialaccount.frozen_balance += total_amount
            user.financialaccount.save()

            return withdrawal

        except Exception as e:
            print(f"Error creating withdrawal: {str(e)}")
            raise

    def process_withdrawal(self, withdrawal):
        """Process a pending withdrawal request"""
        try:
            if withdrawal.status != 'pending':
                raise ValueError("Invalid withdrawal status")

            # Update status to processing
            withdrawal.status = 'processing'
            withdrawal.save()

            # Create blockchain transaction
            tx_hash = self.blockchain.send_transaction(
                withdrawal.network,
                withdrawal.address,
                withdrawal.amount
            )

            # Update withdrawal with transaction hash
            withdrawal.transaction_hash = tx_hash
            withdrawal.processed_at = timezone.now()
            withdrawal.status = 'completed'
            withdrawal.save()

            # Move from frozen balance to withdrawn
            account = withdrawal.account
            account.frozen_balance -= (withdrawal.amount + withdrawal.fee)
            account.total_withdrawn += withdrawal.amount
            account.save()

            # Create transaction record
            Transaction.objects.create(
                account=account,
                transaction_type='withdrawal',
                amount=withdrawal.amount,
                fee=withdrawal.fee,
                network=withdrawal.network,
                transaction_hash=tx_hash,
                status='completed'
            )

            # Notify user
            self.notify_withdrawal_update(withdrawal)

            return withdrawal

        except Exception as e:
            # Handle failure
            withdrawal.status = 'failed'
            withdrawal.error_message = str(e)
            withdrawal.save()

            # Return frozen balance to available
            account = withdrawal.account
            account.frozen_balance -= (withdrawal.amount + withdrawal.fee)
            account.balance += (withdrawal.amount + withdrawal.fee)
            account.save()

            # Notify user of failure
            self.notify_withdrawal_update(withdrawal)
            raise

    @staticmethod
    def notify_withdrawal_update(withdrawal):
        """Send withdrawal update notification through WebSocket"""
        channel_layer = get_channel_layer()
        
        withdrawal_data = {
            'id': withdrawal.id,
            'amount': str(withdrawal.amount),
            'fee': str(withdrawal.fee),
            'network': withdrawal.network,
            'status': withdrawal.status,
            'address': withdrawal.address,
            'created_at': withdrawal.created_at.isoformat(),
            'processed_at': withdrawal.processed_at.isoformat() if withdrawal.processed_at else None,
        }
        
        async_to_sync(channel_layer.group_send)(
            f"withdrawal_updates_{withdrawal.account.user.id}",
            {
                'type': 'withdrawal_update',
                'data': withdrawal_data
            }
        ) 