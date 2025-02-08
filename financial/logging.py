import logging
from decimal import Decimal
from django.utils import timezone

logger = logging.getLogger('blockchain')

class TransactionLogger:
    @staticmethod
    def log_withdrawal_request(withdrawal):
        """Log withdrawal request"""
        logger.info(
            f"Withdrawal request created: ID={withdrawal.id}, "
            f"User={withdrawal.account.user.username}, "
            f"Amount={withdrawal.amount} {withdrawal.network}, "
            f"Address={withdrawal.address}"
        )

    @staticmethod
    def log_withdrawal_processed(withdrawal, tx_hash):
        """Log processed withdrawal"""
        logger.info(
            f"Withdrawal processed: ID={withdrawal.id}, "
            f"User={withdrawal.account.user.username}, "
            f"Amount={withdrawal.amount} {withdrawal.network}, "
            f"TxHash={tx_hash}"
        )

    @staticmethod
    def log_withdrawal_error(withdrawal, error):
        """Log withdrawal error"""
        logger.error(
            f"Withdrawal error: ID={withdrawal.id}, "
            f"User={withdrawal.account.user.username}, "
            f"Error={str(error)}"
        )

    @staticmethod
    def log_blockchain_transaction(network, tx_type, amount, address, tx_hash, status):
        """Log blockchain transaction"""
        logger.info(
            f"Blockchain transaction: Network={network}, "
            f"Type={tx_type}, Amount={amount}, "
            f"Address={address}, TxHash={tx_hash}, "
            f"Status={status}"
        )

    @staticmethod
    def log_balance_update(account, old_balance, new_balance, reason):
        """Log balance updates"""
        logger.info(
            f"Balance update: User={account.user.username}, "
            f"Old={old_balance}, New={new_balance}, "
            f"Change={new_balance - old_balance}, "
            f"Reason={reason}"
        )

    @staticmethod
    def log_error(error_type, message, details=None):
        """Log general errors"""
        log_message = f"Error: Type={error_type}, Message={message}"
        if details:
            log_message += f", Details={details}"
        logger.error(log_message) 