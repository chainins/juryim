from django.apps import AppConfig
from django.db.models.signals import post_migrate

class GamblingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gambling'
    verbose_name = 'Gambling System'

    def ready(self):
        """Initialize app and register signals"""
        from . import signals
        
        # Register post-migrate handler
        post_migrate.connect(self.create_default_settings, sender=self)
    
    def create_default_settings(self, **kwargs):
        """Create default gambling settings after migration"""
        from django.conf import settings
        from .models import GamblingSetting
        
        defaults = {
            'MIN_BET_AMOUNT': '0.00000001',
            'MAX_BET_AMOUNT': '1.00000000',
            'MIN_GAME_DURATION': '5',  # minutes
            'MAX_GAME_DURATION': '1440',  # minutes (24 hours)
            'DEFAULT_FEE_PERCENTAGE': '2.0',
            'MIN_FEE_AMOUNT': '0.00000100',
            'MAX_DAILY_BETS': '100',
            'MAX_BETS_PER_MINUTE': '5',
        }
        
        for key, value in defaults.items():
            GamblingSetting.objects.get_or_create(
                key=key,
                defaults={'value': value}
            ) 