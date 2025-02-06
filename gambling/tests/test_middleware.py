from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from decimal import Decimal
from ..middleware import GamblingMiddleware
from ..models import GamblingGame, GamblingBet
from django.utils import timezone

User = get_user_model()

class GamblingMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = GamblingMiddleware(lambda r: HttpResponse())
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

    def test_process_request_authenticated(self):
        request = self.factory.get('/')
        request.user = self.user
        
        # Create some active bets
        bet1 = GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )
        bet2 = GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00200000'),
            bet_data={'number': 3},
            fee_amount=Decimal('0.00002000')
        )
        
        response = self.middleware(request)
        
        # Verify gambling context is added
        self.assertTrue(hasattr(request, 'gambling_context'))
        self.assertEqual(request.gambling_context['active_bets_count'], 2)
        self.assertEqual(
            request.gambling_context['total_active_bets'],
            Decimal('0.00300000')
        )

    def test_process_request_unauthenticated(self):
        request = self.factory.get('/')
        request.user = None
        
        response = self.middleware(request)
        
        # Verify gambling context is empty for unauthenticated users
        self.assertTrue(hasattr(request, 'gambling_context'))
        self.assertEqual(request.gambling_context['active_bets_count'], 0)
        self.assertEqual(
            request.gambling_context['total_active_bets'],
            Decimal('0')
        )

    def test_process_request_with_completed_bets(self):
        request = self.factory.get('/')
        request.user = self.user
        
        # Create active and completed bets
        active_bet = GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )
        completed_bet = GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00200000'),
            bet_data={'number': 3},
            fee_amount=Decimal('0.00002000'),
            status='won'
        )
        
        response = self.middleware(request)
        
        # Verify only active bets are counted
        self.assertEqual(request.gambling_context['active_bets_count'], 1)
        self.assertEqual(
            request.gambling_context['total_active_bets'],
            Decimal('0.00100000')
        )

    def test_process_request_with_multiple_games(self):
        request = self.factory.get('/')
        request.user = self.user
        
        # Create another game
        game2 = GamblingGame.objects.create(
            title='Test Game 2',
            description='Test Description 2',
            game_type='coin',
            created_by=self.user,
            start_time=timezone.now() + timezone.timedelta(minutes=5),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            minimum_single_bet=Decimal('0.00000100'),
            maximum_single_bet=Decimal('0.10000000'),
            fee_percentage=Decimal('1.0'),
            status='active'
        )
        
        # Create bets for different games
        bet1 = GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )
        bet2 = GamblingBet.objects.create(
            user=self.user,
            game=game2,
            amount=Decimal('0.00200000'),
            bet_data={'side': 'heads'},
            fee_amount=Decimal('0.00002000')
        )
        
        response = self.middleware(request)
        
        # Verify bets from all games are counted
        self.assertEqual(request.gambling_context['active_bets_count'], 2)
        self.assertEqual(
            request.gambling_context['total_active_bets'],
            Decimal('0.00300000')
        )

    def test_process_request_performance(self):
        request = self.factory.get('/')
        request.user = self.user
        
        # Create many bets
        for i in range(100):
            GamblingBet.objects.create(
                user=self.user,
                game=self.game,
                amount=Decimal('0.00100000'),
                bet_data={'number': 6},
                fee_amount=Decimal('0.00001000')
            )
        
        # Verify middleware handles large number of bets efficiently
        import time
        start_time = time.time()
        response = self.middleware(request)
        execution_time = time.time() - start_time
        
        self.assertTrue(execution_time < 0.1)  # Should execute in under 100ms
        self.assertEqual(request.gambling_context['active_bets_count'], 100) 