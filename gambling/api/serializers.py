from rest_framework import serializers
from django.utils import timezone
from django.db import models
from decimal import Decimal
from ..models import GamblingGame, GamblingBet
from ..utils import validate_bet_data, calculate_win_probability

class GamblingGameSerializer(serializers.ModelSerializer):
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = GamblingGame
        fields = [
            'id', 'title', 'description', 'game_type',
            'minimum_single_bet', 'maximum_single_bet',
            'fee_percentage', 'total_pool', 'status',
            'start_time', 'end_time', 'time_remaining',
            'result'
        ]
    
    def get_time_remaining(self, obj):
        if obj.status == 'active' and obj.end_time > timezone.now():
            return (obj.end_time - timezone.now()).total_seconds()
        return 0

class GamblingBetSerializer(serializers.ModelSerializer):
    game_title = serializers.CharField(source='game.title', read_only=True)
    win_probability = serializers.SerializerMethodField()
    
    class Meta:
        model = GamblingBet
        fields = [
            'id', 'game', 'game_title', 'amount',
            'fee_amount', 'bet_data', 'status',
            'placed_at', 'result_time', 'win_probability'
        ]
    
    def get_win_probability(self, obj):
        return calculate_win_probability(
            obj.game.game_type,
            obj.bet_data
        )

class PlaceBetSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=18,
        decimal_places=8,
        min_value=Decimal('0.00000001')
    )
    bet_data = serializers.JSONField()
    
    def validate(self, data):
        game = self.context.get('game')
        if not game:
            raise serializers.ValidationError("Game context is required")
            
        amount = data['amount']
        if amount < game.minimum_single_bet:
            raise serializers.ValidationError(
                f"Minimum bet is {game.minimum_single_bet}"
            )
        if amount > game.maximum_single_bet:
            raise serializers.ValidationError(
                f"Maximum bet is {game.maximum_single_bet}"
            )
            
        if not validate_bet_data(game.game_type, data['bet_data']):
            raise serializers.ValidationError("Invalid bet data")
            
        return data

class GameStatsSerializer(serializers.ModelSerializer):
    total_bets = serializers.IntegerField(source='gamblingbet_set.count')
    unique_players = serializers.SerializerMethodField()
    average_bet = serializers.SerializerMethodField()
    total_fees = serializers.SerializerMethodField()
    
    class Meta:
        model = GamblingGame
        fields = [
            'id', 'title', 'total_pool', 'total_bets',
            'unique_players', 'average_bet', 'total_fees'
        ]
    
    def get_unique_players(self, obj):
        return obj.gamblingbet_set.values('user').distinct().count()
    
    def get_average_bet(self, obj):
        if obj.total_bets > 0:
            return obj.total_pool / obj.total_bets
        return Decimal('0')
    
    def get_total_fees(self, obj):
        return obj.gamblingbet_set.aggregate(
            total=models.Sum('fee_amount')
        )['total'] or Decimal('0') 