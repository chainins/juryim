from django.utils import timezone
from django.urls import resolve
from django.contrib import messages
from django.http import HttpResponseRedirect
import logging
from .models import GamblingGame

logger = logging.getLogger(__name__)

class GamblingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request
        if request.user.is_authenticated:
            self.process_active_games(request)
            
        response = self.get_response(request)
        
        # Process response
        return response
    
    def process_active_games(self, request):
        """Process active games for the current user"""
        try:
            # Get current URL name
            current_url = resolve(request.path_info).url_name
            
            # Only process on gambling-related pages
            if current_url and current_url.startswith('gambling:'):
                # Auto-complete expired games
                expired_games = GamblingGame.objects.filter(
                    status='active',
                    end_time__lte=timezone.now()
                )
                
                for game in expired_games:
                    try:
                        game.complete()
                    except Exception as e:
                        logger.error(f"Error auto-completing game {game.id}: {str(e)}")
                
                # Update request user's active bets count
                request.user.active_bets_count = request.user.gamblingbet_set.filter(
                    status='placed',
                    game__status='active'
                ).count()
                
        except Exception as e:
            logger.error(f"Error in GamblingMiddleware: {str(e)}")

class GamblingRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            self.check_rate_limits(request)
            
        return self.get_response(request)
    
    def check_rate_limits(self, request):
        """Check and enforce gambling rate limits"""
        try:
            current_url = resolve(request.path_info).url_name
            
            if current_url == 'gambling:place_bet':
                # Check bet frequency
                recent_bets = request.user.gamblingbet_set.filter(
                    placed_at__gte=timezone.now() - timezone.timedelta(minutes=1)
                ).count()
                
                if recent_bets >= 5:  # Max 5 bets per minute
                    raise RateLimitExceeded("Betting too frequently. Please wait.")
                
                # Check daily betting limit
                daily_bets = request.user.gamblingbet_set.filter(
                    placed_at__date=timezone.now().date()
                )
                
                daily_amount = sum(bet.amount for bet in daily_bets)
                if daily_amount >= request.user.daily_betting_limit:
                    raise RateLimitExceeded("Daily betting limit reached.")
                
        except RateLimitExceeded as e:
            messages.error(request, str(e))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        except Exception as e:
            logger.error(f"Error in GamblingRateLimitMiddleware: {str(e)}")

class RateLimitExceeded(Exception):
    pass 