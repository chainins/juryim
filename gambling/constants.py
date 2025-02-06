from decimal import Decimal

# Game Status
STATUS_PENDING = 'pending'
STATUS_ACTIVE = 'active'
STATUS_COMPLETED = 'completed'
STATUS_CANCELLED = 'cancelled'

GAME_STATUS_CHOICES = [
    (STATUS_PENDING, 'Pending'),
    (STATUS_ACTIVE, 'Active'),
    (STATUS_COMPLETED, 'Completed'),
    (STATUS_CANCELLED, 'Cancelled'),
]

# Game Types
TYPE_DICE = 'dice'
TYPE_COIN = 'coin'
TYPE_ROULETTE = 'roulette'

GAME_TYPE_CHOICES = [
    (TYPE_DICE, 'Dice'),
    (TYPE_COIN, 'Coin Flip'),
    (TYPE_ROULETTE, 'Roulette'),
]

# Bet Status
BET_STATUS_PLACED = 'placed'
BET_STATUS_WON = 'won'
BET_STATUS_LOST = 'lost'
BET_STATUS_CANCELLED = 'cancelled'
BET_STATUS_REFUNDED = 'refunded'

BET_STATUS_CHOICES = [
    (BET_STATUS_PLACED, 'Placed'),
    (BET_STATUS_WON, 'Won'),
    (BET_STATUS_LOST, 'Lost'),
    (BET_STATUS_CANCELLED, 'Cancelled'),
    (BET_STATUS_REFUNDED, 'Refunded'),
]

# Game Specific Constants
DICE_MIN_NUMBER = 1
DICE_MAX_NUMBER = 6
DICE_NUMBERS = list(range(DICE_MIN_NUMBER, DICE_MAX_NUMBER + 1))

COIN_SIDES = ['heads', 'tails']

ROULETTE_MIN_NUMBER = 0
ROULETTE_MAX_NUMBER = 36
ROULETTE_NUMBERS = list(range(ROULETTE_MIN_NUMBER, ROULETTE_MAX_NUMBER + 1))

# Win Multipliers
WIN_MULTIPLIERS = {
    TYPE_DICE: Decimal('5.5'),     # 6x - house edge
    TYPE_COIN: Decimal('1.9'),     # 2x - house edge
    TYPE_ROULETTE: Decimal('35'),  # 36x - house edge
}

# Time Constants
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 24
MINUTES_PER_DAY = MINUTES_PER_HOUR * HOURS_PER_DAY

MIN_GAME_DURATION_MINUTES = 5
MAX_GAME_DURATION_MINUTES = MINUTES_PER_DAY  # 24 hours

# Fee Constants
MIN_FEE_PERCENTAGE = Decimal('0.1')
MAX_FEE_PERCENTAGE = Decimal('10.0')
DEFAULT_FEE_PERCENTAGE = Decimal('2.0')

# Bet Amount Constants
MIN_BET_AMOUNT = Decimal('0.00000001')  # 1 satoshi
MAX_BET_AMOUNT = Decimal('1.00000000')  # 1 coin

# Rate Limiting Constants
MAX_BETS_PER_MINUTE = 5
MAX_DAILY_BETS = 100

# Cache Keys
CACHE_KEY_GAME_STATS = 'game_stats_{game_id}'
CACHE_KEY_USER_BETS = 'user_bets_{user_id}'
CACHE_KEY_ACTIVE_GAMES = 'active_games'

# WebSocket Groups
WS_GROUP_GAME = 'game_{game_id}'
WS_GROUP_USER = 'user_{user_id}'

# Notification Types
NOTIFICATION_GAME_CREATED = 'game_created'
NOTIFICATION_GAME_STARTED = 'game_started'
NOTIFICATION_GAME_ENDING = 'game_ending_soon'
NOTIFICATION_GAME_COMPLETED = 'game_completed'
NOTIFICATION_BET_PLACED = 'bet_placed'
NOTIFICATION_BET_RESULT = 'bet_result'

# API Constants
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Database Constants
MAX_TITLE_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500 