from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from ..models import GamblingGame, GamblingBet
from ..cache import (
    get_cached_game,
    cache_game,
    get_cached_game_stats,
    cache_game_stats,
    invalidate_game_cache,
    get_user_active_bets_cache_key,
    get_game_cache_key
)

User = get_user_model()

class GamblingCacheTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            balance=Decimal('1.00000000')
        )
        self.game = GamblingGame.objects.create(
            title='Test Game',
            description='Test Description',
            game_type='dice',
            created_by=self.user,
            start_time=timezone.now() + timezone.timedelta(minutes=5),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            minimum_single_bet=Decimal('0.00000100'),
            maximum_single_bet=Decimal('0.10000000'),
            fee_percentage=Decimal('1.0'),
            status='active'
        )
        self.client.login(username='testuser', password='testpass123')
        # Clear cache before each test
        cache.clear()

    def test_game_caching(self):
        """Test game object caching"""
        # Initially not in cache
        cached_game = get_cached_game(self.game.id)
        self.assertIsNone(cached_game)
        
        # Cache the game
        cache_game(self.game)
        
        # Should now be in cache
        cached_game = get_cached_game(self.game.id)
        self.assertIsNotNone(cached_game)
        self.assertEqual(cached_game.id, self.game.id)
        self.assertEqual(cached_game.title, self.game.title)

    def test_game_stats_caching(self):
        """Test game statistics caching"""
        # Create some bets
        GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )
        GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00200000'),
            bet_data={'number': 3},
            fee_amount=Decimal('0.00002000')
        )
        
        # Initially not in cache
        cached_stats = get_cached_game_stats(self.game.id)
        self.assertIsNone(cached_stats)
        
        # Cache the stats
        stats = {
            'total_bets': Decimal('0.00300000'),
            'total_fees': Decimal('0.00003000'),
            'total_players': 1
        }
        cache_game_stats(self.game.id, stats)
        
        # Should now be in cache
        cached_stats = get_cached_game_stats(self.game.id)
        self.assertIsNotNone(cached_stats)
        self.assertEqual(cached_stats['total_bets'], Decimal('0.00300000'))
        self.assertEqual(cached_stats['total_fees'], Decimal('0.00003000'))

    def test_cache_invalidation(self):
        """Test cache invalidation on game updates"""
        # Cache the game
        cache_game(self.game)
        self.assertIsNotNone(get_cached_game(self.game.id))
        
        # Invalidate cache
        invalidate_game_cache(self.game.id)
        
        # Should no longer be in cache
        self.assertIsNone(get_cached_game(self.game.id))
        self.assertIsNone(get_cached_game_stats(self.game.id))

    def test_user_active_bets_caching(self):
        """Test caching of user's active bets"""
        cache_key = get_user_active_bets_cache_key(self.user.id)
        
        # Create active bets
        bet1 = GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )
        bet2 = GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00200000'),
            bet_data={'number': 3},
            fee_amount=Decimal('0.00002000')
        )
        
        # Cache user's active bets
        active_bets = [bet1, bet2]
        cache.set(cache_key, active_bets, timeout=300)
        
        # Verify cache
        cached_bets = cache.get(cache_key)
        self.assertEqual(len(cached_bets), 2)
        self.assertEqual(cached_bets[0].id, bet1.id)
        self.assertEqual(cached_bets[1].id, bet2.id)

    def test_cache_performance(self):
        """Test performance improvement with caching"""
        # Create multiple bets
        for i in range(10):
            GamblingBet.objects.create(
                user=self.user,
                game=self.game,
                amount=Decimal('0.00100000'),
                bet_data={'number': 6},
                fee_amount=Decimal('0.00001000')
            )
        
        # First request - no cache
        start_time = timezone.now()
        response = self.client.get(reverse('gambling:game_detail', args=[self.game.id]))
        uncached_time = timezone.now() - start_time
        
        # Second request - with cache
        start_time = timezone.now()
        response = self.client.get(reverse('gambling:game_detail', args=[self.game.id]))
        cached_time = timezone.now() - start_time
        
        # Cached response should be faster
        self.assertLess(cached_time, uncached_time)

    def test_cache_race_conditions(self):
        """Test handling of potential race conditions in caching"""
        # Simulate concurrent cache updates
        game_key = get_game_cache_key(self.game.id)
        
        # First thread sets cache
        cache.set(game_key, self.game, timeout=300)
        
        # Second thread updates game
        self.game.title = 'Updated Game'
        self.game.save()
        
        # Cache should be invalidated
        cached_game = cache.get(game_key)
        self.assertIsNone(cached_game)

    def tearDown(self):
        # Clear cache after each test
        cache.clear() 