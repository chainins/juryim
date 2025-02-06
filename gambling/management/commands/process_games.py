from django.core.management.base import BaseCommand
from django.utils import timezone
from gambling.models import GamblingGame
from gambling.services import GamblingService

class Command(BaseCommand):
    help = 'Process completed gambling games and distribute winnings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get expired active games
        expired_games = GamblingGame.objects.filter(
            status='active',
            end_time__lte=timezone.now()
        )
        
        self.stdout.write(f'Found {expired_games.count()} games to process')
        
        for game in expired_games:
            try:
                self.stdout.write(f'Processing game {game.id}: {game.title}')
                
                if not dry_run:
                    GamblingService.complete_game(game)
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully completed game {game.id}')
                    )
                else:
                    self.stdout.write(f'Would complete game {game.id} (dry run)')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing game {game.id}: {str(e)}')
                )
                continue 