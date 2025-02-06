from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from ..context_processors import gambling_processor
from ..models import GamblingGame, GamblingBet

User = get_user_model()

class GamblingContextProcessorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            balance=Decimal('1.00000000')
        )
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

    def test_context_processor_authenticated(self):
        request = self.factory.get('/')
        request.user = self.user
        
        # Add gambling context (normally added by middleware)
        request.gambling_context = {
            'active_bets_count': 2,
            'total_active_bets': Decimal('0.00300000')
        }
        
        context = gambling_processor(request)
        
        self.assertIn('GAMBLING_TYPES', context)
        self.assertIn('GAMBLING_STATUSES', context)
        self.assertIn('active_bets_count', context)
        self.assertIn('total_active_bets', context)
        self.assertEqual(context['active_bets_count'], 2)
        self.assertEqual(context['total_active_bets'], Decimal('0.00300000'))

    def test_context_processor_unauthenticated(self):
        request = self.factory.get('/')
        request.user = None
        
        # Add empty gambling context
        request.gambling_context = {
            'active_bets_count': 0,
            'total_active_bets': Decimal('0')
        }
        
        context = gambling_processor(request)
        
        self.assertIn('GAMBLING_TYPES', context)
        self.assertIn('GAMBLING_STATUSES', context)
        self.assertEqual(context['active_bets_count'], 0)
        self.assertEqual(context['total_active_bets'], Decimal('0'))

    def test_gambling_types_content(self):
        request = self.factory.get('/')
        request.user = self.user
        request.gambling_context = {}
        
        context = gambling_processor(request)
        
        gambling_types = context['GAMBLING_TYPES']
        self.assertIn('dice', gambling_types)
        self.assertIn('coin', gambling_types)
        self.assertIn('roulette', gambling_types)
        
        # Verify display names
        self.assertEqual(gambling_types['dice'], 'Dice')
        self.assertEqual(gambling_types['coin'], 'Coin Flip')
        self.assertEqual(gambling_types['roulette'], 'Roulette')

    def test_gambling_statuses_content(self):
        request = self.factory.get('/')
        request.user = self.user
        request.gambling_context = {}
        
        context = gambling_processor(request)
        
        gambling_statuses = context['GAMBLING_STATUSES']
        self.assertIn('pending', gambling_statuses)
        self.assertIn('active', gambling_statuses)
        self.assertIn('completed', gambling_statuses)
        self.assertIn('cancelled', gambling_statuses)
        
        # Verify display names
        self.assertEqual(gambling_statuses['pending'], 'Pending')
        self.assertEqual(gambling_statuses['active'], 'Active')
        self.assertEqual(gambling_statuses['completed'], 'Completed')
        self.assertEqual(gambling_statuses['cancelled'], 'Cancelled')

    def test_missing_gambling_context(self):
        request = self.factory.get('/')
        request.user = self.user
        # Don't add gambling_context to request
        
        context = gambling_processor(request)
        
        # Should provide default values
        self.assertEqual(context['active_bets_count'], 0)
        self.assertEqual(context['total_active_bets'], Decimal('0'))

    def test_context_processor_performance(self):
        request = self.factory.get('/')
        request.user = self.user
        request.gambling_context = {
            'active_bets_count': 1000,
            'total_active_bets': Decimal('1.00000000')
        }
        
        import time
        start_time = time.time()
        
        # Call processor multiple times
        for _ in range(100):
            context = gambling_processor(request)
            
        execution_time = time.time() - start_time
        
        # Should be very fast (under 10ms for 100 calls)
        self.assertTrue(execution_time < 0.01) 