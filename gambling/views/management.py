from django.views.generic import ListView, DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from ..models import GamblingGame, GamblingBet, GamblingTransaction

class GameManagementView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'gambling.manage_games'
    template_name = 'gambling/management/game_list.html'
    context_object_name = 'games'
    
    def get_queryset(self):
        return GamblingGame.objects.with_stats()

class BetManagementView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'gambling.manage_bets'
    model = GamblingBet
    template_name = 'gambling/management/bet_list.html'

class TransactionManagementView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'gambling.manage_transactions'
    model = GamblingTransaction
    template_name = 'gambling/management/transaction_list.html' 