from django.db import models
from django.conf import settings
from django.db.models import Sum, Count
from tasks.models import ArbitrationTask

class GamblingGameQuerySet(models.QuerySet):
    def with_stats(self):
        return self.annotate(
            total_pool=Sum('bets__amount'),
            total_bets=Count('bets'),
            unique_players=Count('bets__user', distinct=True)
        )

class GamblingGame(models.Model):
    GAME_TYPES = (
        ('dice', 'Dice'),
        ('coin', 'Coin Flip'),
        ('lottery', 'Lottery')
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    game_type = models.CharField(max_length=20, choices=GAME_TYPES)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    minimum_single_bet = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1.00
    )
    maximum_single_bet = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1000.00
    )
    fee_percentage = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=2.00
    )
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = GamblingGameQuerySet.as_manager()

    def __str__(self):
        return self.title

class GamblingBet(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('cancelled', 'Cancelled')
    )

    game = models.ForeignKey(
        GamblingGame,
        on_delete=models.CASCADE,
        related_name='bets'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gambling_bets'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bet_data = models.JSONField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    win_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )
    placed_at = models.DateTimeField(auto_now_add=True)
    result_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s bet on {self.game.title}"

class GamblingTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('bet', 'Bet Placed'),
        ('win', 'Win'),
        ('refund', 'Refund')
    )

    bet = models.ForeignKey(
        GamblingBet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.bet}"

class InvitedGambler(models.Model):
    game = models.ForeignKey(GamblingGame, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    invited_at = models.DateTimeField(auto_now_add=True)
    has_participated = models.BooleanField(default=False)

    class Meta:
        db_table = 'invited_gamblers'
        unique_together = ['game', 'user']

class GamblingSetting(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.JSONField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key

    class Meta:
        ordering = ['key']

class Game(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    min_bet = models.DecimalField(max_digits=10, decimal_places=2)
    max_bet = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Bet(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    outcome = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.game.name} - {self.amount}" 