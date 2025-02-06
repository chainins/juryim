from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from ..utils import (
    calculate_fee,
    generate_game_result,
    check_winning_bet,
    calculate_payout_multiplier,
    format_bet_data_display,
    format_currency_amount
)
from ..models import GamblingGame, GamblingBet

User = get_user_model()

class GamblingUtilsTest(TestCase):
    def setUp(self):
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

    def test_calculate_fee(self):
        # Regular fee calculation
        amount = Decimal('1.00000000')
        fee_percentage = Decimal('1.0')
        fee = calculate_fee(amount, fee_percentage)
        self.assertEqual(fee, Decimal('0.01000000'))
        
        # Zero amount
        fee = calculate_fee(Decimal('0'), fee_percentage)
        self.assertEqual(fee, Decimal('0'))
        
        # Small amount
        fee = calculate_fee(Decimal('0.00000100'), fee_percentage)
        self.assertEqual(fee, Decimal('0.00000001'))

    def test_generate_game_result(self):
        # Dice game result
        result = generate_game_result('dice')
        self.assertIn('number', result)
        self.assertTrue(1 <= result['number'] <= 6)
        
        # Coin game result
        result = generate_game_result('coin')
        self.assertIn('side', result)
        self.assertIn(result['side'], ['heads', 'tails'])
        
        # Roulette game result
        result = generate_game_result('roulette')
        self.assertIn('number', result)
        self.assertTrue(0 <= result['number'] <= 36)
        
        # Invalid game type
        with self.assertRaises(ValueError):
            generate_game_result('invalid')

    def test_check_winning_bet(self):
        # Dice game
        self.assertTrue(check_winning_bet(
            'dice',
            {'number': 6},  # bet
            {'number': 6}   # result
        ))
        self.assertFalse(check_winning_bet(
            'dice',
            {'number': 6},  # bet
            {'number': 1}   # result
        ))
        
        # Coin game
        self.assertTrue(check_winning_bet(
            'coin',
            {'side': 'heads'},  # bet
            {'side': 'heads'}   # result
        ))
        self.assertFalse(check_winning_bet(
            'coin',
            {'side': 'heads'},  # bet
            {'side': 'tails'}   # result
        ))
        
        # Roulette game
        self.assertTrue(check_winning_bet(
            'roulette',
            {'number': 36},  # bet
            {'number': 36}   # result
        ))
        self.assertFalse(check_winning_bet(
            'roulette',
            {'number': 36},  # bet
            {'number': 0}    # result
        ))

    def test_calculate_payout_multiplier(self):
        # Dice game (6x)
        multiplier = calculate_payout_multiplier('dice')
        self.assertEqual(multiplier, Decimal('6'))
        
        # Coin game (2x)
        multiplier = calculate_payout_multiplier('coin')
        self.assertEqual(multiplier, Decimal('2'))
        
        # Roulette game (36x)
        multiplier = calculate_payout_multiplier('roulette')
        self.assertEqual(multiplier, Decimal('36'))
        
        # Invalid game type
        with self.assertRaises(ValueError):
            calculate_payout_multiplier('invalid')

    def test_format_bet_data_display(self):
        # Dice bet
        display = format_bet_data_display('dice', {'number': 6})
        self.assertEqual(display, 'Number: 6')
        
        # Coin bet
        display = format_bet_data_display('coin', {'side': 'heads'})
        self.assertEqual(display, 'Side: Heads')
        
        # Roulette bet
        display = format_bet_data_display('roulette', {'number': 36})
        self.assertEqual(display, 'Number: 36')
        
        # Invalid game type
        with self.assertRaises(ValueError):
            format_bet_data_display('invalid', {})
        
        # Invalid data structure
        with self.assertRaises(ValueError):
            format_bet_data_display('dice', {'invalid': 'data'})

    def test_format_currency_amount(self):
        # Regular amount
        formatted = format_currency_amount(Decimal('1.23456789'))
        self.assertEqual(formatted, '1.23456789')
        
        # Zero amount
        formatted = format_currency_amount(Decimal('0'))
        self.assertEqual(formatted, '0.00000000')
        
        # Small amount
        formatted = format_currency_amount(Decimal('0.00000001'))
        self.assertEqual(formatted, '0.00000001')
        
        # Large amount
        formatted = format_currency_amount(Decimal('1234.56789012'))
        self.assertEqual(formatted, '1234.56789012')
        
        # Negative amount
        formatted = format_currency_amount(Decimal('-1.23456789'))
        self.assertEqual(formatted, '-1.23456789') 