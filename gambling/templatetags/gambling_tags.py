from django import template
from django.utils import timezone
from ..models import GamblingGame, GamblingBet

register = template.Library()

@register.simple_tag
def get_user_game_stats(user, game):
    """Get user statistics for a specific game"""
    bets = GamblingBet.objects.filter(
        user=user,
        game=game
    )
    
    total_amount = sum(bet.amount for bet in bets)
    won_amount = sum(
        bet.win_amount for bet in bets.filter(status='won')
        if hasattr(bet, 'win_amount')
    )
    
    return {
        'total_bets': bets.count(),
        'total_amount': total_amount,
        'won_amount': won_amount
    }

@register.filter
def time_until_end(game):
    """Format time remaining until game ends"""
    if game.status != 'active':
        return 'Ended'
        
    remaining = game.end_time - timezone.now()
    
    if remaining.total_seconds() <= 0:
        return 'Ended'
        
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60
    seconds = remaining.seconds % 60
    
    if hours > 0:
        return f'{hours}h {minutes}m'
    elif minutes > 0:
        return f'{minutes}m {seconds}s'
    else:
        return f'{seconds}s'

@register.filter
def format_bet_data(bet_data, game_type):
    """Format bet data for display"""
    if game_type == 'dice':
        return f"Number {bet_data.get('number')}"
    elif game_type == 'coin':
        return bet_data.get('side').title()
    elif game_type == 'roulette':
        return f"Number {bet_data.get('number')}"
    return str(bet_data)

@register.inclusion_tag('gambling/tags/game_card.html')
def render_game_card(game, user=None):
    """Render a game card with user-specific information"""
    context = {
        'game': game,
        'user_stats': None
    }
    
    if user and user.is_authenticated:
        context['user_stats'] = get_user_game_stats(user, game)
    
    return context

@register.inclusion_tag('gambling/tags/bet_history.html')
def render_bet_history(user, limit=5):
    """Render user's recent bet history"""
    bets = GamblingBet.objects.filter(
        user=user
    ).select_related('game').order_by('-placed_at')[:limit]
    
    return {
        'bets': bets
    } 