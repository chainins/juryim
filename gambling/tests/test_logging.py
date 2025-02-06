from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import logging
from unittest.mock import patch, MagicMock
from ..models import GamblingGame, GamblingBet
from ..exceptions import InvalidBetError, InsufficientBalanceError

User = get_user_model()

class GamblingLoggingTest(TestCase):
    def setUp(self):
        self.logger = logging.getLogger('gambling')
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

    @patch('gambling.logging.logger.info')
    def test_game_creation_logging(self, mock_logger):
        """Test logging of game creation"""
        game = GamblingGame.objects.create(
            title='Logged Game',
            description='Test Description',
            game_type='dice',
            created_by=self.user,
            start_time=timezone.now() + timezone.timedelta(minutes=5),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            minimum_single_bet=Decimal('0.00000100'),
            maximum_single_bet=Decimal('0.10000000'),
            fee_percentage=Decimal('1.0')
        )
        
        mock_logger.assert_called_with(
            f'Game created: {game.id} by user {self.user.username}'
        )

    @patch('gambling.logging.logger.info')
    def test_bet_placement_logging(self, mock_logger):
        """Test logging of bet placement"""
        bet = GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )
        
        mock_logger.assert_called_with(
            f'Bet placed: {bet.id} on game {self.game.id} by user {self.user.username}'
        )

    @patch('gambling.logging.logger.error')
    def test_error_logging(self, mock_logger):
        """Test logging of errors"""
        try:
            raise InvalidBetError('Invalid bet amount')
        except InvalidBetError as e:
            self.logger.error('Bet error: %s', str(e))
        
        mock_logger.assert_called_with('Bet error: Invalid bet amount')

    @patch('gambling.logging.logger.warning')
    def test_insufficient_balance_logging(self, mock_logger):
        """Test logging of insufficient balance"""
        try:
            raise InsufficientBalanceError(
                required=Decimal('2.00000000'),
                available=Decimal('1.00000000')
            )
        except InsufficientBalanceError as e:
            self.logger.warning('Balance error: %s', str(e))
        
        mock_logger.assert_called_once()

    @patch('gambling.logging.logger.info')
    def test_game_status_change_logging(self, mock_logger):
        """Test logging of game status changes"""
        self.game.status = 'completed'
        self.game.save()
        
        mock_logger.assert_called_with(
            f'Game {self.game.id} status changed to completed'
        )

    @override_settings(LOGGING={
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'test_handler': {
                'class': 'logging.NullHandler',
            },
        },
        'loggers': {
            'gambling': {
                'handlers': ['test_handler'],
                'level': 'DEBUG',
            },
        },
    })
    def test_logging_configuration(self):
        """Test logging configuration"""
        logger = logging.getLogger('gambling')
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(len(logger.handlers), 1)

    @patch('gambling.logging.logger.critical')
    def test_critical_error_logging(self, mock_logger):
        """Test logging of critical errors"""
        try:
            raise Exception('Critical system error')
        except Exception as e:
            self.logger.critical('System error: %s', str(e))
        
        mock_logger.assert_called_with('System error: Critical system error')

    def test_log_formatting(self):
        """Test log message formatting"""
        with self.assertLogs('gambling', level='INFO') as logs:
            self.logger.info('Test message with data: %s', 'test_value')
            
        self.assertEqual(len(logs.records), 1)
        self.assertIn('Test message with data: test_value', logs.records[0].message) 