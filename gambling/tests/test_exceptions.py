from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from ..exceptions import (
    InsufficientBalanceError,
    InvalidBetError,
    GameNotActiveError,
    InvalidGameStateError,
    BetNotAllowedError
)
from ..models import GamblingGame, GamblingBet

User = get_user_model()

class GamblingExceptionsTest(TestCase):
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

    def test_insufficient_balance_error(self):
        """Test insufficient balance exception"""
        with self.assertRaises(InsufficientBalanceError) as context:
            if self.user.balance < Decimal('2.00000000'):
                raise InsufficientBalanceError(
                    required=Decimal('2.00000000'),
                    available=self.user.balance
                )
        
        self.assertIn('Insufficient balance', str(context.exception))
        self.assertEqual(context.exception.required, Decimal('2.00000000'))
        self.assertEqual(context.exception.available, Decimal('1.00000000'))

    def test_invalid_bet_error(self):
        """Test invalid bet exception"""
        with self.assertRaises(InvalidBetError) as context:
            if self.game.game_type == 'dice':
                if not (1 <= 7 <= 6):  # Invalid dice number
                    raise InvalidBetError('Invalid dice number: must be between 1 and 6')
        
        self.assertIn('Invalid dice number', str(context.exception))

    def test_game_not_active_error(self):
        """Test game not active exception"""
        self.game.status = 'completed'
        self.game.save()
        
        with self.assertRaises(GameNotActiveError) as context:
            if self.game.status != 'active':
                raise GameNotActiveError(
                    game_id=self.game.id,
                    current_status=self.game.status
                )
        
        self.assertIn('Game is not active', str(context.exception))
        self.assertEqual(context.exception.game_id, self.game.id)
        self.assertEqual(context.exception.current_status, 'completed')

    def test_invalid_game_state_error(self):
        """Test invalid game state transition exception"""
        with self.assertRaises(InvalidGameStateError) as context:
            if self.game.status == 'active':
                raise InvalidGameStateError(
                    from_status='active',
                    to_status='pending',
                    game_id=self.game.id
                )
        
        self.assertIn('Invalid game state transition', str(context.exception))
        self.assertEqual(context.exception.from_status, 'active')
        self.assertEqual(context.exception.to_status, 'pending')

    def test_bet_not_allowed_error(self):
        """Test bet not allowed exception"""
        with self.assertRaises(BetNotAllowedError) as context:
            if self.game.start_time > timezone.now():
                raise BetNotAllowedError(
                    'Betting not allowed before game starts',
                    game_id=self.game.id
                )
        
        self.assertIn('Betting not allowed', str(context.exception))
        self.assertEqual(context.exception.game_id, self.game.id)

    def test_exception_inheritance(self):
        """Test exception class inheritance"""
        self.assertTrue(issubclass(InsufficientBalanceError, Exception))
        self.assertTrue(issubclass(InvalidBetError, Exception))
        self.assertTrue(issubclass(GameNotActiveError, Exception))
        self.assertTrue(issubclass(InvalidGameStateError, Exception))
        self.assertTrue(issubclass(BetNotAllowedError, Exception))

    def test_exception_attributes(self):
        """Test exception attributes preservation"""
        try:
            raise InvalidGameStateError(
                from_status='active',
                to_status='pending',
                game_id=self.game.id,
                message='Custom error message'
            )
        except InvalidGameStateError as e:
            self.assertEqual(e.from_status, 'active')
            self.assertEqual(e.to_status, 'pending')
            self.assertEqual(e.game_id, self.game.id)
            self.assertIn('Custom error message', str(e))

    def test_exception_chaining(self):
        """Test exception chaining"""
        try:
            try:
                raise ValueError('Original error')
            except ValueError as e:
                raise InvalidBetError('Invalid bet data') from e
        except InvalidBetError as e:
            self.assertIsInstance(e.__cause__, ValueError)
            self.assertEqual(str(e.__cause__), 'Original error') 