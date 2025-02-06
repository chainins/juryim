from rest_framework import permissions
from django.utils import timezone
from .models import GamblingBet
from .exceptions import RateLimitExceededError

class CanPlaceBets(permissions.BasePermission):
    """Permission to check if user can place bets"""
    
    message = "You are not allowed to place bets."
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            return False
            
        # Check if user is banned from betting
        if hasattr(user, 'gambling_profile'):
            if user.gambling_profile.is_banned:
                self.message = "Your betting privileges have been suspended."
                return False
        
        # Check rate limits
        try:
            self._check_rate_limits(user)
        except RateLimitExceededError as e:
            self.message = str(e)
            return False
            
        return True
    
    def _check_rate_limits(self, user):
        # Check bets per minute
        recent_bets = GamblingBet.objects.filter(
            user=user,
            placed_at__gte=timezone.now() - timezone.timedelta(minutes=1)
        ).count()
        
        if recent_bets >= 5:
            raise RateLimitExceededError(
                "You are placing bets too frequently. Please wait."
            )
        
        # Check daily bet limit
        daily_bets = GamblingBet.objects.filter(
            user=user,
            placed_at__date=timezone.now().date()
        ).count()
        
        if daily_bets >= 100:
            raise RateLimitExceededError(
                "You have reached your daily betting limit."
            )

class IsGameActive(permissions.BasePermission):
    """Permission to check if game is active"""
    
    message = "This game is not active."
    
    def has_object_permission(self, request, view, obj):
        return obj.status == 'active'

class IsGameOwner(permissions.BasePermission):
    """Permission to check if user owns the game"""
    
    message = "You do not have permission to manage this game."
    
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user

class CanViewGameDetails(permissions.BasePermission):
    """Permission to view detailed game information"""
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin can view all games
        if user.is_staff:
            return True
            
        # Game creator can view their games
        if obj.created_by == user:
            return True
            
        # Users with active bets can view the game
        if user.is_authenticated:
            has_bet = GamblingBet.objects.filter(
                user=user,
                game=obj
            ).exists()
            return has_bet
            
        return False 