from django.test import TestCase
from django.core.management import call_command
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from io import StringIO
from ..models import GamblingGame, GamblingBet

User = get_user_model()

class GamblingManagementCommandsTest(TestCase):
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

    def test_cleanup_expired_games(self):
        """Test command to cleanup expired games"""
        # Create expired game
        expired_game = GamblingGame.objects.create(
            title='Expired Game',
            description='Test Description',
            game_type='dice',
            created_by=self.user,
            start_time=timezone.now() - timezone.timedelta(days=2),
            end_time=timezone.now() - timezone.timedelta(days=1),
            minimum_single_bet=Decimal('0.00000100'),
            maximum_single_bet=Decimal('0.10000000'),
            fee_percentage=Decimal('1.0'),
            status='active'
        )

        out = StringIO()
        call_command('cleanup_expired_games', stdout=out)
        
        # Verify expired game was handled
        expired_game.refresh_from_db()
        self.assertEqual(expired_game.status, 'completed')
        self.assertIn('Cleaned up expired games', out.getvalue())

    def test_process_pending_games(self):
        """Test command to process pending games"""
        # Create pending game with past start time
        pending_game = GamblingGame.objects.create(
            title='Pending Game',
            description='Test Description',
            game_type='dice',
            created_by=self.user,
            start_time=timezone.now() - timezone.timedelta(minutes=5),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            minimum_single_bet=Decimal('0.00000100'),
            maximum_single_bet=Decimal('0.10000000'),
            fee_percentage=Decimal('1.0'),
            status='pending'
        )

        out = StringIO()
        call_command('process_pending_games', stdout=out)
        
        # Verify pending game was activated
        pending_game.refresh_from_db()
        self.assertEqual(pending_game.status, 'active')
        self.assertIn('Processed pending games', out.getvalue())

    def test_generate_gambling_report(self):
        """Test command to generate gambling report"""
        # Create some bets
        GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )
        GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00200000'),
            bet_data={'number': 3},
            fee_amount=Decimal('0.00002000')
        )

        out = StringIO()
        call_command('generate_gambling_report', stdout=out)
        
        # Verify report contains expected information
        output = out.getvalue()
        self.assertIn('Gambling Report', output)
        self.assertIn('Total Games:', output)
        self.assertIn('Total Bets:', output)
        self.assertIn('Total Fees:', output)

    def test_command_error_handling(self):
        """Test error handling in management commands"""
        # Test with invalid date format
        out = StringIO()
        with self.assertRaises(SystemExit):
            call_command('generate_gambling_report', date='invalid-date', stdout=out)
        
        # Test with non-existent game ID
        out = StringIO()
        with self.assertRaises(SystemExit):
            call_command('process_pending_games', game_id=99999, stdout=out)

    def test_dry_run_option(self):
        """Test dry-run option in commands"""
        # Create expired game
        expired_game = GamblingGame.objects.create(
            title='Expired Game',
            description='Test Description',
            game_type='dice',
            created_by=self.user,
            start_time=timezone.now() - timezone.timedelta(days=2),
            end_time=timezone.now() - timezone.timedelta(days=1),
            minimum_single_bet=Decimal('0.00000100'),
            maximum_single_bet=Decimal('0.10000000'),
            fee_percentage=Decimal('1.0'),
            status='active'
        )

        out = StringIO()
        call_command('cleanup_expired_games', dry_run=True, stdout=out)
        
        # Verify no changes were made
        expired_game.refresh_from_db()
        self.assertEqual(expired_game.status, 'active')
        self.assertIn('Dry run - no changes made', out.getvalue()) 