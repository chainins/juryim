import logging

logger = logging.getLogger('gambling')

def log_game_creation(game, user):
    logger.info(f'Game created: {game.id} by user {user.username}')

def log_bet_placement(bet):
    logger.info(f'Bet placed: {bet.id} on game {bet.game.id} by user {bet.user.username}')

def log_game_status_change(game):
    logger.info(f'Game {game.id} status changed to {game.status}')

def log_error(error_message):
    logger.error(f'Error occurred: {error_message}')

def log_warning(warning_message):
    logger.warning(warning_message)

def log_critical(critical_message):
    logger.critical(f'Critical error: {critical_message}') 