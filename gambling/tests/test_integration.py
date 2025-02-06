from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from channels.testing import WebsocketCommunicator
from ..consumers import GameConsumer
from ..models import GamblingGame, GamblingBet

User = get_user_model()

class GamblingIntegrationTest(TestCase):
    async def setUp(self):
        self.client = Client()
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
        self.client.login(username='testuser', password='testpass123')

    async def test_bet_placement_workflow(self):
        """Test complete bet placement workflow including WebSocket updates"""
        # 1. Place bet via API
        bet_data = {
            'amount': '0.00100000',
            'bet_data': {'number': 6}
        }
        response = self.client.post(
            reverse('gambling:place_bet_api', args=[self.game.id]),
            bet_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        bet_id = response.json()['bet_id']

        # 2. Connect to WebSocket
        communicator = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            f"/ws/game/{self.game.id}/"
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # 3. Verify bet update received
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'bet.placed')
        self.assertEqual(response['bet']['id'], bet_id)

        await communicator.disconnect()

    def test_game_completion_workflow(self):
        """Test game completion workflow including balance updates"""
        initial_balance = self.user.balance

        # 1. Place bet
        bet = GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )

        # 2. Complete game
        self.game.complete({'number': 6})  # Winning number matches bet
        
        # 3. Verify bet status updated
        bet.refresh_from_db()
        self.assertEqual(bet.status, 'won')
        
        # 4. Verify user balance updated
        self.user.refresh_from_db()
        self.assertGreater(self.user.balance, initial_balance)

    def test_concurrent_bet_placement(self):
        """Test handling of concurrent bet placements"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123',
            balance=Decimal('1.00000000')
        )

        # Place bets concurrently
        bet_data = {
            'amount': '0.00100000',
            'bet_data': {'number': 6}
        }
        
        # Simulate concurrent requests
        response1 = self.client.post(
            reverse('gambling:place_bet_api', args=[self.game.id]),
            bet_data,
            content_type='application/json'
        )
        
        self.client.login(username='otheruser', password='testpass123')
        response2 = self.client.post(
            reverse('gambling:place_bet_api', args=[self.game.id]),
            bet_data,
            content_type='application/json'
        )

        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        
        # Verify both bets were created correctly
        self.assertEqual(GamblingBet.objects.count(), 2)
        self.assertEqual(
            self.game.total_bets,
            Decimal('0.00200000')
        )

    def test_game_cancellation_workflow(self):
        """Test game cancellation workflow including refunds"""
        initial_balance = self.user.balance

        # 1. Place bet
        bet = GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )

        # 2. Cancel game
        self.game.cancel()
        
        # 3. Verify bet status
        bet.refresh_from_db()
        self.assertEqual(bet.status, 'cancelled')
        
        # 4. Verify refund
        self.user.refresh_from_db()
        self.assertEqual(
            self.user.balance,
            initial_balance  # Should be refunded to original balance
        )

    def test_game_notification_workflow(self):
        """Test game notifications through different channels"""
        # 1. Create game with future start time
        future_game = GamblingGame.objects.create(
            title='Future Game',
            description='Test Description',
            game_type='dice',
            created_by=self.user,
            start_time=timezone.now() + timezone.timedelta(minutes=5),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            minimum_single_bet=Decimal('0.00000100'),
            maximum_single_bet=Decimal('0.10000000'),
            fee_percentage=Decimal('1.0'),
            status='pending'
        )

        # 2. Place bet
        bet = GamblingBet.objects.create(
            user=self.user,
            game=future_game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )

        # 3. Activate game
        future_game.activate()
        
        # 4. Verify notifications
        # This would typically check email notifications and WebSocket messages
        # Implementation depends on your notification system
        self.assertEqual(future_game.status, 'active')
        self.assertTrue(
            GamblingBet.objects.filter(
                game=future_game,
                user=self.user
            ).exists()
        ) 