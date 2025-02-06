from celery import shared_task
from django.utils import timezone
from django.db import transaction
from .models import GamblingGame, GamblingBet
from .services import GamblingService
from .utils import generate_game_result
from .notifications import GamblingNotifier
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_completed_games():
    """Process all completed games that haven't been processed yet"""
    try:
        expired_games = GamblingGame.objects.filter(
            status='active',
            end_time__lte=timezone.now()
        )
        
        for game in expired_games:
            try:
                with transaction.atomic():
                    GamblingService.complete_game(game)
                logger.info(f"Successfully completed game {game.id}")
            except Exception as e:
                logger.error(f"Error completing game {game.id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in process_completed_games task: {str(e)}")
        raise

@shared_task
def cleanup_expired_games():
    """Clean up old completed games data"""
    try:
        # Find games completed more than 30 days ago
        cutoff_date = timezone.now() - timezone.timedelta(days=30)
        old_games = GamblingGame.objects.filter(
            status='completed',
            end_time__lt=cutoff_date
        )
        
        for game in old_games:
            try:
                # Archive game data if needed
                # Delete game
                game.delete()
                logger.info(f"Cleaned up game {game.id}")
            except Exception as e:
                logger.error(f"Error cleaning up game {game.id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in cleanup_expired_games task: {str(e)}")
        raise

@shared_task
def update_game_statistics():
    """Update statistics for active games"""
    try:
        active_games = GamblingGame.objects.filter(status='active')
        
        for game in active_games:
            try:
                stats = GamblingService.calculate_game_stats(game)
                # Update game statistics
                game.total_bets = stats['total_bets']
                game.unique_players = stats['unique_players']
                game.save(update_fields=['total_bets', 'unique_players'])
                logger.info(f"Updated statistics for game {game.id}")
            except Exception as e:
                logger.error(f"Error updating stats for game {game.id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in update_game_statistics task: {str(e)}")
        raise

@shared_task
def process_bet_result(bet_id):
    """Process individual bet result"""
    try:
        bet = GamblingBet.objects.select_related('game').get(id=bet_id)
        
        if bet.status != 'placed':
            logger.warning(f"Bet {bet_id} is not in placed status")
            return
            
        if bet.game.status != 'completed':
            logger.warning(f"Game {bet.game.id} is not completed")
            return
            
        try:
            with transaction.atomic():
                GamblingService.process_bet_result(bet)
            logger.info(f"Processed result for bet {bet_id}")
        except Exception as e:
            logger.error(f"Error processing bet {bet_id}: {str(e)}")
            
    except GamblingBet.DoesNotExist:
        logger.error(f"Bet {bet_id} not found")
    except Exception as e:
        logger.error(f"Error in process_bet_result task: {str(e)}")
        raise

@shared_task
def send_game_notifications():
    """Send notifications for game events"""
    try:
        # Notify users about games ending soon
        ending_soon = GamblingGame.objects.filter(
            status='active',
            end_time__lte=timezone.now() + timezone.timedelta(minutes=5),
            end_time__gt=timezone.now()
        )
        
        for game in ending_soon:
            try:
                GamblingService.notify_game_ending_soon(game)
                logger.info(f"Sent ending soon notification for game {game.id}")
            except Exception as e:
                logger.error(f"Error sending notification for game {game.id}: {str(e)}")
                continue
                
        # Notify users about completed games
        just_completed = GamblingGame.objects.filter(
            status='completed',
            end_time__gte=timezone.now() - timezone.timedelta(minutes=5)
        )
        
        for game in just_completed:
            try:
                GamblingService.notify_game_completed(game)
                logger.info(f"Sent completion notification for game {game.id}")
            except Exception as e:
                logger.error(f"Error sending completion notification for game {game.id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in send_game_notifications task: {str(e)}")
        raise

@shared_task
def complete_expired_games():
    """Complete games that have expired"""
    now = timezone.now()
    expired_games = GamblingGame.objects.filter(
        status='active',
        end_time__lte=now
    )
    
    for game in expired_games:
        try:
            GamblingService.complete_game(game)
            logger.info(f"Completed expired game {game.id}")
        except Exception as e:
            logger.error(f"Error completing game {game.id}: {e}")

@shared_task
def notify_ending_soon_games():
    """Notify about games ending soon"""
    now = timezone.now()
    threshold = now + timezone.timedelta(minutes=5)
    
    ending_soon = GamblingGame.objects.filter(
        status='active',
        end_time__gt=now,
        end_time__lte=threshold,
        ending_notified=False
    )
    
    for game in ending_soon:
        try:
            GamblingNotifier.notify_game_ending_soon(game)
            game.ending_notified = True
            game.save(update_fields=['ending_notified'])
            logger.info(f"Sent ending soon notification for game {game.id}")
        except Exception as e:
            logger.error(f"Error sending ending notification for game {game.id}: {e}")

@shared_task
def cleanup_old_games():
    """Clean up old completed games"""
    cutoff = timezone.now() - timezone.timedelta(days=30)
    old_games = GamblingGame.objects.filter(
        status='completed',
        end_time__lt=cutoff
    )
    
    deleted_count = old_games.count()
    old_games.delete()
    
    logger.info(f"Cleaned up {deleted_count} old games") 