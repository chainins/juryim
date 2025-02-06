from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from ..models import GamblingGame, GamblingBet

User = get_user_model()

class GamblingGameModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.game_data = {
            'title': 'Test Game',
            'description': 'Test Description',
            'game_type': 'dice',
            'created_by': self.user,
            'start_time': timezone.now() + timezone.timedelta(minutes=5),
            'end_time': timezone.now() + timezone.timedelta(hours=1),
            'minimum_single_bet': Decimal('0.00000100'),
            'maximum_single_bet': Decimal('0.10000000'),
            'fee_percentage': Decimal('1.0')
        }

    def test_game_creation(self):
        game = GamblingGame.objects.create(**self.game_data)
        self.assertEqual(game.title, 'Test Game')
        self.assertEqual(game.game_type, 'dice')
        self.assertEqual(game.status, 'pending')
        self.assertEqual(game.created_by, self.user)

    def test_game_str_representation(self):
        game = GamblingGame.objects.create(**self.game_data)
        self.assertEqual(str(game), 'Test Game')

    def test_invalid_game_type(self):
        self.game_data['game_type'] = 'invalid'
        with self.assertRaises(ValidationError):
            game = GamblingGame.objects.create(**self.game_data)
            game.full_clean()

    def test_invalid_bet_limits(self):
        self.game_data['minimum_single_bet'] = Decimal('0.2')
        self.game_data['maximum_single_bet'] = Decimal('0.1')
        with self.assertRaises(ValidationError):
            game = GamblingGame.objects.create(**self.game_data)
            game.full_clean()

    def test_invalid_fee_percentage(self):
        self.game_data['fee_percentage'] = Decimal('15.0')
        with self.assertRaises(ValidationError):
            game = GamblingGame.objects.create(**self.game_data)
            game.full_clean()

class GamblingBetModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
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
            fee_percentage=Decimal('1.0')
        )
        self.bet_data = {
            'user': self.user,
            'game': self.game,
            'amount': Decimal('0.00100000'),
            'bet_data': {'number': 6},
            'fee_amount': Decimal('0.00001000')
        }

    def test_bet_creation(self):
        bet = GamblingBet.objects.create(**self.bet_data)
        self.assertEqual(bet.user, self.user)
        self.assertEqual(bet.game, self.game)
        self.assertEqual(bet.amount, Decimal('0.00100000'))
        self.assertEqual(bet.status, 'placed')

    def test_bet_str_representation(self):
        bet = GamblingBet.objects.create(**self.bet_data)
        expected = f'Bet {bet.id} by {self.user.username} on {self.game.title}'
        self.assertEqual(str(bet), expected)

    def test_invalid_bet_amount(self):
        self.bet_data['amount'] = Decimal('0.00000001')  # Below minimum
        with self.assertRaises(ValidationError):
            bet = GamblingBet.objects.create(**self.bet_data)
            bet.full_clean()

    def test_invalid_bet_data(self):
        self.bet_data['bet_data'] = {'invalid': 'data'}
        with self.assertRaises(ValidationError):
            bet = GamblingBet.objects.create(**self.bet_data)
            bet.full_clean()

    def test_bet_status_transitions(self):
        bet = GamblingBet.objects.create(**self.bet_data)
        self.assertEqual(bet.status, 'placed')
        
        bet.status = 'won'
        bet.win_amount = Decimal('0.00200000')
        bet.save()
        self.assertEqual(bet.status, 'won')
        
        # Should not be able to change from won to placed
        bet.status = 'placed'
        with self.assertRaises(ValidationError):
            bet.full_clean() 