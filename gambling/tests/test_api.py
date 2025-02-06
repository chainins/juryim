from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import json
from ..models import GamblingGame, GamblingBet

User = get_user_model()

class GamblingAPITest(TestCase):
    def setUp(self):
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

    def test_place_bet_api(self):
        url = reverse('gambling:place_bet_api', args=[self.game.id])
        data = {
            'amount': '0.00100000',
            'bet_data': {'number': 6}
        }
        
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('bet_id', response_data)
        self.assertIn('fee_amount', response_data)

    def test_game_status_api(self):
        url = reverse('gambling:game_status_api', args=[self.game.id])
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'active')
        self.assertEqual(data['total_bets'], '0.00000000')
        self.assertEqual(data['total_players'], 0)

    def test_user_bets_api(self):
        # Create some bets
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
        
        url = reverse('gambling:user_bets_api')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['bets']), 2)
        self.assertEqual(data['total_active_bets'], '0.00300000')

    def test_invalid_bet_data(self):
        url = reverse('gambling:place_bet_api', args=[self.game.id])
        
        # Invalid amount
        data = {
            'amount': '0.00000001',
            'bet_data': {'number': 6}
        }
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        # Invalid bet data
        data = {
            'amount': '0.00100000',
            'bet_data': {'number': 7}
        }
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_game_not_found(self):
        url = reverse('gambling:place_bet_api', args=[99999])
        data = {
            'amount': '0.00100000',
            'bet_data': {'number': 6}
        }
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_access(self):
        self.client.logout()
        
        # Try to place bet
        url = reverse('gambling:place_bet_api', args=[self.game.id])
        data = {
            'amount': '0.00100000',
            'bet_data': {'number': 6}
        }
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
        
        # Try to get game status
        url = reverse('gambling:game_status_api', args=[self.game.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_game_statistics_api(self):
        # Create some bets
        GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )
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
        
        url = reverse('gambling:game_statistics_api', args=[self.game.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['total_bets'], '0.00300000')
        self.assertEqual(data['total_players'], 2)
        self.assertEqual(data['total_fees'], '0.00003000')

    def test_concurrent_bets(self):
        url = reverse('gambling:place_bet_api', args=[self.game.id])
        data = {
            'amount': '0.00100000',
            'bet_data': {'number': 6}
        }
        
        # Place multiple bets quickly
        responses = []
        for _ in range(5):
            response = self.client.post(
                url,
                json.dumps(data),
                content_type='application/json'
            )
            responses.append(response)
        
        # Verify all bets were successful
        for response in responses:
            self.assertEqual(response.status_code, 200)
        
        # Verify total bets
        self.assertEqual(
            GamblingBet.objects.filter(game=self.game).count(),
            5
        ) 