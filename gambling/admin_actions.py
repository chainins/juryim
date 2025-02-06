from django.contrib import admin, messages
from django.utils import timezone
from .services import GamblingService

@admin.action(description="Complete selected games")
def complete_games(modeladmin, request, queryset):
    """Admin action to complete selected games"""
    completed = 0
    errors = 0
    
    for game in queryset.filter(status='active'):
        try:
            GamblingService.complete_game(game)
            completed += 1
        except Exception as e:
            errors += 1
            messages.error(
                request,
                f"Error completing game {game.id}: {str(e)}"
            )
    
    if completed:
        messages.success(
            request,
            f"Successfully completed {completed} games."
        )
    
    if errors:
        messages.warning(
            request,
            f"Failed to complete {errors} games. See error messages above."
        )

@admin.action(description="Cancel selected games")
def cancel_games(modeladmin, request, queryset):
    """Admin action to cancel selected games"""
    cancelled = 0
    errors = 0
    
    for game in queryset.filter(status='active'):
        try:
            GamblingService.cancel_game(game)
            cancelled += 1
        except Exception as e:
            errors += 1
            messages.error(
                request,
                f"Error cancelling game {game.id}: {str(e)}"
            )
    
    if cancelled:
        messages.success(
            request,
            f"Successfully cancelled {cancelled} games."
        )
    
    if errors:
        messages.warning(
            request,
            f"Failed to cancel {errors} games. See error messages above."
        )

@admin.action(description="Recalculate game statistics")
def recalculate_stats(modeladmin, request, queryset):
    """Admin action to recalculate game statistics"""
    updated = 0
    errors = 0
    
    for game in queryset:
        try:
            stats = GamblingService.calculate_game_stats(game)
            game.total_bets = stats['total_bets']
            game.unique_players = stats['unique_players']
            game.save(update_fields=['total_bets', 'unique_players'])
            updated += 1
        except Exception as e:
            errors += 1
            messages.error(
                request,
                f"Error updating stats for game {game.id}: {str(e)}"
            )
    
    if updated:
        messages.success(
            request,
            f"Successfully updated statistics for {updated} games."
        )
    
    if errors:
        messages.warning(
            request,
            f"Failed to update statistics for {errors} games. See error messages above."
        ) 