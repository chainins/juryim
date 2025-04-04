from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import GamblingGame, GamblingBet, GamblingTransaction, Game, Bet

@admin.register(GamblingGame)
class GamblingGameAdmin(admin.ModelAdmin):
    list_display = ('title', 'game_type', 'status', 'get_total_pool', 'get_total_bets', 'get_unique_players')
    list_filter = ('game_type', 'status', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('get_total_pool', 'get_total_bets', 'get_unique_players')

    def get_total_pool(self, obj):
        return obj.bets.aggregate(total=models.Sum('amount'))['total'] or 0
    get_total_pool.short_description = 'Total Pool'

    def get_total_bets(self, obj):
        return obj.bets.count()
    get_total_bets.short_description = 'Total Bets'

    def get_unique_players(self, obj):
        return obj.bets.values('user').distinct().count()
    get_unique_players.short_description = 'Unique Players'

@admin.register(GamblingBet)
class GamblingBetAdmin(admin.ModelAdmin):
    list_display = ('game', 'user', 'amount', 'status', 'placed_at')
    list_filter = ('status', 'placed_at')
    search_fields = ('user__username', 'game__title')
    readonly_fields = ('placed_at', 'result_time')
    
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
    list_display = ('bet', 'transaction_type', 'amount', 'timestamp')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('bet__user__username', 'bet__game__title')
    readonly_fields = ('timestamp',)
    
    def bet_link(self, obj):
        url = reverse('admin:gambling_gamblingbet_change', args=[obj.bet.id])
        return format_html('<a href="{}">{}</a>', url, obj.bet.id)
    bet_link.short_description = 'Bet'

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_bet', 'max_bet', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'amount', 'outcome', 'created_at')
    search_fields = ('user__username', 'game__name')
    list_filter = ('created_at', 'outcome') 