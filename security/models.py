from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class LoginAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'login_attempts'

class SecurityLog(models.Model):
    ACTION_TYPES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('security_settings', 'Security Settings Change'),
        ('email_change', 'Email Change'),
        ('2fa_change', 'Two-Factor Authentication Change'),
        ('api_key', 'API Key Action'),
        ('suspicious_activity', 'Suspicious Activity'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'security_logs'

class SecuritySettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_method = models.CharField(
        max_length=20,
        choices=(
            ('email', 'Email'),
            ('authenticator', 'Authenticator App'),
        ),
        default='email'
    )
    login_notification = models.BooleanField(default=True)
    suspicious_login_notification = models.BooleanField(default=True)
    require_2fa_for_withdrawal = models.BooleanField(default=True)
    last_security_review = models.DateTimeField(auto_now_add=True)
    trusted_devices = models.JSONField(default=list)
    ip_whitelist = models.JSONField(default=list)

    class Meta:
        db_table = 'security_settings'

class APIKey(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True)
    secret = models.CharField(max_length=64)
    permissions = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'api_keys'

class TwoFactorBackupCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=20)
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'two_factor_backup_codes' 