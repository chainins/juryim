from django import forms
from decimal import Decimal
from .models import WithdrawalRequest, PaymentProvider, DepositRequest

class TransferForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=18,
        decimal_places=8,
        min_value=Decimal('0.00000001'),
        widget=forms.NumberInput(attrs={'step': '0.00000001'})
    )
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than 0")
        return amount

class WithdrawalForm(forms.ModelForm):
    confirm_address = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm withdrawal address'
        })
    )
    
    class Meta:
        model = WithdrawalRequest
        fields = ['amount', 'address', 'network']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Enter amount'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter withdrawal address'
            }),
            'network': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        self.provider = kwargs.pop('provider', None)
        super().__init__(*args, **kwargs)
        
        if self.provider:
            self.fields['amount'].widget.attrs.update({
                'min': self.provider.min_amount,
                'max': self.provider.max_amount
            })

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if self.provider:
            if amount < self.provider.min_amount:
                raise forms.ValidationError(
                    f"Minimum withdrawal amount is {self.provider.min_amount}"
                )
            if amount > self.provider.max_amount:
                raise forms.ValidationError(
                    f"Maximum withdrawal amount is {self.provider.max_amount}"
                )
                
        if self.account:
            fee = self.provider.calculate_withdrawal_fee(amount)
            if self.account.balance < (amount + fee):
                raise forms.ValidationError("Insufficient funds")
                
        return amount

    def clean(self):
        cleaned_data = super().clean()
        address = cleaned_data.get('address')
        confirm_address = cleaned_data.get('confirm_address')
        
        if address and confirm_address and address != confirm_address:
            raise forms.ValidationError("Addresses do not match")
            
        amount = cleaned_data.get('amount')
        network = cleaned_data.get('network')
        
        if amount and hasattr(self, 'user'):
            account = self.user.financialaccount
            if amount > account.balance:
                raise forms.ValidationError("Insufficient balance for withdrawal")
            
            # Add network-specific validations
            if network == 'BTC' and amount < Decimal('0.001'):
                raise forms.ValidationError("Minimum BTC withdrawal is 0.001")
            elif network == 'ETH' and amount < Decimal('0.01'):
                raise forms.ValidationError("Minimum ETH withdrawal is 0.01")
            elif network == 'USDT' and amount < Decimal('10'):
                raise forms.ValidationError("Minimum USDT withdrawal is 10")
        
        return cleaned_data

class DepositAddressForm(forms.Form):
    network = forms.ChoiceField(choices=[])
    
    def __init__(self, *args, **kwargs):
        networks = kwargs.pop('networks', [])
        super().__init__(*args, **kwargs)
        self.fields['network'].choices = networks 

class DepositForm(forms.ModelForm):
    class Meta:
        model = DepositRequest
        fields = ['amount']
        
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= Decimal('0'):
            raise forms.ValidationError("Amount must be greater than 0")
        return amount 