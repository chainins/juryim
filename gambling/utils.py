import random
from decimal import Decimal, ROUND_DOWN
from django.conf import settings
from django.db import models
from django.utils import timezone
import hashlib

def generate_game_result(game_type, seed=None):
    """Generate random game result"""
    if seed is None:
        # Use current time as seed
        seed = str(timezone.now().timestamp())
    
    # Create deterministic random number generator
    hash_input = f"{seed}_{game_type}"
    hash_value = hashlib.sha256(hash_input.encode()).hexdigest()
    random.seed(hash_value)
    
    if game_type == 'dice':
        return {'number': random.randint(1, 6)}
        
    elif game_type == 'coin':
        return {'side': random.choice(['heads', 'tails'])}
        
    elif game_type == 'roulette':
        return {'number': random.randint(0, 36)}
        
    return None

def calculate_win_amount(bet_amount, total_pool, winning_bets_total):
    """Calculate win amount with proper decimal handling"""
    if winning_bets_total == 0:
        return Decimal('0')
    
    win_multiplier = total_pool / winning_bets_total
    win_amount = (bet_amount * win_multiplier).quantize(
        Decimal('0.00000001'),
        rounding=ROUND_DOWN
    )
    return win_amount

def calculate_fee(amount, percentage):
    """Calculate fee amount with minimum fee handling"""
    fee = (amount * Decimal(str(percentage)) / Decimal('100')).quantize(
        Decimal('0.00000001'),
        rounding=ROUND_DOWN
    )
    min_fee = Decimal(str(settings.GAMBLING_MIN_FEE))
    return max(fee, min_fee)

def validate_bet_data(game_type, bet_data):
    """Validate bet data for specific game type"""
    if game_type == 'dice':
        number = bet_data.get('number')
        return (
            isinstance(number, int) and 
            1 <= number <= 6
        )
        
    elif game_type == 'coin':
        side = bet_data.get('side')
        return side in ['heads', 'tails']
        
    elif game_type == 'roulette':
        number = bet_data.get('number')
        return (
            isinstance(number, int) and 
            0 <= number <= 36
        )
        
    return False

def format_currency(amount):
    """Format currency amount with proper decimal places"""
    return f"{amount:.8f}"

def check_win(bet_data, result, game_type):
    """Check if bet is winning based on game result"""
    if game_type == 'dice':
        return bet_data.get('number') == result.get('number')
    elif game_type == 'coin':
        return bet_data.get('side') == result.get('side')
    elif game_type == 'roulette':
        return bet_data.get('number') == result.get('number')
    return False

def calculate_win_probability(game_type, bet_data):
    """Calculate win probability for a bet"""
    if game_type == 'dice':
        return Decimal('0.166666667')  # 1/6
        
    elif game_type == 'coin':
        return Decimal('0.5')  # 1/2
        
    elif game_type == 'roulette':
        return Decimal('0.027027027')  # 1/37
        
    return Decimal('0')

def calculate_win_multiplier(game_type, bet_data):
    """Calculate win multiplier for a bet"""
    if game_type == 'dice':
        return Decimal('5.5')  # 6x - house edge
        
    elif game_type == 'coin':
        return Decimal('1.9')  # 2x - house edge
        
    elif game_type == 'roulette':
        return Decimal('35')  # 36x - house edge
        
    return Decimal('0')

def get_game_stats(game):
    """Get game statistics"""
    total_bets = game.gamblingbet_set.count()
    unique_players = game.gamblingbet_set.values('user').distinct().count()
    avg_bet = Decimal('0')
    if total_bets > 0:
        avg_bet = game.total_pool / total_bets
    
    return {
        'total_bets': total_bets,
        'unique_players': unique_players,
        'average_bet': avg_bet,
        'total_pool': game.total_pool,
        'fee_collected': game.gamblingbet_set.aggregate(
            total_fee=models.Sum('fee_amount')
        )['total_fee'] or Decimal('0')
    }

def is_valid_game_duration(start_time, end_time):
    """Validate game duration"""
    min_duration = timezone.timedelta(minutes=settings.GAMBLING_MIN_GAME_DURATION)
    max_duration = timezone.timedelta(hours=settings.GAMBLING_MAX_GAME_DURATION)
    duration = end_time - start_time
    
    return min_duration <= duration <= max_duration 

def check_bet_result(bet_data, game_result, game_type):
    """Check if bet wins based on game result"""
    if game_type == 'dice':
        return bet_data.get('number') == game_result.get('number')
        
    elif game_type == 'coin':
        return bet_data.get('side') == game_result.get('side')
        
    elif game_type == 'roulette':
        return bet_data.get('number') == game_result.get('number')
        
    return False

def calculate_fee_amount(amount, fee_percentage):
    """Calculate fee amount for a bet"""
    fee_decimal = Decimal(str(fee_percentage)) / Decimal('100')
    return (amount * fee_decimal).quantize(Decimal('0.00000001'))

def format_amount(amount):
    """Format decimal amount to 8 decimal places"""
    return Decimal(str(amount)).quantize(Decimal('0.00000001'))

def validate_game_duration(start_time, end_time):
    """Validate game duration is within allowed limits"""
    duration = end_time - start_time
    min_duration = timezone.timedelta(minutes=5)
    max_duration = timezone.timedelta(hours=24)
    
    return min_duration <= duration <= max_duration 