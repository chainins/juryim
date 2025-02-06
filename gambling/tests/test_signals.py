from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from decimal import Decimal
from unittest.mock import patch
from ..models import GamblingGame, GamblingBet
from ..signals import (
    schedule_game_completion,
    schedule_game_start_notification,
    update_user_balance_on_bet,
    update_user_balance_on_win
)

User = get_user_model()

class GamblingSignalsTest(TestCase):
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

    @patch('gambling.signals.complete_game_task.apply_async')
    def test_schedule_game_completion(self, mock_task):
        # Create game with future end time
        game = GamblingGame.objects.create(
            title='Future Game',
            description='Test Description',
            game_type='dice',
            created_by=self.user,
            start_time=timezone.now() + timezone.timedelta(minutes=5),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            minimum_single_bet=Decimal('0.00000100'),
            maximum_single_bet=Decimal('0.10000000'),
            fee_percentage=Decimal('1.0')
        )
        
        # Verify completion task was scheduled
        mock_task.assert_called_once()
        args, kwargs = mock_task.call_args
        self.assertEqual(kwargs['args'][0], game.id)

    @patch('gambling.signals.send_game_start_notification_task.apply_async')
    def test_schedule_game_start_notification(self, mock_task):
        # Create game with future start time
        game = GamblingGame.objects.create(
            title='Future Game',
            description='Test Description',
            game_type='dice',
            created_by=self.user,
            start_time=timezone.now() + timezone.timedelta(minutes=5),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            minimum_single_bet=Decimal('0.00000100'),
            maximum_single_bet=Decimal('0.10000000'),
            fee_percentage=Decimal('1.0')
        )
        
        # Verify notification task was scheduled
        mock_task.assert_called_once()
        args, kwargs = mock_task.call_args
        self.assertEqual(kwargs['args'][0], game.id)

    def test_update_user_balance_on_bet(self):
        initial_balance = self.user.balance
        bet_amount = Decimal('0.00100000')
        fee_amount = Decimal('0.00001000')
        
        # Create bet
        bet = GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=bet_amount,
            bet_data={'number': 6},
            fee_amount=fee_amount
        )
        
        # Refresh user from database
        self.user.refresh_from_db()
        
        # Verify balance was reduced by bet amount plus fee
        expected_balance = initial_balance - bet_amount - fee_amount
        self.assertEqual(self.user.balance, expected_balance)

    def test_update_user_balance_on_win(self):
        initial_balance = self.user.balance
        bet_amount = Decimal('0.00100000')
        fee_amount = Decimal('0.00001000')
        win_amount = Decimal('0.00600000')
        
        # Create bet
        bet = GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=bet_amount,
            bet_data={'number': 6},
            fee_amount=fee_amount
        )
        
        # Update bet to won status with win amount
        bet.status = 'won'
        bet.win_amount = win_amount
        bet.save()
        
        # Refresh user from database
        self.user.refresh_from_db()
        
        # Verify balance includes win amount
        expected_balance = initial_balance - bet_amount - fee_amount + win_amount
        self.assertEqual(self.user.balance, expected_balance)

    def test_signal_disconnection(self):
        # Temporarily disconnect signals
        post_save.disconnect(schedule_game_completion, sender=GamblingGame)
        post_save.disconnect(schedule_game_start_notification, sender=GamblingGame)
        pre_save.disconnect(update_user_balance_on_bet, sender=GamblingBet)
        post_save.disconnect(update_user_balance_on_win, sender=GamblingBet)
        
        try:
            # Create game without triggering signals
            game = GamblingGame.objects.create(
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
            
            # Create bet without triggering signals
            initial_balance = self.user.balance
            bet = GamblingBet.objects.create(
                user=self.user,
                game=game,
                amount=Decimal('0.00100000'),
                bet_data={'number': 6},
                fee_amount=Decimal('0.00001000')
            )
            
            # Verify balance unchanged
            self.user.refresh_from_db()
            self.assertEqual(self.user.balance, initial_balance)
            
        finally:
            # Reconnect signals
            post_save.connect(schedule_game_completion, sender=GamblingGame)
            post_save.connect(schedule_game_start_notification, sender=GamblingGame)
            pre_save.connect(update_user_balance_on_bet, sender=GamblingBet)
            post_save.connect(update_user_balance_on_win, sender=GamblingBet) 