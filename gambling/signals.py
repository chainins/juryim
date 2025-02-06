from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal
from .models import GamblingGame, GamblingBet, GamblingTransaction
from financial.services import FinancialService
from .services import GamblingService
from .notifications import GamblingNotifier
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=GamblingGame)
def handle_game_completion(sender, instance, **kwargs):
    """Handle game completion and process results"""
    if instance.pk:  # Only for existing games
        old_instance = GamblingGame.objects.get(pk=instance.pk)
        if old_instance.status != 'completed' and instance.status == 'completed':
            # Process winning bets
            winning_bets = instance.calculate_winner()
            if winning_bets:
                total_winning_amount = sum(bet.amount for bet in winning_bets)
                if total_winning_amount > 0:
                    win_multiplier = instance.total_pool / total_winning_amount
                    
                    for bet in winning_bets:
                        win_amount = (bet.amount * win_multiplier).quantize(Decimal('0.00000001'))
                        bet.status = 'won'
                        bet.result_time = timezone.now()
                        bet.save()
                        
                        # Create win transaction
                        GamblingTransaction.objects.create(
                            bet=bet,
                            transaction_type='bet_win',
                            amount=win_amount
                        )
                        
                        # Credit user's account
                        FinancialService.create_transaction(
                            account=bet.user.financial_account,
                            transaction_type='bet_win',
                            amount=win_amount,
                            description=f'Win from game {instance.title}'
                        )
            
            # Process losing bets
            losing_bets = GamblingBet.objects.filter(
                game=instance,
                status='placed'
            )
            for bet in losing_bets:
                bet.status = 'lost'
                bet.result_time = timezone.now()
                bet.save()

@receiver(post_save, sender=GamblingGame)
def handle_game_status_change(sender, instance, created, **kwargs):
    """Handle game status changes"""
    if not created and instance.tracker.has_changed('status'):
        old_status = instance.tracker.previous('status')
        new_status = instance.status
        
        if old_status == 'active' and new_status == 'completed':
            # Process game completion
            try:
                GamblingService.process_game_completion(instance)
            except Exception as e:
                logger.error(f"Error processing game completion: {str(e)}")
                
            # Send notifications
            try:
                GamblingNotifier.notify_game_completed(instance)
            except Exception as e:
                logger.error(f"Error sending game completion notifications: {str(e)}")

@receiver(post_save, sender=GamblingBet)
def handle_bet_placed(sender, instance, created, **kwargs):
    """Handle new bet placement"""
    if created:
        try:
            # Update game statistics
            GamblingService.update_game_stats(instance.game)
            
            # Send notification
            GamblingNotifier.notify_bet_placed(instance)
        except Exception as e:
            logger.error(f"Error handling new bet: {str(e)}")

@receiver(pre_save, sender=GamblingBet)
def handle_bet_status_change(sender, instance, **kwargs):
    """Handle bet status changes"""
    if instance.pk:  # Only for existing bets
        try:
            old_instance = GamblingBet.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                if instance.status in ['won', 'lost']:
                    # Process bet result
                    GamblingService.process_bet_result(instance)
                    
                    # Send notification
                    GamblingNotifier.notify_bet_result(instance)
        except GamblingBet.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Error handling bet status change: {str(e)}")

@receiver(post_save, sender=GamblingGame)
def handle_game_timing(sender, instance, created, **kwargs):
    """Handle game timing events"""
    if instance.status == 'active':
        now = timezone.now()
        
        # Check if game should be marked as completed
        if instance.end_time <= now:
            try:
                GamblingService.complete_game(instance)
            except Exception as e:
                logger.error(f"Error completing expired game: {str(e)}")
        
        # Check if game is ending soon
        elif instance.end_time <= now + timezone.timedelta(minutes=5):
            try:
                GamblingNotifier.notify_game_ending_soon(instance)
            except Exception as e:
                logger.error(f"Error sending game ending soon notification: {str(e)}") 