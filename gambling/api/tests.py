from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal
from ..models import GamblingGame, GamblingBet
from financial.models import FinancialAccount

User = get_user_model()

class GamblingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.account = FinancialAccount.objects.create(
            user=self.user,
            balance=Decimal('1.0')
        )
        self.client.force_authenticate(user=self.user)
        
        self.game = GamblingGame.objects.create(
            title='Test Game',
            description='Test Description',
            game_type='dice',
            creator=self.user,
            minimum_single_bet=Decimal('0.0001'),
            maximum_single_bet=Decimal('1.0'),
            fee_percentage=Decimal('2.0'),
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1)
        )

    def test_list_games(self):
        url = reverse('gambling-api:game-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_game_detail(self):
        url = reverse('gambling-api:game-detail', args=[self.game.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Game')

    def test_place_bet(self):
        url = reverse('gambling-api:game-place-bet', args=[self.game.id])
        data = {
            'amount': '0.1',
            'bet_data': {'number': 6}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GamblingBet.objects.count(), 1)

    def test_place_bet_insufficient_funds(self):
        url = reverse('gambling-api:game-place-bet', args=[self.game.id])
        data = {
            'amount': '2.0',  # More than account balance
            'bet_data': {'number': 6}
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(GamblingBet.objects.count(), 0)

    def test_place_bet_invalid_data(self):
        url = reverse('gambling-api:game-place-bet', args=[self.game.id])
        data = {
            'amount': '0.1',
            'bet_data': {'number': 7}  # Invalid dice number
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(GamblingBet.objects.count(), 0)

    def test_get_game_stats(self):
        # Place a bet first
        bet = GamblingBet.objects.create(
            game=self.game,
            user=self.user,
            amount=Decimal('0.1'),
            fee_amount=Decimal('0.002'),
            bet_data={'number': 6}
        )
        
        url = reverse('gambling-api:game-stats', args=[self.game.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_bets'], 1)
        self.assertEqual(response.data['unique_players'], 1)

    def test_list_user_bets(self):
        bet = GamblingBet.objects.create(
            game=self.game,
            user=self.user,
            amount=Decimal('0.1'),
            fee_amount=Decimal('0.002'),
            bet_data={'number': 6}
        )
        
        url = reverse('gambling-api:bet-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_active_bets(self):
        bet = GamblingBet.objects.create(
            game=self.game,
            user=self.user,
            amount=Decimal('0.1'),
            fee_amount=Decimal('0.002'),
            bet_data={'number': 6}
        )
        
        url = reverse('gambling-api:bet-active')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_completed_bets(self):
        bet = GamblingBet.objects.create(
            game=self.game,
            user=self.user,
            amount=Decimal('0.1'),
            fee_amount=Decimal('0.002'),
            bet_data={'number': 6},
            status='won'
        )
        
        url = reverse('gambling-api:bet-completed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) 