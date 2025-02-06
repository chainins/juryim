from django.core.cache import cache

def get_cached_game(game_id):
    return cache.get(f'game:{game_id}')

def cache_game(game):
    cache.set(f'game:{game.id}', game, timeout=300)

def get_cached_game_stats(game_id):
    return cache.get(f'game_stats:{game_id}')

def cache_game_stats(game_id, stats):
    cache.set(f'game_stats:{game_id}', stats, timeout=300)

def invalidate_game_cache(game_id):
    cache.delete(f'game:{game_id}')
    cache.delete(f'game_stats:{game_id}')

def get_user_active_bets_cache_key(user_id):
    return f'user_active_bets:{user_id}'

def get_game_cache_key(game_id):
    return f'game:{game_id}' 