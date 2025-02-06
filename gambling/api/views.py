from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from ..models import GamblingGame, GamblingBet
from ..services import GamblingService
from .serializers import (
    GamblingGameSerializer, GamblingBetSerializer,
    PlaceBetSerializer, GameStatsSerializer
)

class GamblingGameViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = GamblingGameSerializer
    
    def get_queryset(self):
        queryset = GamblingGame.objects.all()
        status = self.request.query_params.get('status', None)
        game_type = self.request.query_params.get('game_type', None)
        
        if status:
            queryset = queryset.filter(status=status)
        if game_type:
            queryset = queryset.filter(game_type=game_type)
            
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def place_bet(self, request, pk=None):
        game = self.get_object()
        
        if game.status != 'active':
            return Response(
                {'error': 'Game is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = PlaceBetSerializer(data=request.data)
        if serializer.is_valid():
            try:
                bet = GamblingService.place_bet(
                    game=game,
                    user=request.user,
                    amount=serializer.validated_data['amount'],
                    bet_data=serializer.validated_data['bet_data']
                )
                return Response(
                    GamblingBetSerializer(bet).data,
                    status=status.HTTP_201_CREATED
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True)
    def stats(self, request, pk=None):
        game = self.get_object()
        serializer = GameStatsSerializer(game)
        return Response(serializer.data)

class GamblingBetViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = GamblingBetSerializer
    
    def get_queryset(self):
        return GamblingBet.objects.filter(
            user=self.request.user
        ).order_by('-placed_at')
    
    @action(detail=False)
    def active(self, request):
        queryset = self.get_queryset().filter(
            status='placed',
            game__end_time__gt=timezone.now()
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def completed(self, request):
        queryset = self.get_queryset().exclude(status='placed')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data) 