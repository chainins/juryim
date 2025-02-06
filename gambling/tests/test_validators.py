from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from ..validators import (
    validate_game_duration,
    validate_bet_limits,
    validate_fee_percentage,
    validate_future_datetime,
    validate_game_type,
    validate_bet_data,
    validate_bet_amount
)
from ..models import GamblingGame

class GamblingValidatorsTest(TestCase):
    def test_validate_game_duration(self):
        # Valid duration
        start_time = timezone.now() + timezone.timedelta(minutes=5)
        end_time = start_time + timezone.timedelta(hours=1)
        validate_game_duration(start_time, end_time)
        
        # Too short duration
        end_time = start_time + timezone.timedelta(minutes=3)
        with self.assertRaises(ValidationError):
            validate_game_duration(start_time, end_time)
        
        # Too long duration
        end_time = start_time + timezone.timedelta(days=2)
        with self.assertRaises(ValidationError):
            validate_game_duration(start_time, end_time)
        
        # End time before start time
        end_time = start_time - timezone.timedelta(hours=1)
        with self.assertRaises(ValidationError):
            validate_game_duration(start_time, end_time)

    def test_validate_bet_limits(self):
        # Valid limits
        validate_bet_limits(
            Decimal('0.00000100'),
            Decimal('0.10000000')
        )
        
        # Minimum greater than maximum
        with self.assertRaises(ValidationError):
            validate_bet_limits(
                Decimal('0.20000000'),
                Decimal('0.10000000')
            )
        
        # Invalid minimum (too low)
        with self.assertRaises(ValidationError):
            validate_bet_limits(
                Decimal('0.00000001'),
                Decimal('0.10000000')
            )
        
        # Invalid maximum (too high)
        with self.assertRaises(ValidationError):
            validate_bet_limits(
                Decimal('0.00000100'),
                Decimal('100.00000000')
            )

    def test_validate_fee_percentage(self):
        # Valid fee percentage
        validate_fee_percentage(Decimal('1.0'))
        validate_fee_percentage(Decimal('5.5'))
        
        # Too low
        with self.assertRaises(ValidationError):
            validate_fee_percentage(Decimal('0.05'))
        
        # Too high
        with self.assertRaises(ValidationError):
            validate_fee_percentage(Decimal('15.0'))
        
        # Negative
        with self.assertRaises(ValidationError):
            validate_fee_percentage(Decimal('-1.0'))

    def test_validate_future_datetime(self):
        # Valid future time
        future_time = timezone.now() + timezone.timedelta(minutes=5)
        validate_future_datetime(future_time)
        
        # Past time
        past_time = timezone.now() - timezone.timedelta(minutes=5)
        with self.assertRaises(ValidationError):
            validate_future_datetime(past_time)

    def test_validate_game_type(self):
        # Valid game types
        validate_game_type('dice')
        validate_game_type('coin')
        validate_game_type('roulette')
        
        # Invalid game type
        with self.assertRaises(ValidationError):
            validate_game_type('invalid')

    def test_validate_bet_data(self):
        # Valid dice bet
        validate_bet_data('dice', {'number': 6})
        
        # Invalid dice number
        with self.assertRaises(ValidationError):
            validate_bet_data('dice', {'number': 7})
        
        # Valid coin bet
        validate_bet_data('coin', {'side': 'heads'})
        validate_bet_data('coin', {'side': 'tails'})
        
        # Invalid coin side
        with self.assertRaises(ValidationError):
            validate_bet_data('coin', {'side': 'invalid'})
        
        # Valid roulette bet
        validate_bet_data('roulette', {'number': 36})
        
        # Invalid roulette number
        with self.assertRaises(ValidationError):
            validate_bet_data('roulette', {'number': 37})
        
        # Missing required data
        with self.assertRaises(ValidationError):
            validate_bet_data('dice', {})
        
        # Invalid data structure
        with self.assertRaises(ValidationError):
            validate_bet_data('dice', {'invalid': 'data'})

    def test_validate_bet_amount(self):
        game = GamblingGame(
            minimum_single_bet=Decimal('0.00000100'),
            maximum_single_bet=Decimal('0.10000000')
        )
        
        # Valid amount
        validate_bet_amount(Decimal('0.00100000'), game)
        
        # Below minimum
        with self.assertRaises(ValidationError):
            validate_bet_amount(Decimal('0.00000001'), game)
        
        # Above maximum
        with self.assertRaises(ValidationError):
            validate_bet_amount(Decimal('1.00000000'), game)
        
        # Negative amount
        with self.assertRaises(ValidationError):
            validate_bet_amount(Decimal('-0.00100000'), game)
        
        # Zero amount
        with self.assertRaises(ValidationError):
            validate_bet_amount(Decimal('0'), game) 