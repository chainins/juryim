from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from tasks.models import ArbitrationTask

class GamblingGame(models.Model):
    GAME_TYPES = (
        ('dice', 'Dice Roll'),
        ('coin', 'Coin Flip'),
        ('roulette', 'Roulette'),
        ('custom', 'Custom Game')
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
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_games'
    )
    total_pool = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0'))
    minimum_single_bet = models.DecimalField(max_digits=18, decimal_places=8)
    maximum_single_bet = models.DecimalField(max_digits=18, decimal_places=8)
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.00'))
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.JSONField(null=True, blank=True)
    options = models.JSONField(default=dict)  # Game-specific options
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    arbitration_task = models.OneToOneField(
        ArbitrationTask,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        db_table = 'gambling_games'
        ordering = ['-created_at']

    def calculate_winner(self):
        """Calculate winner based on game type and result"""
        if not self.result:
            return None
            
        if self.game_type == 'dice':
            winning_number = self.result.get('number')
            return GamblingBet.objects.filter(
                game=self,
                bet_data__number=winning_number
            )
        elif self.game_type == 'coin':
            winning_side = self.result.get('side')
            return GamblingBet.objects.filter(
                game=self,
                bet_data__side=winning_side
            )
        return None

class GamblingBet(models.Model):
    STATUS_CHOICES = (
        ('placed', 'Placed'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('refunded', 'Refunded')
    )

    game = models.ForeignKey(GamblingGame, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    fee_amount = models.DecimalField(max_digits=18, decimal_places=8)
    bet_data = models.JSONField()  # Game-specific bet data
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')
    placed_at = models.DateTimeField(auto_now_add=True)
    result_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'gambling_bets'
        ordering = ['-placed_at']

class GamblingTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('bet_place', 'Bet Placement'),
        ('bet_win', 'Bet Win'),
        ('bet_refund', 'Bet Refund'),
        ('fee', 'Fee')
    )

    bet = models.ForeignKey(GamblingBet, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)

    class Meta:
        db_table = 'gambling_transactions'

class InvitedGambler(models.Model):
    game = models.ForeignKey(GamblingGame, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    invited_at = models.DateTimeField(auto_now_add=True)
    has_participated = models.BooleanField(default=False)

    class Meta:
        db_table = 'invited_gamblers'
        unique_together = ['game', 'user'] 