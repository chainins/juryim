from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core import mail
from decimal import Decimal
from unittest.mock import patch
from ..models import GamblingGame, GamblingBet
from ..tasks import (
    complete_game_task,
    cleanup_old_games_task,
    send_game_start_notification_task,
    send_bet_result_notification_task
)

User = get_user_model()

class GamblingTasksTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
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

    @patch('gambling.tasks.GamblingService.complete_game')
    def test_complete_game_task(self, mock_complete_game):
        # Set up mock return value
        mock_complete_game.return_value = {'number': 6}
        
        # Execute task
        complete_game_task(self.game.id)
        
        # Verify game completion
        mock_complete_game.assert_called_once_with(self.game)
        
        # Verify game status
        self.game.refresh_from_db()
        self.assertEqual(self.game.status, 'completed')

    def test_cleanup_old_games_task(self):
        # Create old completed game
        old_game = GamblingGame.objects.create(
            title='Old Game',
            description='Old Description',
            game_type='dice',
            created_by=self.user,
            start_time=timezone.now() - timezone.timedelta(days=31),
            end_time=timezone.now() - timezone.timedelta(days=30),
            minimum_single_bet=Decimal('0.00000100'),
            maximum_single_bet=Decimal('0.10000000'),
            fee_percentage=Decimal('1.0'),
            status='completed'
        )
        
        # Execute task
        cleanup_old_games_task()
        
        # Verify old game is deleted
        self.assertFalse(GamblingGame.objects.filter(id=old_game.id).exists())
        # Verify active game remains
        self.assertTrue(GamblingGame.objects.filter(id=self.game.id).exists())

    def test_send_game_start_notification_task(self):
        # Execute task
        send_game_start_notification_task(self.game.id)
        
        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertIn(self.game.title, mail.outbox[0].subject)
        self.assertIn(self.game.title, mail.outbox[0].body)

    def test_send_bet_result_notification_task(self):
        # Set game as completed with result
        self.game.status = 'completed'
        self.game.result = {'number': 6}
        self.game.save()
        
        # Set bet as won
        self.bet.status = 'won'
        self.bet.win_amount = Decimal('0.00600000')
        self.bet.save()
        
        # Execute task
        send_bet_result_notification_task(self.bet.id)
        
        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertIn('won', mail.outbox[0].subject.lower())
        self.assertIn('0.00600000', mail.outbox[0].body)

    @patch('gambling.tasks.send_game_start_notification_task.apply_async')
    def test_game_start_notification_scheduling(self, mock_task):
        # Create future game
        future_game = GamblingGame.objects.create(
            title='Future Game',
            description='Future Description',
            game_type='dice',
            created_by=self.user,
            start_time=timezone.now() + timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=2),
            minimum_single_bet=Decimal('0.00000100'),
            maximum_single_bet=Decimal('0.10000000'),
            fee_percentage=Decimal('1.0'),
            status='pending'
        )
        
        # Verify task was scheduled
        mock_task.assert_called_once()
        args, kwargs = mock_task.call_args
        self.assertEqual(kwargs['args'][0], future_game.id)

    @patch('gambling.tasks.complete_game_task.apply_async')
    def test_game_completion_scheduling(self, mock_task):
        # Create game ending soon
        ending_game = GamblingGame.objects.create(
            title='Ending Game',
            description='Ending Description',
            game_type='dice',
            created_by=self.user,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(minutes=5),
            minimum_single_bet=Decimal('0.00000100'),
            maximum_single_bet=Decimal('0.10000000'),
            fee_percentage=Decimal('1.0'),
            status='active'
        )
        
        # Verify task was scheduled
        mock_task.assert_called_once()
        args, kwargs = mock_task.call_args
        self.assertEqual(kwargs['args'][0], ending_game.id) 