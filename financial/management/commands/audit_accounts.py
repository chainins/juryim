from django.core.management.base import BaseCommand
from django.db.models import Sum
from financial.models import FinancialAccount, Transaction
from decimal import Decimal

class Command(BaseCommand):
    help = 'Audit financial accounts for discrepancies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Fix discrepancies automatically'
        )
        parser.add_argument(
            '--email-report',
            action='store_true',
            help='Email audit report to administrators'
        )

    def handle(self, *args, **options):
        fix = options['fix']
        email_report = options['email_report']
        discrepancies = []

        accounts = FinancialAccount.objects.all()
        for account in accounts:
            # Calculate expected balance
            transactions = Transaction.objects.filter(account=account)
            expected_balance = transactions.aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0')

            # Check for discrepancy
            if account.balance != expected_balance:
                discrepancy = {
                    'account': account,
                    'current_balance': account.balance,
                    'expected_balance': expected_balance,
                    'difference': account.balance - expected_balance
                }
                discrepancies.append(discrepancy)

                self.stdout.write(
                    self.style.WARNING(
                        f'Account {account.id}: '
                        f'Balance mismatch of {discrepancy["difference"]}'
                    )
                )

                if fix:
                    account.balance = expected_balance
                    account.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Fixed balance for account {account.id}'
                        )
                    )

        if email_report and discrepancies:
            self.send_audit_report(discrepancies)

        self.stdout.write(
            self.style.SUCCESS(
                f'Audit completed. Found {len(discrepancies)} discrepancies'
            )
        )

    def send_audit_report(self, discrepancies):
        # Implementation for sending email report
        pass 