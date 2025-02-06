from django import forms
from .models import SecuritySettings, APIKey

class SecuritySettingsForm(forms.ModelForm):
    class Meta:
        model = SecuritySettings
        fields = [
            'two_factor_enabled',
            'two_factor_method',
            'login_notification',
            'suspicious_login_notification',
            'require_2fa_for_withdrawal'
        ]

class TwoFactorSetupForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit code'
        })
    )

class APIKeyForm(forms.ModelForm):
    permissions = forms.MultipleChoiceField(
        choices=[
            ('read', 'Read Access'),
            ('trade', 'Trading Access'),
            ('withdraw', 'Withdrawal Access')
        ],
        widget=forms.CheckboxSelectMultiple
    )
    
    class Meta:
        model = APIKey
        fields = ['name', 'permissions', 'expires_at']
        widgets = {
            'expires_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}
            )
        }

class WhitelistIPForm(forms.Form):
    ip_address = forms.GenericIPAddressField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter IP address'
        })
    )
    description = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Description (optional)'
        })
    ) 