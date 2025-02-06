from django.test import TestCase
from django.template import Template, Context
from django.utils import timezone
from decimal import Decimal
from ..templatetags.gambling_tags import (
    format_game_type,
    format_game_status,
    format_bet_status,
    format_time_remaining,
    format_bet_data,
    format_game_result
)
from ..models import GamblingGame, GamblingBet

class GamblingTemplateTagsTest(TestCase):
    def setUp(self):
        self.now = timezone.now()

    def test_format_game_type(self):
        # Test direct filter usage
        self.assertEqual(format_game_type('dice'), 'Dice')
        self.assertEqual(format_game_type('coin'), 'Coin Flip')
        self.assertEqual(format_game_type('roulette'), 'Roulette')
        
        # Test template rendering
        template = Template(
            '{% load gambling_tags %}'
            '{{ game_type|format_game_type }}'
        )
        context = Context({'game_type': 'dice'})
        self.assertEqual(template.render(context), 'Dice')

    def test_format_game_status(self):
        # Test direct filter usage
        self.assertEqual(format_game_status('pending'), 'Pending')
        self.assertEqual(format_game_status('active'), 'Active')
        self.assertEqual(format_game_status('completed'), 'Completed')
        self.assertEqual(format_game_status('cancelled'), 'Cancelled')
        
        # Test template rendering
        template = Template(
            '{% load gambling_tags %}'
            '{{ status|format_game_status }}'
        )
        context = Context({'status': 'active'})
        self.assertEqual(template.render(context), 'Active')

    def test_format_bet_status(self):
        # Test direct filter usage
        self.assertEqual(format_bet_status('placed'), 'Placed')
        self.assertEqual(format_bet_status('won'), 'Won')
        self.assertEqual(format_bet_status('lost'), 'Lost')
        
        # Test template rendering
        template = Template(
            '{% load gambling_tags %}'
            '{{ status|format_bet_status }}'
        )
        context = Context({'status': 'won'})
        self.assertEqual(template.render(context), 'Won')

    def test_format_time_remaining(self):
        # Test future time
        future_time = self.now + timezone.timedelta(minutes=30)
        formatted = format_time_remaining(future_time)
        self.assertIn('minutes', formatted.lower())
        
        # Test past time
        past_time = self.now - timezone.timedelta(minutes=30)
        formatted = format_time_remaining(past_time)
        self.assertEqual(formatted, 'Ended')
        
        # Test template rendering
        template = Template(
            '{% load gambling_tags %}'
            '{{ time|format_time_remaining }}'
        )
        context = Context({'time': future_time})
        rendered = template.render(context)
        self.assertIn('minutes', rendered.lower())

    def test_format_bet_data(self):
        # Test dice bet
        bet_data = {'number': 6}
        formatted = format_bet_data('dice', bet_data)
        self.assertEqual(formatted, 'Number: 6')
        
        # Test coin bet
        bet_data = {'side': 'heads'}
        formatted = format_bet_data('coin', bet_data)
        self.assertEqual(formatted, 'Side: Heads')
        
        # Test roulette bet
        bet_data = {'number': 36}
        formatted = format_bet_data('roulette', bet_data)
        self.assertEqual(formatted, 'Number: 36')
        
        # Test template rendering
        template = Template(
            '{% load gambling_tags %}'
            '{% format_bet_data game_type bet_data %}'
        )
        context = Context({
            'game_type': 'dice',
            'bet_data': {'number': 6}
        })
        self.assertEqual(template.render(context), 'Number: 6')

    def test_format_game_result(self):
        # Test dice result
        result = {'number': 6}
        formatted = format_game_result('dice', result)
        self.assertEqual(formatted, 'Rolled: 6')
        
        # Test coin result
        result = {'side': 'heads'}
        formatted = format_game_result('coin', result)
        self.assertEqual(formatted, 'Result: Heads')
        
        # Test roulette result
        result = {'number': 36}
        formatted = format_game_result('roulette', result)
        self.assertEqual(formatted, 'Number: 36')
        
        # Test template rendering
        template = Template(
            '{% load gambling_tags %}'
            '{% format_game_result game_type result %}'
        )
        context = Context({
            'game_type': 'dice',
            'result': {'number': 6}
        })
        self.assertEqual(template.render(context), 'Rolled: 6')

    def test_template_tag_combinations(self):
        # Test multiple tags in one template
        template = Template(
            '{% load gambling_tags %}'
            'Game: {{ game_type|format_game_type }}\n'
            'Status: {{ status|format_game_status }}\n'
            'Time: {{ time|format_time_remaining }}\n'
            '{% format_bet_data game_type bet_data %}'
        )
        
        context = Context({
            'game_type': 'dice',
            'status': 'active',
            'time': self.now + timezone.timedelta(minutes=30),
            'bet_data': {'number': 6}
        })
        
        rendered = template.render(context)
        self.assertIn('Game: Dice', rendered)
        self.assertIn('Status: Active', rendered)
        self.assertIn('minutes', rendered.lower())
        self.assertIn('Number: 6', rendered)

    def test_invalid_inputs(self):
        # Test invalid game type
        self.assertEqual(format_game_type('invalid'), 'Unknown')
        
        # Test invalid game status
        self.assertEqual(format_game_status('invalid'), 'Unknown')
        
        # Test invalid bet status
        self.assertEqual(format_bet_status('invalid'), 'Unknown')
        
        # Test invalid bet data
        with self.assertRaises(ValueError):
            format_bet_data('dice', {'invalid': 'data'})
        
        # Test invalid game result
        with self.assertRaises(ValueError):
            format_game_result('dice', {'invalid': 'data'}) 