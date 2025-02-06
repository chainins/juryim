from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from .models import GamblingBet
from .exceptions import (
    RateLimitExceededError,
    GameClosedError,
    InvalidGameStateError
)

def require_active_game(view_func):
    """Decorator to ensure game is active"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        game = kwargs.get('game')
        if not game or game.status != 'active':
            messages.error(request, "This game is not active.")
            return redirect('gambling:game_list')
        return view_func(request, *args, **kwargs)
    return wrapper

def check_betting_limits(view_func):
    """Decorator to check betting limits"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        
        # Check bets per minute
        recent_bets = GamblingBet.objects.filter(
            user=user,
            placed_at__gte=timezone.now() - timezone.timedelta(minutes=1)
        ).count()
        
        if recent_bets >= 5:
            messages.error(
                request,
                "You are placing bets too frequently. Please wait."
            )
            return redirect('gambling:game_list')
        
        # Check daily bet limit
        daily_bets = GamblingBet.objects.filter(
            user=user,
            placed_at__date=timezone.now().date()
        ).count()
        
        if daily_bets >= 100:
            messages.error(
                request,
                "You have reached your daily betting limit."
            )
            return redirect('gambling:game_list')
            
        return view_func(request, *args, **kwargs)
    return wrapper

def require_game_owner(view_func):
    """Decorator to ensure user owns the game"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        game = kwargs.get('game')
        if not game or game.created_by != request.user:
            raise PermissionDenied(
                "You do not have permission to manage this game."
            )
        return view_func(request, *args, **kwargs)
    return wrapper

def handle_gambling_errors(view_func):
    """Decorator to handle gambling-specific exceptions"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except RateLimitExceededError as e:
            messages.error(request, str(e))
            return redirect('gambling:game_list')
        except GameClosedError:
            messages.error(request, "This game is no longer accepting bets.")
            return redirect('gambling:game_list')
        except InvalidGameStateError as e:
            messages.error(request, str(e))
            return redirect('gambling:game_list')
    return wrapper 