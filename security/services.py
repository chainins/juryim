from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import pyotp
import secrets
import string
from .models import (
    LoginAttempt, SecurityLog, SecuritySettings,
    APIKey, TwoFactorBackupCode
)

class SecurityService:
    @staticmethod
    def log_login_attempt(request, user=None, success=False, reason=''):
        """Log a login attempt"""
        LoginAttempt.objects.create(
            user=user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=success,
            failure_reason=reason
        )

    @staticmethod
    def log_security_action(request, user, action_type, details=None):
        """Log a security-related action"""
        SecurityLog.objects.create(
            user=user,
            action_type=action_type,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details=details or {}
        )

    @staticmethod
    def generate_2fa_secret():
        """Generate a new TOTP secret"""
        return pyotp.random_base32()

    @staticmethod
    def verify_2fa_code(secret, code):
        """Verify a 2FA code"""
        totp = pyotp.TOTP(secret)
        return totp.verify(code)

    @staticmethod
    def generate_backup_codes(user, count=8):
        """Generate new backup codes for 2FA"""
        chars = string.ascii_uppercase + string.digits
        codes = []
        for _ in range(count):
            code = ''.join(secrets.choice(chars) for _ in range(10))
            TwoFactorBackupCode.objects.create(
                user=user,
                code=code
            )
            codes.append(code)
        return codes

    @staticmethod
    def verify_backup_code(user, code):
        """Verify and consume a backup code"""
        try:
            backup_code = TwoFactorBackupCode.objects.get(
                user=user,
                code=code,
                used=False
            )
            backup_code.used = True
            backup_code.used_at = timezone.now()
            backup_code.save()
            return True
        except TwoFactorBackupCode.DoesNotExist:
            return False

    @staticmethod
    def generate_api_key():
        """Generate a new API key pair"""
        key = secrets.token_hex(32)
        secret = secrets.token_hex(32)
        return key, secret

    @staticmethod
    def is_suspicious_login(request, user):
        """Check if login attempt is suspicious"""
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        settings = SecuritySettings.objects.get(user=user)
        
        # Check if IP is whitelisted
        if ip_address in settings.ip_whitelist:
            return False
            
        # Check if device is trusted
        for device in settings.trusted_devices:
            if device.get('user_agent') == user_agent:
                return False
                
        # Check for login attempts from different locations
        recent_attempts = LoginAttempt.objects.filter(
            user=user,
            timestamp__gte=timezone.now() - timedelta(hours=24)
        )
        
        if recent_attempts.exclude(ip_address=ip_address).exists():
            return True
            
        return False

    @staticmethod
    def notify_suspicious_login(user, request):
        """Send notification about suspicious login"""
        subject = 'Suspicious Login Attempt Detected'
        message = f'''
        A suspicious login attempt was detected for your account.
        
        Time: {timezone.now()}
        IP Address: {request.META.get('REMOTE_ADDR')}
        Device: {request.META.get('HTTP_USER_AGENT', '')}
        
        If this wasn't you, please secure your account immediately.
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        ) 