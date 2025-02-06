from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from .models import GamblingGame
from .utils import validate_bet_data, validate_game_duration
from decimal import Decimal

class CreateGameForm(forms.ModelForm):
    class Meta:
        model = GamblingGame
        fields = [
            'title', 'description', 'game_type',
            'minimum_single_bet', 'maximum_single_bet',
            'fee_percentage', 'start_time', 'end_time'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            ),
            'end_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            )
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            # Validate game duration
            if not validate_game_duration(start_time, end_time):
                raise forms.ValidationError(
                    "Invalid game duration. Must be between 5 minutes and 24 hours."
                )
            
            # Ensure start time is in the future
            if start_time <= timezone.now():
                raise forms.ValidationError(
                    "Start time must be in the future."
                )
        
        min_bet = cleaned_data.get('minimum_single_bet')
        max_bet = cleaned_data.get('maximum_single_bet')
        
        if min_bet and max_bet and min_bet >= max_bet:
            raise forms.ValidationError(
                "Minimum bet must be less than maximum bet."
            )
        
        return cleaned_data

class PlaceBetForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=16,
        decimal_places=8,
        validators=[
            MinValueValidator(Decimal('0.00000001')),
            MaxValueValidator(Decimal('1.00000000'))
        ]
    )
    
    def __init__(self, *args, game=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game
        
        if game:
            self.fields['amount'].validators = [
                MinValueValidator(game.minimum_single_bet),
                MaxValueValidator(game.maximum_single_bet)
            ]
            
            # Add game-specific bet fields
            if game.game_type == 'dice':
                self.fields['number'] = forms.IntegerField(
                    min_value=1,
                    max_value=6
                )
            elif game.game_type == 'coin':
                self.fields['side'] = forms.ChoiceField(
                    choices=[('heads', 'Heads'), ('tails', 'Tails')]
                )
            elif game.game_type == 'roulette':
                self.fields['number'] = forms.IntegerField(
                    min_value=0,
                    max_value=36
                )
    
    def clean(self):
        cleaned_data = super().clean()
        
        if not self.game:
            raise forms.ValidationError("Game not specified.")
        
        if self.game.status != 'active':
            raise forms.ValidationError("Game is not active.")
        
        if self.game.end_time <= timezone.now():
            raise forms.ValidationError("Game has ended.")
        
        # Build bet data based on game type
        bet_data = {}
        if self.game.game_type == 'dice':
            bet_data['number'] = cleaned_data.get('number')
        elif self.game.game_type == 'coin':
            bet_data['side'] = cleaned_data.get('side')
        elif self.game.game_type == 'roulette':
            bet_data['number'] = cleaned_data.get('number')
        
        if not validate_bet_data(self.game.game_type, bet_data):
            raise forms.ValidationError("Invalid bet data.")
        
        cleaned_data['bet_data'] = bet_data
        return cleaned_data

class GameFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[
            ('', 'All'),
            ('active', 'Active'),
            ('completed', 'Completed')
        ],
        required=False
    )
    game_type = forms.ChoiceField(
        choices=[
            ('', 'All'),
            ('dice', 'Dice'),
            ('coin', 'Coin Flip'),
            ('roulette', 'Roulette')
        ],
        required=False
    )
    min_pool = forms.DecimalField(
        required=False,
        min_value=0
    )
    max_pool = forms.DecimalField(
        required=False,
        min_value=0
    )
    
    def clean(self):
        cleaned_data = super().clean()
        min_pool = cleaned_data.get('min_pool')
        max_pool = cleaned_data.get('max_pool')
        
        if min_pool and max_pool and min_pool > max_pool:
            raise forms.ValidationError(
                "Minimum pool must be less than maximum pool."
            )
        
        return cleaned_data 