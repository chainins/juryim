from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from ..serializers import (
    GamblingGameSerializer,
    GamblingBetSerializer,
    GameStatusSerializer,
    UserBetSerializer,
    GameStatisticsSerializer
)
from ..models import GamblingGame, GamblingBet

User = get_user_model()

class GamblingSerializersTest(TestCase):
    def setUp(self):
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
        self.bet = GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )

    def test_gambling_game_serializer(self):
        serializer = GamblingGameSerializer(self.game)
        data = serializer.data
        
        self.assertEqual(data['title'], 'Test Game')
        self.assertEqual(data['description'], 'Test Description')
        self.assertEqual(data['game_type'], 'dice')
        self.assertEqual(data['status'], 'active')
        self.assertEqual(data['minimum_single_bet'], '0.00000100')
        self.assertEqual(data['maximum_single_bet'], '0.10000000')
        self.assertEqual(data['fee_percentage'], '1.0')
        self.assertEqual(data['created_by'], self.user.username)

    def test_gambling_bet_serializer(self):
        serializer = GamblingBetSerializer(self.bet)
        data = serializer.data
        
        self.assertEqual(data['amount'], '0.00100000')
        self.assertEqual(data['bet_data'], {'number': 6})
        self.assertEqual(data['fee_amount'], '0.00001000')
        self.assertEqual(data['status'], 'placed')
        self.assertEqual(data['user'], self.user.username)
        self.assertEqual(data['game'], self.game.id)

    def test_game_status_serializer(self):
        # Create additional bet
        GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00200000'),
            bet_data={'number': 3},
            fee_amount=Decimal('0.00002000')
        )
        
        serializer = GameStatusSerializer(self.game)
        data = serializer.data
        
        self.assertEqual(data['status'], 'active')
        self.assertEqual(data['total_bets'], '0.00300000')
        self.assertEqual(data['total_players'], 1)
        self.assertIn('time_remaining', data)

    def test_user_bet_serializer(self):
        serializer = UserBetSerializer(self.bet)
        data = serializer.data
        
        self.assertEqual(data['amount'], '0.00100000')
        self.assertEqual(data['bet_data'], {'number': 6})
        self.assertEqual(data['status'], 'placed')
        self.assertEqual(data['game_title'], 'Test Game')
        self.assertEqual(data['game_type'], 'dice')
        self.assertIn('placed_at', data)

    def test_game_statistics_serializer(self):
        # Create bet from another user
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        GamblingBet.objects.create(
            user=other_user,
            game=self.game,
            amount=Decimal('0.00200000'),
            bet_data={'number': 3},
            fee_amount=Decimal('0.00002000')
        )
        
        serializer = GameStatisticsSerializer(self.game)
        data = serializer.data
        
        self.assertEqual(data['total_bets'], '0.00300000')
        self.assertEqual(data['total_players'], 2)
        self.assertEqual(data['total_fees'], '0.00003000')
        self.assertEqual(data['game_type'], 'dice')
        self.assertEqual(data['status'], 'active')

    def test_serializer_validation(self):
        # Test invalid bet data
        invalid_data = {
            'user': self.user.id,
            'game': self.game.id,
            'amount': '0.00100000',
            'bet_data': {'invalid': 'data'},
            'fee_amount': '0.00001000'
        }
        serializer = GamblingBetSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        
        # Test invalid amount
        invalid_data = {
            'user': self.user.id,
            'game': self.game.id,
            'amount': '-0.00100000',
            'bet_data': {'number': 6},
            'fee_amount': '0.00001000'
        }
        serializer = GamblingBetSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_serializer_methods(self):
        # Test custom method field
        serializer = UserBetSerializer(self.bet)
        self.assertEqual(
            serializer.get_game_title(self.bet),
            'Test Game'
        )
        
        # Test time remaining calculation
        serializer = GameStatusSerializer(self.game)
        time_remaining = serializer.get_time_remaining(self.game)
        self.assertIsInstance(time_remaining, str)
        self.assertIn('minutes', time_remaining)

    def test_nested_serialization(self):
        # Test nested user data
        serializer = GamblingGameSerializer(self.game)
        self.assertIn('created_by', serializer.data)
        self.assertEqual(serializer.data['created_by'], self.user.username)
        
        # Test nested game data
        serializer = GamblingBetSerializer(self.bet)
        self.assertIn('game', serializer.data)
        self.assertEqual(serializer.data['game'], self.game.id) 