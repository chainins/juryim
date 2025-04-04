from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q
from django.db import transaction
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import GamblingGame, GamblingBet, InvitedGambler, Game, Bet
from .forms import GamblingGameForm, PlaceBetForm, CreateGameForm
from .services import GamblingService
from .decorators import (
    require_active_game,
    check_betting_limits,
    handle_gambling_errors
)
import json
from decimal import Decimal
from financial.models import Transaction
from financial.utils import process_transaction

class GamblingViews:
    @staticmethod
    @login_required
    def create_game(request):
        """Create new gambling game"""
        if request.method == 'POST':
            form = CreateGameForm(request.POST)
            if form.is_valid():
                try:
                    game = GamblingService.create_game(
                        data=form.cleaned_data,
                        user=request.user
                    )
                    messages.success(request, "Game created successfully!")
                    return redirect('gambling:game_detail', game_id=game.id)
                except Exception as e:
                    messages.error(request, str(e))
        else:
            form = CreateGameForm()
        
        return render(request, 'gambling/create_game.html', {
            'form': form
        })

    @staticmethod
    @login_required
    def game_list(request):
        """Display list of gambling games"""
        games = Game.objects.all()
        return render(request, 'gambling/game_list.html', {'games': games})

    @staticmethod
    @login_required
    def place_bet(request, game_id):
        game = get_object_or_404(Game, id=game_id)
        
        if game.status != 'active':
            messages.error(request, 'This game is not accepting bets.')
            return redirect('gambling:game_detail', game_id=game.id)
            
        if game.is_specific_users and not InvitedGambler.objects.filter(
            game=game, user=request.user
        ).exists():
            messages.error(request, 'You are not invited to this game.')
            return redirect('gambling:game_list')
            
        if request.method == 'POST':
            amount = request.POST.get('amount')
            try:
                amount = float(amount)
                if amount < game.min_bet or amount > game.max_bet:
                    messages.error(request, f'Bet must be between {game.min_bet} and {game.max_bet}')
                    return redirect('gambling:game_detail', game_id=game.id)
                    
                # Use existing transaction processing
                transaction = process_transaction(
                    user=request.user,
                    amount=-amount,  # Negative for bet placement
                    transaction_type='BET',
                    description=f'Bet placed on {game.name}'
                )
                
                if transaction:
                    bet = Bet.objects.create(
                        user=request.user,
                        game=game,
                        amount=amount
                    )
                    messages.success(request, 'Bet placed successfully')
                    return redirect('gambling:game_list')
                else:
                    messages.error(request, 'Insufficient funds')
                    
            except ValueError:
                messages.error(request, 'Invalid bet amount')
        else:
            form = PlaceBetForm(game)
            
        return render(request, 'gambling/place_bet.html', {
            'form': form,
            'game': game
        })

    @staticmethod
    @login_required
    def game_detail(request, game_id):
        """Display game details and betting form"""
        game = get_object_or_404(
            GamblingGame.objects.with_stats(),
            id=game_id
        )
        
        user_bets = GamblingBet.objects.filter(
            game=game,
            user=request.user
        ).order_by('-placed_at')
        
        if request.method == 'POST' and game.status == 'active':
            form = PlaceBetForm(
                request.POST,
                game=game
            )
            if form.is_valid():
                try:
                    with transaction.atomic():
                        bet = GamblingService.place_bet(
                            game=game,
                            user=request.user,
                            amount=form.cleaned_data['amount'],
                            bet_data=form.cleaned_data['bet_data']
                        )
                    messages.success(request, "Bet placed successfully!")
                    return redirect('gambling:game_detail', game_id=game.id)
                except Exception as e:
                    messages.error(request, str(e))
        else:
            form = PlaceBetForm(game=game)
        
        return render(request, 'gambling/game_detail.html', {
            'game': game,
            'form': form,
            'user_bets': user_bets
        })

    @staticmethod
    @login_required
    def my_bets(request):
        """Display user's betting history"""
        status = request.GET.get('status')
        
        bets = GamblingBet.objects.filter(
            user=request.user
        ).select_related('game')
        
        if status == 'active':
            bets = bets.filter(
                status='placed',
                game__status='active'
            )
        elif status == 'completed':
            bets = bets.filter(
                status__in=['won', 'lost']
            )
        
        bets = bets.order_by('-placed_at')
        
        paginator = Paginator(bets, 20)
        page = request.GET.get('page')
        bets = paginator.get_page(page)
        
        return render(request, 'gambling/user_bets.html', {
            'bets': bets,
            'status': status
        })

    @staticmethod
    @login_required
    @require_active_game
    @check_betting_limits
    @handle_gambling_errors
    def place_bet_api(request, game_id):
        """API endpoint for placing bets"""
        game = get_object_or_404(GamblingGame, id=game_id)
        
        if request.method != 'POST':
            return JsonResponse({
                'error': 'Method not allowed'
            }, status=405)
        
        try:
            data = json.loads(request.body)
            amount = Decimal(data.get('amount'))
            bet_data = data.get('bet_data')
            
            bet = GamblingService.place_bet(
                game=game,
                user=request.user,
                amount=amount,
                bet_data=bet_data
            )
            
            return JsonResponse({
                'status': 'success',
                'bet_id': bet.id
            })
            
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({
                'error': 'Invalid request data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=400) 