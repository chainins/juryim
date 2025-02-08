from django.core.management.base import BaseCommand
from django.utils import timezone
from financial.models import WithdrawalRequest
from financial.services import WithdrawalService

class Command(BaseCommand):
    help = 'Process pending withdrawal requests'

    def handle(self, *args, **options):
        withdrawal_service = WithdrawalService()
        
        # Get pending withdrawals
        pending_withdrawals = WithdrawalRequest.objects.filter(
            status='pending'
        ).select_related('account')

        self.stdout.write(f"Found {pending_withdrawals.count()} pending withdrawals")

        for withdrawal in pending_withdrawals:
            try:
                self.stdout.write(f"Processing withdrawal {withdrawal.id}")
                withdrawal_service.process_withdrawal(withdrawal)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully processed withdrawal {withdrawal.id}"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Error processing withdrawal {withdrawal.id}: {str(e)}"
                    )
                ) 