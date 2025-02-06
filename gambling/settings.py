from django.conf import settings
from decimal import Decimal

# Game Types
GAMBLING_GAME_TYPES = getattr(settings, 'GAMBLING_GAME_TYPES', [
    ('dice', 'Dice'),
    ('coin', 'Coin Flip'),
    ('roulette', 'Roulette')
])

# Bet Limits
GAMBLING_MIN_BET = getattr(
    settings,
    'GAMBLING_MIN_BET',
    Decimal('0.00000001')
)

GAMBLING_MAX_BET = getattr(
    settings,
    'GAMBLING_MAX_BET',
    Decimal('1.00000000')
)

# Game Duration Limits
GAMBLING_MIN_GAME_DURATION = getattr(
    settings,
    'GAMBLING_MIN_GAME_DURATION',
    5  # minutes
)

GAMBLING_MAX_GAME_DURATION = getattr(
    settings,
    'GAMBLING_MAX_GAME_DURATION',
    1440  # minutes (24 hours)
)

# Fee Settings
GAMBLING_DEFAULT_FEE_PERCENTAGE = getattr(
    settings,
    'GAMBLING_DEFAULT_FEE_PERCENTAGE',
    Decimal('2.0')
)

GAMBLING_MIN_FEE = getattr(
    settings,
    'GAMBLING_MIN_FEE',
    Decimal('0.00000100')
)

# Rate Limiting
GAMBLING_MAX_DAILY_BETS = getattr(
    settings,
    'GAMBLING_MAX_DAILY_BETS',
    100
)

GAMBLING_MAX_BETS_PER_MINUTE = getattr(
    settings,
    'GAMBLING_MAX_BETS_PER_MINUTE',
    5
)

# WebSocket Settings
GAMBLING_WS_GROUP_PREFIX = getattr(
    settings,
    'GAMBLING_WS_GROUP_PREFIX',
    'gambling'
)

# Notification Settings
GAMBLING_EMAIL_NOTIFICATIONS = getattr(
    settings,
    'GAMBLING_EMAIL_NOTIFICATIONS',
    True
)

GAMBLING_NOTIFICATION_TYPES = getattr(
    settings,
    'GAMBLING_NOTIFICATION_TYPES',
    [
        'game_created',
        'game_started',
        'game_ending_soon',
        'game_completed',
        'bet_placed',
        'bet_result'
    ]
)

# Game Result Settings
GAMBLING_RESULT_SEED_PREFIX = getattr(
    settings,
    'GAMBLING_RESULT_SEED_PREFIX',
    'gambling_result'
)

# Cache Settings
GAMBLING_CACHE_PREFIX = getattr(
    settings,
    'GAMBLING_CACHE_PREFIX',
    'gambling'
)

GAMBLING_CACHE_TIMEOUT = getattr(
    settings,
    'GAMBLING_CACHE_TIMEOUT',
    300  # 5 minutes
)

# Cleanup Settings
GAMBLING_CLEANUP_DAYS = getattr(
    settings,
    'GAMBLING_CLEANUP_DAYS',
    30
)

# API Settings
GAMBLING_API_PAGE_SIZE = getattr(
    settings,
    'GAMBLING_API_PAGE_SIZE',
    20
)

GAMBLING_API_MAX_PAGE_SIZE = getattr(
    settings,
    'GAMBLING_API_MAX_PAGE_SIZE',
    100
)

# Game Type Specific Settings
GAMBLING_DICE_NUMBERS = getattr(
    settings,
    'GAMBLING_DICE_NUMBERS',
    list(range(1, 7))
)

GAMBLING_COIN_SIDES = getattr(
    settings,
    'GAMBLING_COIN_SIDES',
    ['heads', 'tails']
)

GAMBLING_ROULETTE_NUMBERS = getattr(
    settings,
    'GAMBLING_ROULETTE_NUMBERS',
    list(range(0, 37))
)

# Win Multipliers
GAMBLING_WIN_MULTIPLIERS = getattr(
    settings,
    'GAMBLING_WIN_MULTIPLIERS',
    {
        'dice': Decimal('5.5'),  # 6x - house edge
        'coin': Decimal('1.9'),  # 2x - house edge
        'roulette': Decimal('35')  # 36x - house edge
    }
) 