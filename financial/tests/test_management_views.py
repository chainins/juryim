from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from ..models import FinancialAccount, WithdrawalRequest
from decimal import Decimal

User = get_user_model()

class ManagementViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True
        )
        # Add necessary permissions
        permissions = Permission.objects.filter(
            codename__in=[
                'manage_accounts',
                'manage_withdrawals'
            ]
        )
        self.admin_user.user_permissions.add(*permissions)
        
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test data
        self.account = FinancialAccount.objects.create(
            user=self.user,
            balance=Decimal('100.00')
        )
        self.withdrawal = WithdrawalRequest.objects.create(
            account=self.account,
            amount=Decimal('50.00'),
            fee=Decimal('1.00'),
            network='BTC',
            address='1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
        )

    def test_account_list_view(self):
        # Unauthenticated user should be redirected
        response = self.client.get(reverse('financial_management:accounts'))
        self.assertEqual(response.status_code, 302)
        
        # Regular user should get permission denied
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('financial_management:accounts'))
        self.assertEqual(response.status_code, 403)
        
        # Admin user should get access
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('financial_management:accounts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('financial/management/account_list.html')
        self.assertContains(response, self.user.username)

    def test_withdrawal_management(self):
        self.client.login(username='admin', password='testpass123')
        
        # Test withdrawal list view
        response = self.client.get(reverse('financial_management:withdrawals'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.withdrawal.amount))
        
        # Test withdrawal approval
        response = self.client.post(
            reverse('financial_management:approve_withdrawal', 
                   args=[self.withdrawal.id])
        )
        self.assertEqual(response.status_code, 302)
        self.withdrawal.refresh_from_db()
        self.assertEqual(self.withdrawal.status, 'approved')
        
        # Test withdrawal rejection
        new_withdrawal = WithdrawalRequest.objects.create(
            account=self.account,
            amount=Decimal('25.00'),
            fee=Decimal('1.00'),
            network='BTC',
            address='1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
        )
        response = self.client.post(
            reverse('financial_management:reject_withdrawal', 
                   args=[new_withdrawal.id]),
            {'reason': 'Test rejection'}
        )
        self.assertEqual(response.status_code, 302)
        new_withdrawal.refresh_from_db()
        self.assertEqual(new_withdrawal.status, 'rejected') 