from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

class GamblingNotifier:
    @staticmethod
    def notify_game_created(game):
        """Notify about new game creation"""
        try:
            # WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "gambling",
                {
                    "type": "game_update",
                    "game_id": game.id,
                    "data": {
                        "action": "created",
                        "title": game.title,
                        "game_type": game.game_type
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error sending game creation notification: {e}")
    
    @staticmethod
    def notify_game_ending_soon(game):
        """Notify users about game ending soon"""
        try:
            # Email notifications
            bet_users = game.gamblingbet_set.values_list(
                'user__email', flat=True
            ).distinct()
            
            for email in bet_users:
                context = {
                    'game': game,
                    'game_url': settings.SITE_URL + reverse(
                        'gambling:game_detail',
                        args=[game.id]
                    )
                }
                
                html_message = render_to_string(
                    'gambling/email/game_ending_soon.html',
                    context
                )
                
                send_mail(
                    subject=f"Game Ending Soon: {game.title}",
                    message="",
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True
                )
            
            # WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"game_{game.id}",
                {
                    "type": "game_update",
                    "game_id": game.id,
                    "data": {
                        "action": "ending_soon",
                        "time_remaining": game.time_remaining
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error sending game ending notification: {e}")
    
    @staticmethod
    def notify_game_completed(game):
        """Notify about game completion"""
        try:
            # Email notifications
            bet_users = game.gamblingbet_set.values_list(
                'user__email', flat=True
            ).distinct()
            
            for email in bet_users:
                context = {
                    'game': game,
                    'game_url': settings.SITE_URL + reverse(
                        'gambling:game_detail',
                        args=[game.id]
                    )
                }
                
                html_message = render_to_string(
                    'gambling/email/game_completed.html',
                    context
                )
                
                send_mail(
                    subject=f"Game Completed: {game.title}",
                    message="",
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True
                )
            
            # WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"game_{game.id}",
                {
                    "type": "game_completed",
                    "game_id": game.id,
                    "data": {
                        "result": game.result
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error sending game completion notification: {e}")
    
    @staticmethod
    def notify_bet_placed(bet):
        """Notify about new bet placement"""
        try:
            # Email notification
            context = {
                'bet': bet,
                'game_url': settings.SITE_URL + reverse(
                    'gambling:game_detail',
                    args=[bet.game.id]
                )
            }
            
            html_message = render_to_string(
                'gambling/email/bet_placed.html',
                context
            )
            
            send_mail(
                subject=f"Bet Placed: {bet.game.title}",
                message="",
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[bet.user.email],
                fail_silently=True
            )
            
            # WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"game_{bet.game.id}",
                {
                    "type": "bet_placed",
                    "game_id": bet.game.id,
                    "data": {
                        "amount": str(bet.amount),
                        "total_pool": str(bet.game.total_pool)
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error sending bet placement notification: {e}")
    
    @staticmethod
    def notify_bet_result(bet):
        """Notify about bet result"""
        try:
            # Email notification
            context = {
                'bet': bet,
                'game_url': settings.SITE_URL + reverse(
                    'gambling:game_detail',
                    args=[bet.game.id]
                )
            }
            
            html_message = render_to_string(
                'gambling/email/bet_result.html',
                context
            )
            
            send_mail(
                subject=f"Bet Result: {bet.game.title}",
                message="",
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[bet.user.email],
                fail_silently=True
            )
            
            # WebSocket notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{bet.user.id}",
                {
                    "type": "bet_result",
                    "bet_id": bet.id,
                    "data": {
                        "status": bet.status,
                        "win_amount": str(bet.win_amount) if bet.win_amount else "0"
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error sending bet result notification: {e}") 