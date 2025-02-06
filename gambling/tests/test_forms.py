from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from ..forms import CreateGameForm, PlaceBetForm, GameFilterForm
from ..models import GamblingGame

User = get_user_model()

class CreateGameFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.form_data = {
            'title': 'Test Game',
            'description': 'Test Description',
            'game_type': 'dice',
            'minimum_single_bet': Decimal('0.00000100'),
            'maximum_single_bet': Decimal('0.10000000'),
            'fee_percentage': Decimal('1.0'),
            'start_time': (timezone.now() + timezone.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': (timezone.now() + timezone.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        }

    def test_valid_form(self):
        form = CreateGameForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_game_duration(self):
        self.form_data['end_time'] = (
            timezone.now() + timezone.timedelta(minutes=3)
        ).strftime('%Y-%m-%d %H:%M:%S')
        form = CreateGameForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Game duration must be between 5 minutes and 24 hours', str(form.errors))

    def test_invalid_bet_limits(self):
        self.form_data['minimum_single_bet'] = '0.2'
        self.form_data['maximum_single_bet'] = '0.1'
        form = CreateGameForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Minimum bet must be less than maximum bet', str(form.errors))

    def test_past_start_time(self):
        self.form_data['start_time'] = (
            timezone.now() - timezone.timedelta(minutes=5)
        ).strftime('%Y-%m-%d %H:%M:%S')
        form = CreateGameForm(data=self.form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Start time must be in the future', str(form.errors))

class PlaceBetFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
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
        self.form_data = {
            'amount': '0.00100000',
            'number': '6'
        }

    def test_valid_dice_bet(self):
        form = PlaceBetForm(data=self.form_data, game=self.game)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['bet_data'], {'number': 6})

    def test_valid_coin_bet(self):
        self.game.game_type = 'coin'
        self.game.save()
        self.form_data = {
            'amount': '0.00100000',
            'side': 'heads'
        }
        form = PlaceBetForm(data=self.form_data, game=self.game)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['bet_data'], {'side': 'heads'})

    def test_valid_roulette_bet(self):
        self.game.game_type = 'roulette'
        self.game.save()
        self.form_data = {
            'amount': '0.00100000',
            'number': '36'
        }
        form = PlaceBetForm(data=self.form_data, game=self.game)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['bet_data'], {'number': 36})

    def test_invalid_bet_amount(self):
        self.form_data['amount'] = '0.00000001'  # Below minimum
        form = PlaceBetForm(data=self.form_data, game=self.game)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def test_invalid_dice_number(self):
        self.form_data['number'] = '7'  # Invalid dice number
        form = PlaceBetForm(data=self.form_data, game=self.game)
        self.assertFalse(form.is_valid())
        self.assertIn('number', form.errors)

    def test_inactive_game(self):
        self.game.status = 'completed'
        self.game.save()
        form = PlaceBetForm(data=self.form_data, game=self.game)
        self.assertFalse(form.is_valid())
        self.assertIn('Game is not active', str(form.errors))

class GameFilterFormTest(TestCase):
    def test_valid_filter(self):
        form_data = {
            'status': 'active',
            'game_type': 'dice',
            'min_pool': '0.001',
            'max_pool': '1.000'
        }
        form = GameFilterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_pool_range(self):
        form_data = {
            'min_pool': '1.000',
            'max_pool': '0.001'
        }
        form = GameFilterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Minimum pool must be less than maximum pool', str(form.errors))

    def test_empty_filter(self):
        form = GameFilterForm(data={})
        self.assertTrue(form.is_valid()) 