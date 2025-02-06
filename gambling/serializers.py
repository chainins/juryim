from rest_framework import serializers
from django.utils import timezone
from .models import GamblingGame, GamblingBet
from .utils import (
    validate_bet_data,
    calculate_fee_amount,
    validate_game_duration
)

class GamblingGameSerializer(serializers.ModelSerializer):
    total_bets = serializers.IntegerField(read_only=True)
    unique_players = serializers.IntegerField(read_only=True)
    time_remaining = serializers.SerializerMethodField()
    user_bets = serializers.SerializerMethodField()
    
    class Meta:
        model = GamblingGame
        fields = [
            'id', 'title', 'description', 'game_type',
            'status', 'minimum_single_bet', 'maximum_single_bet',
            'fee_percentage', 'total_pool', 'total_bets',
            'unique_players', 'start_time', 'end_time',
            'time_remaining', 'user_bets', 'result',
            'created_at', 'created_by'
        ]
        read_only_fields = [
            'status', 'total_pool', 'total_bets',
            'unique_players', 'result', 'created_at'
        ]
    
    def get_time_remaining(self, obj):
        if obj.status != 'active':
            return None
            
        remaining = obj.end_time - timezone.now()
        if remaining.total_seconds() <= 0:
            return None
            
        return int(remaining.total_seconds())
    
    def get_user_bets(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return None
            
        bets = GamblingBet.objects.filter(
            game=obj,
            user=user
        )
        return GamblingBetSerializer(bets, many=True).data
    
    def validate(self, data):
        if 'start_time' in data and 'end_time' in data:
            if not validate_game_duration(data['start_time'], data['end_time']):
                raise serializers.ValidationError(
                    "Invalid game duration"
                )
        
        if 'minimum_single_bet' in data and 'maximum_single_bet' in data:
            if data['minimum_single_bet'] >= data['maximum_single_bet']:
                raise serializers.ValidationError(
                    "Minimum bet must be less than maximum bet"
                )
        
        return data

class GamblingBetSerializer(serializers.ModelSerializer):
    game_title = serializers.CharField(source='game.title', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = GamblingBet
        fields = [
            'id', 'game', 'game_title', 'user', 'username',
            'amount', 'fee_amount', 'bet_data', 'status',
            'win_amount', 'placed_at', 'result_time'
        ]
        read_only_fields = [
            'fee_amount', 'status', 'win_amount',
            'placed_at', 'result_time'
        ]
    
    def validate(self, data):
        game = data['game']
        amount = data['amount']
        bet_data = data['bet_data']
        
        if game.status != 'active':
            raise serializers.ValidationError(
                "Game is not active"
            )
        
        if amount < game.minimum_single_bet:
            raise serializers.ValidationError(
                f"Minimum bet is {game.minimum_single_bet}"
            )
        
        if amount > game.maximum_single_bet:
            raise serializers.ValidationError(
                f"Maximum bet is {game.maximum_single_bet}"
            )
        
        if not validate_bet_data(game.game_type, bet_data):
            raise serializers.ValidationError(
                "Invalid bet data"
            )
        
        # Calculate and set fee amount
        data['fee_amount'] = calculate_fee_amount(
            amount,
            game.fee_percentage
        )
        
        return data

class GameResultSerializer(serializers.Serializer):
    game_type = serializers.ChoiceField(choices=['dice', 'coin', 'roulette'])
    result = serializers.DictField()
    timestamp = serializers.DateTimeField()
    
    def validate_result(self, value):
        game_type = self.initial_data.get('game_type')
        
        if game_type == 'dice':
            number = value.get('number')
            if not isinstance(number, int) or number < 1 or number > 6:
                raise serializers.ValidationError(
                    "Dice result must be number between 1 and 6"
                )
                
        elif game_type == 'coin':
            side = value.get('side')
            if side not in ['heads', 'tails']:
                raise serializers.ValidationError(
                    "Coin result must be 'heads' or 'tails'"
                )
                
        elif game_type == 'roulette':
            number = value.get('number')
            if not isinstance(number, int) or number < 0 or number > 36:
                raise serializers.ValidationError(
                    "Roulette result must be number between 0 and 36"
                )
        
        return value 