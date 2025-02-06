from django.core.management.base import BaseCommand
from django.utils import timezone
from gambling.models import GamblingGame
from gambling.services import GamblingService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Cleanup old completed games and process expired games'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to keep completed games'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        # Process expired games
        expired_games = GamblingGame.objects.filter(
            status='active',
            end_time__lte=timezone.now()
        )
        
        self.stdout.write(f"Found {expired_games.count()} expired games")
        
        for game in expired_games:
            try:
                if not dry_run:
                    GamblingService.complete_game(game)
                self.stdout.write(
                    self.style.SUCCESS(f"Completed game {game.id}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error completing game {game.id}: {str(e)}")
                )
                logger.error(f"Error completing game {game.id}: {str(e)}")
        
        # Cleanup old games
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        old_games = GamblingGame.objects.filter(
            status='completed',
            end_time__lt=cutoff_date
        )
        
        self.stdout.write(
            f"Found {old_games.count()} old games to clean up"
        )
        
        for game in old_games:
            try:
                if not dry_run:
                    game.delete()
                self.stdout.write(
                    self.style.SUCCESS(f"Deleted game {game.id}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error deleting game {game.id}: {str(e)}")
                )
                logger.error(f"Error deleting game {game.id}: {str(e)}")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING("Dry run - no changes made")
            ) 