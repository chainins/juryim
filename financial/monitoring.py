from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger('blockchain')

class MonitoringService:
    def __init__(self):
        self.logger = logger

    def check_wallet_balance(self, network):
        """Check if hot wallet balance is sufficient"""
        try:
            from .blockchain import BlockchainAPI
            blockchain = BlockchainAPI()
            
            # Get minimum required balance from settings
            min_balance = Decimal(settings.NETWORK_SETTINGS[network]['min_hot_wallet_balance'])
            
            # Get current balance
            if network == 'BTC':
                balance = blockchain.get_btc_balance()
            elif network == 'ETH':
                balance = blockchain.get_eth_balance()
            elif network == 'USDT':
                balance = blockchain.get_usdt_balance()
            else:
                raise ValueError(f"Unsupported network: {network}")
            
            # Check if balance is below threshold
            if balance < min_balance:
                self.alert_low_balance(network, balance, min_balance)
                
            return balance
            
        except Exception as e:
            self.logger.error(f"Error checking {network} wallet balance: {str(e)}")
            self.alert_error("Wallet Balance Check", network, str(e))
            return None

    def check_pending_withdrawals(self):
        """Check for stuck pending withdrawals"""
        from .models import WithdrawalRequest
        from django.utils import timezone
        from datetime import timedelta
        
        try:
            # Get withdrawals pending for more than 1 hour
            threshold = timezone.now() - timedelta(hours=1)
            stuck_withdrawals = WithdrawalRequest.objects.filter(
                status='pending',
                created_at__lt=threshold
            )
            
            if stuck_withdrawals.exists():
                self.alert_stuck_withdrawals(stuck_withdrawals)
                
            return stuck_withdrawals.count()
            
        except Exception as e:
            self.logger.error(f"Error checking pending withdrawals: {str(e)}")
            self.alert_error("Pending Withdrawals Check", "ALL", str(e))
            return None

    def alert_low_balance(self, network, current_balance, min_balance):
        """Send low balance alert"""
        subject = f"LOW BALANCE ALERT - {network}"
        message = (
            f"The {network} hot wallet balance is below minimum threshold!\n\n"
            f"Current Balance: {current_balance}\n"
            f"Minimum Required: {min_balance}\n\n"
            f"Please top up the hot wallet as soon as possible."
        )
        
        self._send_alert(subject, message)

    def alert_stuck_withdrawals(self, withdrawals):
        """Send stuck withdrawals alert"""
        subject = "STUCK WITHDRAWALS ALERT"
        message = "The following withdrawals are stuck in pending status:\n\n"
        
        for w in withdrawals:
            message += (
                f"ID: {w.id}\n"
                f"Network: {w.network}\n"
                f"Amount: {w.amount}\n"
                f"Created: {w.created_at}\n"
                f"User: {w.account.user.username}\n\n"
            )
            
        message += "Please investigate and process these withdrawals."
        
        self._send_alert(subject, message)

    def alert_error(self, check_type, network, error):
        """Send error alert"""
        subject = f"MONITORING ERROR - {check_type}"
        message = (
            f"An error occurred during {check_type}:\n\n"
            f"Network: {network}\n"
            f"Error: {error}\n\n"
            f"Please investigate and resolve the issue."
        )
        
        self._send_alert(subject, message)

    def _send_alert(self, subject, message):
        """Send alert email"""
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False
            )
            self.logger.info(f"Alert sent: {subject}")
        except Exception as e:
            self.logger.error(f"Error sending alert: {str(e)}") 