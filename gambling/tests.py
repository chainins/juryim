from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from .models import GamblingGame, GamblingBet
from .services import GamblingService
from .utils import (
    generate_game_result, calculate_win_amount,
    validate_bet_data, check_win
)

User = get_user_model()

class GamblingGameTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
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

    def test_game_creation(self):
        self.assertEqual(self.game.title, 'Test Game')
        self.assertEqual(self.game.status, 'active')
        self.assertEqual(self.game.total_pool, Decimal('0'))

    def test_place_bet(self):
        bet_data = {'number': 6}
        bet_amount = Decimal('0.1')
        
        bet = GamblingService.place_bet(
            game=self.game,
            user=self.user,
            amount=bet_amount,
            bet_data=bet_data
        )
        
        self.assertEqual(bet.amount, bet_amount)
        self.assertEqual(bet.status, 'placed')
        self.assertEqual(bet.bet_data, bet_data)

    def test_invalid_bet_data(self):
        bet_data = {'number': 7}  # Invalid dice number
        bet_amount = Decimal('0.1')
        
        with self.assertRaises(ValueError):
            GamblingService.place_bet(
                game=self.game,
                user=self.user,
                amount=bet_amount,
                bet_data=bet_data
            )

    def test_game_completion(self):
        # Place some bets
        bet1 = GamblingService.place_bet(
            game=self.game,
            user=self.user,
            amount=Decimal('0.1'),
            bet_data={'number': 6}
        )
        
        bet2 = GamblingService.place_bet(
            game=self.game,
            user=self.user,
            amount=Decimal('0.2'),
            bet_data={'number': 3}
        )
        
        # Complete the game
        GamblingService.complete_game(self.game)
        
        # Refresh from db
        self.game.refresh_from_db()
        bet1.refresh_from_db()
        bet2.refresh_from_db()
        
        self.assertEqual(self.game.status, 'completed')
        self.assertIn(bet1.status, ['won', 'lost'])
        self.assertIn(bet2.status, ['won', 'lost'])

class GamblingUtilsTests(TestCase):
    def test_generate_game_result(self):
        dice_result = generate_game_result('dice')
        self.assertIn('number', dice_result)
        self.assertTrue(1 <= dice_result['number'] <= 6)
        
        coin_result = generate_game_result('coin')
        self.assertIn('side', coin_result)
        self.assertIn(coin_result['side'], ['heads', 'tails'])
        
        roulette_result = generate_game_result('roulette')
        self.assertIn('number', roulette_result)
        self.assertTrue(0 <= roulette_result['number'] <= 36)

    def test_calculate_win_amount(self):
        bet_amount = Decimal('1.0')
        total_pool = Decimal('10.0')
        winning_bets_total = Decimal('2.0')
        
        win_amount = calculate_win_amount(
            bet_amount,
            total_pool,
            winning_bets_total
        )
        
        self.assertEqual(win_amount, Decimal('5.0'))

    def test_validate_bet_data(self):
        # Test valid data
        self.assertTrue(validate_bet_data('dice', {'number': 6}))
        self.assertTrue(validate_bet_data('coin', {'side': 'heads'}))
        self.assertTrue(validate_bet_data('roulette', {'number': 36}))
        
        # Test invalid data
        self.assertFalse(validate_bet_data('dice', {'number': 7}))
        self.assertFalse(validate_bet_data('coin', {'side': 'invalid'}))
        self.assertFalse(validate_bet_data('roulette', {'number': 37}))

    def test_check_win(self):
        # Test dice
        self.assertTrue(check_win(
            {'number': 6},
            {'number': 6},
            'dice'
        ))
        self.assertFalse(check_win(
            {'number': 6},
            {'number': 5},
            'dice'
        ))
        
        # Test coin
        self.assertTrue(check_win(
            {'side': 'heads'},
            {'side': 'heads'},
            'coin'
        ))
        self.assertFalse(check_win(
            {'side': 'heads'},
            {'side': 'tails'},
            'coin'
        ))
        
        # Test roulette
        self.assertTrue(check_win(
            {'number': 0},
            {'number': 0},
            'roulette'
        ))
        self.assertFalse(check_win(
            {'number': 0},
            {'number': 1},
            'roulette'
        )) 