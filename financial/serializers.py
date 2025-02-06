from rest_framework import serializers
from .models import WithdrawalRequest

class WithdrawalRequestSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source='account.user.username',
        read_only=True
    )
    
    class Meta:
        model = WithdrawalRequest
        fields = [
            'id', 'account', 'username', 'amount',
            'fee', 'network', 'address', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'status', 'created_at', 'updated_at'
        ] 