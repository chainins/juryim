from django.db import models
from django.db.models import Count, Sum, Q
from django.utils import timezone

class GamblingGameManager(models.Manager):
    def with_stats(self):
        """Add statistics to game queryset"""
        return self.annotate(
            total_bets=Count('gamblingbet'),
            unique_players=Count('gamblingbet__user', distinct=True)
        )
    
    def active(self):
        """Get active games"""
        now = timezone.now()
        return self.filter(
            status='active',
            start_time__lte=now,
            end_time__gt=now
        )
    
    def completed(self):
        """Get completed games"""
        return self.filter(
            status='completed'
        ).order_by('-end_time')
    
    def pending(self):
        """Get pending games"""
        now = timezone.now()
        return self.filter(
            status='pending',
            start_time__gt=now
        )
    
    def by_type(self, game_type):
        """Get games by type"""
        return self.filter(game_type=game_type)
    
    def popular(self):
        """Get popular games based on bet count"""
        return self.annotate(
            bet_count=Count('gamblingbet')
        ).filter(
            status='active'
        ).order_by('-bet_count')

class GamblingBetManager(models.Manager):
    def active(self):
        """Get active bets"""
        return self.filter(
            status='placed',
            game__status='active'
        )
    
    def completed(self):
        """Get completed bets"""
        return self.filter(
            status__in=['won', 'lost']
        ).order_by('-result_time')
    
    def by_user(self, user):
        """Get bets for specific user"""
        return self.filter(user=user)
    
    def won(self):
        """Get winning bets"""
        return self.filter(status='won')
    
    def lost(self):
        """Get losing bets"""
        return self.filter(status='lost')
    
    def with_totals(self):
        """Add total amounts to bet queryset"""
        return self.annotate(
            total_won=Sum('win_amount', filter=Q(status='won')),
            total_lost=Sum('amount', filter=Q(status='lost')),
            total_fees=Sum('fee_amount')
        ) 