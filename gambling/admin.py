from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import GamblingGame, GamblingBet, GamblingTransaction

@admin.register(GamblingGame)
class GamblingGameAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'game_type', 'status', 'total_pool',
        'total_bets', 'unique_players', 'start_time',
        'end_time', 'created_at'
    ]
    list_filter = ['status', 'game_type', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = [
        'total_pool', 'total_bets', 'unique_players',
        'created_at', 'result'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'game_type', 'status')
        }),
        ('Game Settings', {
            'fields': (
                'minimum_single_bet', 'maximum_single_bet',
                'fee_percentage'
            )
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time')
        }),
        ('Statistics', {
            'fields': (
                'total_pool', 'total_bets', 'unique_players',
                'result', 'created_at'
            )
        })
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.with_stats()

@admin.register(GamblingBet)
class GamblingBetAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'game_link', 'user_link', 'amount',
        'fee_amount', 'status', 'placed_at'
    ]
    list_filter = ['status', 'placed_at', 'game__game_type']
    search_fields = [
        'user__username', 'game__title',
        'bet_data', 'transaction_id'
    ]
    readonly_fields = [
        'placed_at', 'result_time', 'transaction_id',
        'win_amount'
    ]
    
    def game_link(self, obj):
        url = reverse(
            'admin:gambling_gamblinggame_change',
            args=[obj.game.id]
        )
        return format_html(
            '<a href="{}">{}</a>',
            url, obj.game.title
        )
    game_link.short_description = 'Game'
    
    def user_link(self, obj):
        url = reverse(
            'admin:auth_user_change',
            args=[obj.user.id]
        )
        return format_html(
            '<a href="{}">{}</a>',
            url, obj.user.username
        )
    user_link.short_description = 'User'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(GamblingTransaction)
class GamblingTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'bet_link', 'transaction_type',
        'amount', 'timestamp'
    ]
    list_filter = ['transaction_type', 'timestamp']
    search_fields = [
        'bet__game__title',
        'bet__user__username',
        'bet__user__email'
    ]
    readonly_fields = ['timestamp']
    
    def bet_link(self, obj):
        url = reverse('admin:gambling_gamblingbet_change', args=[obj.bet.id])
        return format_html('<a href="{}">{}</a>', url, obj.bet.id)
    bet_link.short_description = 'Bet' 