from celery import Celery
from celery.schedules import crontab
from django.conf import settings
import os

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('gambling')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'process-completed-games': {
        'task': 'gambling.tasks.process_completed_games',
        'schedule': crontab(minute='*/1'),  # Every minute
    },
    'cleanup-expired-games': {
        'task': 'gambling.tasks.cleanup_expired_games',
        'schedule': crontab(hour='3', minute='0'),  # Daily at 3 AM
    },
    'update-game-statistics': {
        'task': 'gambling.tasks.update_game_statistics',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'send-game-notifications': {
        'task': 'gambling.tasks.send_game_notifications',
        'schedule': crontab(minute='*/1'),  # Every minute
    },
}

# Configure task routing
app.conf.task_routes = {
    'gambling.tasks.*': {'queue': 'gambling'},
}

# Configure task settings
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.result_expires = 3600  # Results expire after 1 hour
app.conf.worker_prefetch_multiplier = 1  # Disable prefetching
app.conf.task_acks_late = True  # Enable late acknowledgment 