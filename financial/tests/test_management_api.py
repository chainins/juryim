from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from ..models import FinancialAccount, WithdrawalRequest
from decimal import Decimal

User = get_user_model()

class ManagementAPITests(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True
        )
        permissions = Permission.objects.filter(
            codename__in=['manage_withdrawals']
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

    def test_withdrawal_status_api(self):
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(
            f"{reverse('api:withdrawal-status')}?ids={self.withdrawal.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data[str(self.withdrawal.id)],
            self.withdrawal.status
        )

    def test_withdrawal_approval_api(self):
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.post(
            reverse('api:withdrawal-approve', args=[self.withdrawal.id])
        )
        self.assertEqual(response.status_code, 200)
        self.withdrawal.refresh_from_db()
        self.assertEqual(self.withdrawal.status, 'approved')

    def test_withdrawal_rejection_api(self):
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.post(
            reverse('api:withdrawal-reject', args=[self.withdrawal.id]),
            {'reason': 'Test rejection'}
        )
        self.assertEqual(response.status_code, 200)
        self.withdrawal.refresh_from_db()
        self.assertEqual(self.withdrawal.status, 'rejected') 