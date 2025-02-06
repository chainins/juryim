from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from ..models import GamblingGame, GamblingBet

User = get_user_model()

class GamblingAdminTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create superuser
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        # Create regular user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            balance=Decimal('1.00000000')
        )
        # Create game
        self.game = GamblingGame.objects.create(
            title='Test Game',
            description='Test Description',
            game_type='dice',
            created_by=self.user,
            start_time=timezone.now() + timezone.timedelta(minutes=5),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            minimum_single_bet=Decimal('0.00000100'),
            maximum_single_bet=Decimal('0.10000000'),
            fee_percentage=Decimal('1.0'),
            status='active'
        )
        # Create bet
        self.bet = GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )
        # Login as admin
        self.client.login(username='admin', password='adminpass123')

    def test_game_admin_list(self):
        url = reverse('admin:gambling_gamblinggame_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Game')
        self.assertContains(response, 'dice')
        self.assertContains(response, 'active')

    def test_bet_admin_list(self):
        url = reverse('admin:gambling_gamblingbet_changelist')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, '0.00100000')
        self.assertContains(response, 'placed')

    def test_game_admin_detail(self):
        url = reverse('admin:gambling_gamblinggame_change', args=[self.game.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Game')
        self.assertContains(response, 'Test Description')
        self.assertContains(response, 'dice')

    def test_bet_admin_detail(self):
        url = reverse('admin:gambling_gamblingbet_change', args=[self.bet.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, '0.00100000')
        self.assertContains(response, 'placed')

    def test_admin_actions(self):
        # Test cancel game action
        url = reverse('admin:gambling_gamblinggame_changelist')
        data = {
            'action': 'cancel_games',
            '_selected_action': [self.game.id],
        }
        response = self.client.post(url, data, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.game.refresh_from_db()
        self.assertEqual(self.game.status, 'cancelled')

    def test_admin_search(self):
        # Test game search
        url = reverse('admin:gambling_gamblinggame_changelist')
        response = self.client.get(url, {'q': 'Test Game'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Game')
        
        # Test with non-matching search
        response = self.client.get(url, {'q': 'Non Existent Game'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test Game')

    def test_admin_filters(self):
        # Test game type filter
        url = reverse('admin:gambling_gamblinggame_changelist')
        response = self.client.get(url, {'game_type': 'dice'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Game')
        
        # Test status filter
        response = self.client.get(url, {'status': 'active'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Game')

    def test_admin_readonly_fields(self):
        # Test bet detail view has readonly fields
        url = reverse('admin:gambling_gamblingbet_change', args=[self.bet.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'field-amount')
        self.assertContains(response, 'field-fee_amount')
        
        # Attempt to modify readonly field
        data = {
            'amount': '0.00200000',  # Should not change
            'fee_amount': '0.00002000'  # Should not change
        }
        response = self.client.post(url, data)
        
        self.bet.refresh_from_db()
        self.assertEqual(self.bet.amount, Decimal('0.00100000'))
        self.assertEqual(self.bet.fee_amount, Decimal('0.00001000')) 