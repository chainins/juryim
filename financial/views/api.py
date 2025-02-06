from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import WithdrawalRequest
from ..serializers import WithdrawalRequestSerializer

class WithdrawalViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WithdrawalRequestSerializer
    queryset = WithdrawalRequest.objects.all()

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get status updates for multiple withdrawals"""
        withdrawal_ids = request.GET.get('ids', '').split(',')
        withdrawals = WithdrawalRequest.objects.filter(
            id__in=withdrawal_ids
        ).values('id', 'status')
        
        return Response({
            str(w['id']): w['status'] 
            for w in withdrawals
        })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        withdrawal = self.get_object()
        try:
            withdrawal.approve(by_user=request.user)
            return Response({'success': True})
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=400)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        withdrawal = self.get_object()
        reason = request.data.get('reason', '')
        try:
            withdrawal.reject(
                by_user=request.user,
                reason=reason
            )
            return Response({'success': True})
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=400) 