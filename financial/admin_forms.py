from django import forms
from .models import WithdrawalRequest, Transaction

class WithdrawalApprovalForm(forms.ModelForm):
    admin_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False
    )
    
    class Meta:
        model = WithdrawalRequest
        fields = ['status', 'transaction_hash', 'admin_notes']
        
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        transaction_hash = cleaned_data.get('transaction_hash')
        
        if status == 'completed' and not transaction_hash:
            raise forms.ValidationError(
                "Transaction hash is required for completed withdrawals"
            )
            
        return cleaned_data

class ManualTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'account', 'transaction_type', 'amount',
            'fee', 'reference_id', 'description'
        ]
        
    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        amount = cleaned_data.get('amount')
        
        if transaction_type in ['withdrawal', 'bet_loss'] and amount < 0:
            raise forms.ValidationError(
                "Amount should be positive for debit transactions"
            )
            
        return cleaned_data 