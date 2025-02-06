from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import pyotp
from .models import SecuritySettings, SecurityLog, APIKey
from .forms import (
    SecuritySettingsForm, TwoFactorSetupForm,
    APIKeyForm, WhitelistIPForm
)
from .services import SecurityService

class SecurityViews:
    @staticmethod
    @login_required
    def security_dashboard(request):
        settings = SecuritySettings.objects.get_or_create(user=request.user)[0]
        recent_activity = SecurityLog.objects.filter(
            user=request.user
        ).order_by('-timestamp')[:10]
        api_keys = APIKey.objects.filter(user=request.user)
        
        return render(request, 'security/dashboard.html', {
            'settings': settings,
            'recent_activity': recent_activity,
            'api_keys': api_keys
        })

    @staticmethod
    @login_required
    def setup_2fa(request):
        if request.method == 'POST':
            form = TwoFactorSetupForm(request.POST)
            if form.is_valid():
                settings = SecuritySettings.objects.get(user=request.user)
                secret = request.session.get('2fa_setup_secret')
                
                if secret and SecurityService.verify_2fa_code(secret, form.cleaned_data['code']):
                    settings.two_factor_enabled = True
                    settings.two_factor_method = 'authenticator'
                    settings.save()
                    
                    # Generate backup codes
                    backup_codes = SecurityService.generate_backup_codes(request.user)
                    
                    SecurityService.log_security_action(
                        request, request.user, '2fa_change',
                        {'action': 'enabled', 'method': 'authenticator'}
                    )
                    
                    messages.success(request, '2FA has been successfully enabled!')
                    return render(request, 'security/backup_codes.html', {
                        'backup_codes': backup_codes
                    })
                else:
                    messages.error(request, 'Invalid verification code.')
        else:
            form = TwoFactorSetupForm()
            secret = SecurityService.generate_2fa_secret()
            request.session['2fa_setup_secret'] = secret
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                request.user.email,
                issuer_name="YourAppName"
            )
            
        return render(request, 'security/setup_2fa.html', {
            'form': form,
            'secret': secret,
            'qr_uri': provisioning_uri
        })

    @staticmethod
    @login_required
    def manage_api_keys(request):
        if request.method == 'POST':
            form = APIKeyForm(request.POST)
            if form.is_valid():
                api_key = form.save(commit=False)
                api_key.user = request.user
                key, secret = SecurityService.generate_api_key()
                api_key.key = key
                api_key.secret = secret
                api_key.save()
                
                SecurityService.log_security_action(
                    request, request.user, 'api_key',
                    {'action': 'created', 'key_id': api_key.id}
                )
                
                return render(request, 'security/api_key_created.html', {
                    'api_key': api_key,
                    'secret': secret
                })
        else:
            form = APIKeyForm()
            
        api_keys = APIKey.objects.filter(user=request.user)
        return render(request, 'security/api_keys.html', {
            'form': form,
            'api_keys': api_keys
        })

    @staticmethod
    @login_required
    def revoke_api_key(request, key_id):
        api_key = get_object_or_404(APIKey, id=key_id, user=request.user)
        api_key.is_active = False
        api_key.save()
        
        SecurityService.log_security_action(
            request, request.user, 'api_key',
            {'action': 'revoked', 'key_id': api_key.id}
        )
        
        messages.success(request, 'API key has been revoked.')
        return redirect('security:manage_api_keys') 