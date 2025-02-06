from rest_framework.exceptions import APIException
from rest_framework import status

class InsufficientFundsError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Insufficient funds to place bet.'
    default_code = 'insufficient_funds'

class GameNotActiveError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Game is not active.'
    default_code = 'game_not_active'

class InvalidBetError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid bet data.'
    default_code = 'invalid_bet'

class BetLimitError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Bet amount exceeds limits.'
    default_code = 'bet_limit_exceeded'

class GameCompletionError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Error completing game.'
    default_code = 'game_completion_error' 