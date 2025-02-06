from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import json
from ..models import GamblingGame, GamblingBet

User = get_user_model()

class GamblingViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
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
            fee_percentage=Decimal('1.0'),
            status='active'
        )

    def test_game_list_view(self):
        # Login required
        response = self.client.get(reverse('gambling:game_list'))
        self.assertEqual(response.status_code, 302)
        
        # After login
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('gambling:game_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gambling/game_list.html')
        self.assertContains(response, 'Test Game')

    def test_game_detail_view(self):
        # Login required
        response = self.client.get(
            reverse('gambling:game_detail', args=[self.game.id])
        )
        self.assertEqual(response.status_code, 302)
        
        # After login
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('gambling:game_detail', args=[self.game.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gambling/game_detail.html')
        self.assertContains(response, 'Test Game')

    def test_create_game_view(self):
        self.client.login(username='testuser', password='testpass123')
        
        # GET request
        response = self.client.get(reverse('gambling:create_game'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gambling/create_game.html')
        
        # POST request
        game_data = {
            'title': 'New Game',
            'description': 'New Description',
            'game_type': 'dice',
            'minimum_single_bet': '0.00000100',
            'maximum_single_bet': '0.10000000',
            'fee_percentage': '1.0',
            'start_time': (timezone.now() + timezone.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': (timezone.now() + timezone.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        }
        response = self.client.post(reverse('gambling:create_game'), game_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(GamblingGame.objects.filter(title='New Game').exists())

    def test_place_bet_api_view(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Valid bet
        bet_data = {
            'amount': '0.00100000',
            'bet_data': {'number': 6}
        }
        response = self.client.post(
            reverse('gambling:place_bet_api', args=[self.game.id]),
            json.dumps(bet_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('bet_id', data)
        
        # Invalid bet amount
        bet_data['amount'] = '0.00000001'
        response = self.client.post(
            reverse('gambling:place_bet_api', args=[self.game.id]),
            json.dumps(bet_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_user_bets_view(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Create a bet
        bet = GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )
        
        response = self.client.get(reverse('gambling:user_bets'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gambling/user_bets.html')
        self.assertContains(response, 'Test Game')
        self.assertContains(response, '0.00100000')

    def test_game_filter(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Create completed game
        GamblingGame.objects.create(
            title='Completed Game',
            description='Test Description',
            game_type='dice',
            created_by=self.user,
            start_time=timezone.now() + timezone.timedelta(minutes=5),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            minimum_single_bet=Decimal('0.00000100'),
            maximum_single_bet=Decimal('0.10000000'),
            fee_percentage=Decimal('1.0'),
            status='completed'
        )
        
        # Test active filter
        response = self.client.get(reverse('gambling:game_list'), {'status': 'active'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Game')
        self.assertNotContains(response, 'Completed Game')
        
        # Test completed filter
        response = self.client.get(reverse('gambling:game_list'), {'status': 'completed'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Completed Game')
        self.assertNotContains(response, 'Test Game')

    def test_invalid_game_id(self):
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(
            reverse('gambling:game_detail', args=[99999])
        )
        self.assertEqual(response.status_code, 404)
        
        response = self.client.post(
            reverse('gambling:place_bet_api', args=[99999]),
            json.dumps({'amount': '0.001', 'bet_data': {'number': 6}}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404) 