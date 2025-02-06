from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from channels.db import database_sync_to_async
from decimal import Decimal
import json
from ..routing import websocket_urlpatterns
from ..models import GamblingGame, GamblingBet
from ..consumers import GamblingConsumer

User = get_user_model()

class GamblingConsumerTest(TestCase):
    async def setUp(self):
        self.user = await database_sync_to_async(User.objects.create_user)(
            username='testuser',
            password='testpass123'
        )
        
        self.game = await database_sync_to_async(GamblingGame.objects.create)(
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
        
        self.application = URLRouter(websocket_urlpatterns)

    async def test_connect(self):
        communicator = WebsocketCommunicator(
            self.application,
            f"/ws/gambling/"
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_watch_game(self):
        communicator = WebsocketCommunicator(
            self.application,
            f"/ws/gambling/"
        )
        await communicator.connect()
        
        # Send watch_game message
        await communicator.send_json_to({
            'type': 'watch_game',
            'game_id': self.game.id
        })
        
        # Create a bet to trigger update
        bet = await database_sync_to_async(GamblingBet.objects.create)(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )
        
        # Receive game update
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'game_update')
        self.assertEqual(response['game_id'], self.game.id)
        
        await communicator.disconnect()

    async def test_unwatch_game(self):
        communicator = WebsocketCommunicator(
            self.application,
            f"/ws/gambling/"
        )
        await communicator.connect()
        
        # Watch game
        await communicator.send_json_to({
            'type': 'watch_game',
            'game_id': self.game.id
        })
        
        # Unwatch game
        await communicator.send_json_to({
            'type': 'unwatch_game',
            'game_id': self.game.id
        })
        
        # Create a bet (should not receive update)
        bet = await database_sync_to_async(GamblingBet.objects.create)(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )
        
        # Check no message received
        with self.assertRaises(TimeoutError):
            await communicator.receive_json_from()
        
        await communicator.disconnect()

    async def test_receive_invalid_message(self):
        communicator = WebsocketCommunicator(
            self.application,
            f"/ws/gambling/"
        )
        await communicator.connect()
        
        # Send invalid message type
        await communicator.send_json_to({
            'type': 'invalid_type',
            'game_id': self.game.id
        })
        
        # Should receive error message
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'error')
        self.assertIn('Invalid message type', response['message'])
        
        await communicator.disconnect()

    async def test_game_completion_notification(self):
        communicator = WebsocketCommunicator(
            self.application,
            f"/ws/gambling/"
        )
        await communicator.connect()
        
        # Watch game
        await communicator.send_json_to({
            'type': 'watch_game',
            'game_id': self.game.id
        })
        
        # Complete game
        self.game.status = 'completed'
        self.game.result = {'number': 6}
        await database_sync_to_async(self.game.save)()
        
        # Receive game completion notification
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'game_completed')
        self.assertEqual(response['game_id'], self.game.id)
        self.assertIn('result', response['data'])
        
        await communicator.disconnect()

    async def test_multiple_clients(self):
        # Connect first client
        communicator1 = WebsocketCommunicator(
            self.application,
            f"/ws/gambling/"
        )
        await communicator1.connect()
        
        # Connect second client
        communicator2 = WebsocketCommunicator(
            self.application,
            f"/ws/gambling/"
        )
        await communicator2.connect()
        
        # Both watch the game
        await communicator1.send_json_to({
            'type': 'watch_game',
            'game_id': self.game.id
        })
        await communicator2.send_json_to({
            'type': 'watch_game',
            'game_id': self.game.id
        })
        
        # Create a bet
        bet = await database_sync_to_async(GamblingBet.objects.create)(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )
        
        # Both should receive update
        response1 = await communicator1.receive_json_from()
        response2 = await communicator2.receive_json_from()
        
        self.assertEqual(response1['type'], 'game_update')
        self.assertEqual(response2['type'], 'game_update')
        
        await communicator1.disconnect()
        await communicator2.disconnect() 