from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import Http404
from django.core.exceptions import PermissionDenied
from decimal import Decimal
from ..models import GamblingGame, GamblingBet
from ..permissions import (
    can_create_game,
    can_place_bet,
    can_view_game,
    can_cancel_game,
    user_has_sufficient_balance
)
from ..decorators import (
    game_action_permission,
    bet_action_permission,
    require_active_game
)

User = get_user_model()

class GamblingPermissionsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
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

    def test_can_create_game(self):
        # Regular user can create game
        self.assertTrue(can_create_game(self.user))
        
        # User with negative balance cannot create game
        self.user.balance = Decimal('-1.00000000')
        self.user.save()
        self.assertFalse(can_create_game(self.user))
        
        # Unauthenticated user cannot create game
        self.assertFalse(can_create_game(None))

    def test_can_place_bet(self):
        # Valid bet amount
        self.assertTrue(can_place_bet(
            self.user,
            self.game,
            Decimal('0.00100000')
        ))
        
        # Insufficient balance
        self.assertFalse(can_place_bet(
            self.user,
            self.game,
            Decimal('2.00000000')
        ))
        
        # Game not active
        self.game.status = 'completed'
        self.game.save()
        self.assertFalse(can_place_bet(
            self.user,
            self.game,
            Decimal('0.00100000')
        ))

    def test_can_view_game(self):
        # Any authenticated user can view active game
        self.assertTrue(can_view_game(self.user, self.game))
        
        # Game creator can view completed game
        self.game.status = 'completed'
        self.game.save()
        self.assertTrue(can_view_game(self.user, self.game))
        
        # Other users can view completed game if they placed bets
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        GamblingBet.objects.create(
            user=other_user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )
        self.assertTrue(can_view_game(other_user, self.game))

    def test_can_cancel_game(self):
        # Creator can cancel pending game
        self.game.status = 'pending'
        self.game.save()
        self.assertTrue(can_cancel_game(self.user, self.game))
        
        # Cannot cancel active game
        self.game.status = 'active'
        self.game.save()
        self.assertFalse(can_cancel_game(self.user, self.game))
        
        # Other users cannot cancel game
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.assertFalse(can_cancel_game(other_user, self.game))

    def test_user_has_sufficient_balance(self):
        # Sufficient balance
        self.assertTrue(user_has_sufficient_balance(
            self.user,
            Decimal('0.10000000')
        ))
        
        # Insufficient balance
        self.assertFalse(user_has_sufficient_balance(
            self.user,
            Decimal('2.00000000')
        ))
        
        # Zero balance
        self.user.balance = Decimal('0')
        self.user.save()
        self.assertFalse(user_has_sufficient_balance(
            self.user,
            Decimal('0.00000001')
        ))

    def test_game_action_permission_decorator(self):
        @game_action_permission(can_view_game)
        def view_game(request, game_id):
            return True

        request = self.factory.get('/')
        request.user = self.user
        
        # Valid access
        self.assertTrue(view_game(request, self.game.id))
        
        # Invalid game ID
        with self.assertRaises(Http404):
            view_game(request, 99999)
        
        # Unauthorized access
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        request.user = other_user
        self.game.status = 'completed'
        self.game.save()
        with self.assertRaises(PermissionDenied):
            view_game(request, self.game.id)

    def test_bet_action_permission_decorator(self):
        @bet_action_permission
        def modify_bet(request, bet_id):
            return True

        bet = GamblingBet.objects.create(
            user=self.user,
            game=self.game,
            amount=Decimal('0.00100000'),
            bet_data={'number': 6},
            fee_amount=Decimal('0.00001000')
        )
        
        request = self.factory.get('/')
        request.user = self.user
        
        # Valid access
        self.assertTrue(modify_bet(request, bet.id))
        
        # Invalid bet ID
        with self.assertRaises(Http404):
            modify_bet(request, 99999)
        
        # Unauthorized access
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        request.user = other_user
        with self.assertRaises(PermissionDenied):
            modify_bet(request, bet.id)

    def test_require_active_game_decorator(self):
        @require_active_game
        def place_bet(request, game_id):
            return True

        request = self.factory.get('/')
        request.user = self.user
        
        # Active game
        self.assertTrue(place_bet(request, self.game.id))
        
        # Completed game
        self.game.status = 'completed'
        self.game.save()
        with self.assertRaises(PermissionDenied):
            place_bet(request, self.game.id) 