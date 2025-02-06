from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

def validate_future_datetime(value):
    """Validate that datetime is in the future"""
    if value <= timezone.now():
        raise ValidationError(
            "Datetime must be in the future."
        )

def validate_positive_decimal(value):
    """Validate that decimal is positive"""
    if value <= Decimal('0'):
        raise ValidationError(
            "Value must be positive."
        )

def validate_fee_percentage(value):
    """Validate fee percentage"""
    if value < Decimal('0.1') or value > Decimal('10.0'):
        raise ValidationError(
            "Fee percentage must be between 0.1 and 10.0."
        )

def validate_bet_limits(minimum, maximum):
    """Validate bet limits"""
    if minimum >= maximum:
        raise ValidationError(
            "Minimum bet must be less than maximum bet."
        )
    
    if minimum < Decimal('0.00000001'):
        raise ValidationError(
            "Minimum bet cannot be less than 0.00000001."
        )
    
    if maximum > Decimal('1.00000000'):
        raise ValidationError(
            "Maximum bet cannot be more than 1.00000000."
        )

def validate_game_duration(start_time, end_time):
    """Validate game duration"""
    if start_time >= end_time:
        raise ValidationError(
            "End time must be after start time."
        )
    
    duration = end_time - start_time
    min_duration = timezone.timedelta(minutes=5)
    max_duration = timezone.timedelta(hours=24)
    
    if duration < min_duration:
        raise ValidationError(
            "Game duration must be at least 5 minutes."
        )
    
    if duration > max_duration:
        raise ValidationError(
            "Game duration cannot exceed 24 hours."
        )

def validate_dice_number(value):
    """Validate dice number"""
    if not isinstance(value, int) or value < 1 or value > 6:
        raise ValidationError(
            "Dice number must be between 1 and 6."
        )

def validate_coin_side(value):
    """Validate coin side"""
    if value not in ['heads', 'tails']:
        raise ValidationError(
            "Coin side must be 'heads' or 'tails'."
        )

def validate_roulette_number(value):
    """Validate roulette number"""
    if not isinstance(value, int) or value < 0 or value > 36:
        raise ValidationError(
            "Roulette number must be between 0 and 36."
        )

def validate_game_type(game_type):
    """Validate game type is supported"""
    valid_types = ['dice', 'coin', 'roulette']
    if game_type not in valid_types:
        raise ValidationError(f"Invalid game type. Must be one of: {', '.join(valid_types)}")

def validate_bet_data_for_game_type(game_type, bet_data):
    """Validate bet data matches game type requirements"""
    if game_type == 'dice':
        number = bet_data.get('number')
        if not isinstance(number, int) or number < 1 or number > 6:
            raise ValidationError("Dice bet must include a number between 1 and 6")
            
    elif game_type == 'coin':
        side = bet_data.get('side')
        if side not in ['heads', 'tails']:
            raise ValidationError("Coin bet must be either 'heads' or 'tails'")
            
    elif game_type == 'roulette':
        number = bet_data.get('number')
        if not isinstance(number, int) or number < 0 or number > 36:
            raise ValidationError("Roulette bet must include a number between 0 and 36")
    else:
        raise ValidationError("Invalid game type") 