import django_filters
from django.db.models import Q
from django.utils import timezone
from .models import GamblingGame, GamblingBet

class GamblingGameFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(
        choices=GamblingGame.STATUS_CHOICES
    )
    game_type = django_filters.ChoiceFilter(
        choices=GamblingGame.GAME_TYPE_CHOICES
    )
    min_pool = django_filters.NumberFilter(
        field_name='total_pool',
        lookup_expr='gte'
    )
    max_pool = django_filters.NumberFilter(
        field_name='total_pool',
        lookup_expr='lte'
    )
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )
    search = django_filters.CharFilter(method='search_filter')
    
    class Meta:
        model = GamblingGame
        fields = [
            'status', 'game_type', 'created_by',
            'min_pool', 'max_pool',
            'created_after', 'created_before'
        ]
    
    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value)
        )

class GamblingBetFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(
        choices=GamblingBet.STATUS_CHOICES
    )
    game_type = django_filters.ChoiceFilter(
        field_name='game__game_type',
        choices=GamblingGame.GAME_TYPE_CHOICES
    )
    min_amount = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='gte'
    )
    max_amount = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='lte'
    )
    placed_after = django_filters.DateTimeFilter(
        field_name='placed_at',
        lookup_expr='gte'
    )
    placed_before = django_filters.DateTimeFilter(
        field_name='placed_at',
        lookup_expr='lte'
    )
    
    class Meta:
        model = GamblingBet
        fields = [
            'status', 'game_type', 'user',
            'game', 'min_amount', 'max_amount',
            'placed_after', 'placed_before'
        ]

def active_games_filter(queryset):
    """Filter for active games"""
    now = timezone.now()
    return queryset.filter(
        status='active',
        start_time__lte=now,
        end_time__gt=now
    )

def completed_games_filter(queryset):
    """Filter for completed games"""
    return queryset.filter(
        status='completed'
    ).order_by('-end_time')

def user_active_bets_filter(queryset, user):
    """Filter for user's active bets"""
    return queryset.filter(
        user=user,
        status='placed',
        game__status='active'
    )

def user_completed_bets_filter(queryset, user):
    """Filter for user's completed bets"""
    return queryset.filter(
        user=user,
        status__in=['won', 'lost']
    ).order_by('-result_time') 