from django.core.management.base import BaseCommand
from django.utils import timezone
from financial.models import WithdrawalRequest
from datetime import timedelta

class Command(BaseCommand):
    help = 'Cleanup stale withdrawal requests'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to keep pending withdrawals'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=days)

        stale_withdrawals = WithdrawalRequest.objects.filter(
            status='pending',
            created_at__lt=cutoff_date
        )

        self.stdout.write(f'Found {stale_withdrawals.count()} stale withdrawals')

        if not dry_run:
            for withdrawal in stale_withdrawals:
                withdrawal.status = 'cancelled'
                withdrawal.admin_notes = (
                    f'Automatically cancelled after {days} days of inactivity'
                )
                withdrawal.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Cancelled withdrawal {withdrawal.id}'
                    )
                )
        else:
            for withdrawal in stale_withdrawals:
                self.stdout.write(
                    f'Would cancel withdrawal {withdrawal.id}'
                )

        self.stdout.write(self.style.SUCCESS('Cleanup completed')) 