from .models import GamblingGame

def active_games(request):
    """Add active games count to context"""
    if request.user.is_authenticated:
        active_games_count = GamblingGame.objects.filter(
            status='active'
        ).count()
        
        user_active_bets = request.user.gamblingbet_set.filter(
            status='placed',
            game__status='active'
        ).count()
        
        return {
            'active_games_count': active_games_count,
            'user_active_bets': user_active_bets
        }
    return {}

def user_gambling_stats(request):
    """Add user gambling statistics to context"""
    if request.user.is_authenticated:
        total_bets = request.user.gamblingbet_set.count()
        won_bets = request.user.gamblingbet_set.filter(
            status='won'
        ).count()
        
        win_rate = (won_bets / total_bets * 100) if total_bets > 0 else 0
        
        return {
            'user_total_bets': total_bets,
            'user_won_bets': won_bets,
            'user_win_rate': round(win_rate, 2)
        }
    return {} 