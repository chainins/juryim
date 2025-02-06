from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum
from django.core.mail import send_mass_mail
from .models import GamblingGame, GamblingBet, GamblingTransaction
from tasks.models import ArbitrationTask
from tasks.services import TaskService
from django.db import transaction
import random
from financial.services import SecurityService
from django.core.cache import cache
from .utils import (
    generate_game_result,
    check_bet_result,
    calculate_win_multiplier
)
from .exceptions import (
    GameClosedError,
    InvalidGameStateError,
    TransactionError
)
from .notifications import GamblingNotifier
import logging

logger = logging.getLogger(__name__)

class GamblingService:
    @staticmethod
    def create_arbitration_for_game(game):
        """Create arbitration task for gambling game result"""
        arbitration = ArbitrationTask.objects.create(
            task=game,
            voting_options=game.betting_options,
            required_arbitrators=GamblingService.calculate_required_arbitrators(game),
            margin_requirement=game.minimum_total_bet * Decimal('0.05'),
            voting_deadline=game.end_time + timezone.timedelta(days=5)
        )
        
        arbitrators = TaskService.select_arbitrators(arbitration)
        TaskService.notify_arbitrators(arbitration, arbitrators)
        return arbitration

    @staticmethod
    def calculate_required_arbitrators(game):
        """Calculate required arbitrators based on total bet amount"""
        total_bets = GamblingBet.objects.filter(game=game).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        if total_bets < 1000:
            return 3
        elif total_bets < 10000:
            return 5
        else:
            return 7

    @staticmethod
    def process_game_result(game, result):
        """Process game result and distribute winnings"""
        if result == 'uncertain':
            return GamblingService.process_uncertain_result(game)
            
        winning_bets = GamblingBet.objects.filter(
            game=game,
            bet_option=result
        )
        
        total_bets = GamblingBet.objects.filter(game=game).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        fee_amount = total_bets * (game.fee_percentage / 100)
        prize_pool = total_bets - fee_amount
        
        winning_amount = winning_bets.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        if winning_amount > 0:
            for bet in winning_bets:
                payout = (bet.amount / winning_amount) * prize_pool
                bet.is_winner = True
                bet.payout_amount = payout
                bet.save()

    @staticmethod
    def process_uncertain_result(game):
        """Process refunds when result is uncertain"""
        bets = GamblingBet.objects.filter(game=game)
        fee_percentage = Decimal('0.01')  # 1% fee for uncertain results
        
        for bet in bets:
            refund_amount = bet.amount * (1 - fee_percentage)
            bet.payout_amount = refund_amount
            bet.save()

    @staticmethod
    @transaction.atomic
    def place_bet(game, user, amount, bet_data):
        """Place a bet on a game"""
        if game.status != 'active':
            raise GameClosedError("Game is not active")
            
        if game.end_time <= timezone.now():
            raise GameClosedError("Game has ended")
        
        # Create bet
        bet = GamblingBet.objects.create(
            game=game,
            user=user,
            amount=amount,
            bet_data=bet_data,
            fee_amount=GamblingService.calculate_fee(amount, game.fee_percentage)
        )
        
        # Update game pool
        game.total_pool += amount
        game.save(update_fields=['total_pool'])
        
        # Send notification
        try:
            GamblingNotifier.notify_bet_placed(bet)
        except Exception as e:
            logger.error(f"Error sending bet placement notification: {e}")
        
        return bet

    @staticmethod
    @transaction.atomic
    def complete_game(game):
        """Complete a game and process results"""
        if game.status != 'active':
            raise InvalidGameStateError("Game is not active")
        
        # Generate result
        result = generate_game_result(game.game_type)
        game.result = result
        game.status = 'completed'
        game.save()
        
        # Process bets
        bets = game.gamblingbet_set.filter(status='placed')
        for bet in bets:
            try:
                GamblingService.process_bet_result(bet, result)
            except Exception as e:
                logger.error(f"Error processing bet {bet.id}: {e}")
        
        # Send notifications
        try:
            GamblingNotifier.notify_game_completed(game)
        except Exception as e:
            logger.error(f"Error sending game completion notification: {e}")
        
        return game

    @staticmethod
    @transaction.atomic
    def process_bet_result(bet, game_result):
        """Process the result of a bet"""
        if bet.status != 'placed':
            raise InvalidGameStateError("Bet has already been processed")
        
        # Check if bet wins
        is_winner = check_bet_result(
            bet.bet_data,
            game_result,
            bet.game.game_type
        )
        
        if is_winner:
            # Calculate winnings
            multiplier = calculate_win_multiplier(
                bet.game.game_type,
                bet.bet_data
            )
            win_amount = bet.amount * multiplier
            
            bet.status = 'won'
            bet.win_amount = win_amount
        else:
            bet.status = 'lost'
            bet.win_amount = 0
        
        bet.result_time = timezone.now()
        bet.save()
        
        # Send notification
        try:
            GamblingNotifier.notify_bet_result(bet)
        except Exception as e:
            logger.error(f"Error sending bet result notification: {e}")
        
        return bet

    @staticmethod
    @transaction.atomic
    def cancel_game(game):
        """Cancel a game and refund bets"""
        if game.status not in ['pending', 'active']:
            raise InvalidGameStateError("Game cannot be cancelled")
        
        game.status = 'cancelled'
        game.save()
        
        # Refund bets
        bets = game.gamblingbet_set.filter(status='placed')
        for bet in bets:
            try:
                bet.status = 'refunded'
                bet.save()
            except Exception as e:
                logger.error(f"Error refunding bet {bet.id}: {e}")
        
        return game

    @staticmethod
    def generate_game_result(game):
        """Generate random result based on game type"""
        if game.game_type == 'dice':
            return {'number': random.randint(1, 6)}
        elif game.game_type == 'coin':
            return {'side': random.choice(['heads', 'tails'])}
        elif game.game_type == 'roulette':
            return {'number': random.randint(0, 36)}
        return None

    @staticmethod
    @transaction.atomic
    def create_game(data, user):
        """Create a new gambling game"""
        game = GamblingGame.objects.create(
            created_by=user,
            **data
        )
        
        # Send notification
        try:
            GamblingNotifier.notify_game_created(game)
        except Exception as e:
            logger.error(f"Error sending game creation notification: {e}")
        
        return game

    @staticmethod
    def calculate_fee(amount, fee_percentage):
        """Calculate fee amount based on bet amount and fee percentage"""
        return amount * (fee_percentage / 100)

    @staticmethod
    def validate_bet_data(game_type, bet_data):
        """Validate bet data based on game type"""
        if game_type == 'dice':
            number = bet_data.get('number')
            return isinstance(number, int) and 1 <= number <= 6
        # Add more game types as needed
        return False

    @staticmethod
    def process_game_result(game, result):
        """Process game result and update bets"""
        if game.status != 'active':
            return False
        
        game.result = result
        game.status = 'completed'
        game.save()
        return True 