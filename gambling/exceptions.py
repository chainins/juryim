class GamblingError(Exception):
    """Base exception for gambling app"""
    pass

class InvalidBetError(GamblingError):
    """Raised when bet is invalid"""
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class InsufficientFundsError(GamblingError):
    """Raised when user has insufficient funds"""
    pass

class GameClosedError(GamblingError):
    """Raised when trying to bet on closed game"""
    pass

class BetLimitExceededError(GamblingError):
    """Raised when bet exceeds limits"""
    pass

class RateLimitExceededError(GamblingError):
    """Raised when rate limit is exceeded"""
    pass

class InvalidGameStateError(GamblingError):
    """Raised when game state is invalid for operation"""
    def __init__(self, from_status, to_status, game_id, message=None):
        self.from_status = from_status
        self.to_status = to_status
        self.game_id = game_id
        self.message = message or f'Invalid game state transition from {from_status} to {to_status} (Game ID: {game_id})'
        super().__init__(self.message)

class GameValidationError(GamblingError):
    """Raised when game validation fails"""
    pass

class TransactionError(GamblingError):
    """Raised when financial transaction fails"""
    pass

class NotificationError(GamblingError):
    """Raised when notification fails"""
    pass

class InvalidGameTypeError(GamblingError):
    """Raised when game type is invalid"""
    pass

class InvalidBetDataError(GamblingError):
    """Raised when bet data is invalid"""
    pass

class GameDurationError(GamblingError):
    """Raised when game duration is invalid"""
    pass

class FeeLimitError(GamblingError):
    """Raised when fee is outside allowed limits"""
    pass

class InsufficientBalanceError(Exception):
    def __init__(self, required, available, message=None):
        self.required = required
        self.available = available
        self.message = message or f'Insufficient balance: required {required}, available {available}'
        super().__init__(self.message)

class GameNotActiveError(Exception):
    def __init__(self, game_id, current_status, message=None):
        self.game_id = game_id
        self.current_status = current_status
        self.message = message or f'Game is not active: {current_status} (Game ID: {game_id})'
        super().__init__(self.message)

class BetNotAllowedError(Exception):
    def __init__(self, message, game_id):
        self.game_id = game_id
        self.message = message
        super().__init__(message) 