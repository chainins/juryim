from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

class User(AbstractUser):
    ROLE_CHOICES = (
        ('visitor', 'Visitor'),
        ('registered', 'Registered User'),
        ('admin', 'Administrator'),
        ('authorized', 'Authorized User'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='visitor')
    credit_score = models.IntegerField(default=100)
    invitation_code = models.CharField(max_length=30, blank=True, null=True)
    used_invitation_code = models.CharField(max_length=30, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Profile fields
    address = models.TextField(blank=True, null=True)
    id_number = models.CharField(max_length=50, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    
    # Verification flags
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    id_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'

class UserIP(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='ip_addresses')
    ip_address = models.GenericIPAddressField()
    last_used = models.DateTimeField(auto_now=True)
    is_first_ip = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-last_used']
        unique_together = ['user', 'ip_address']

class SecurityQuestion(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        null=True,  # Allow null temporarily for migration
        default=1   # Default to user ID 1 (usually admin)
    )
    question = models.CharField(max_length=255, default="What is your mother's maiden name?")
    answer = models.CharField(max_length=255, default="Not set")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s security question"

class UserSecurityQuestion(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='security_questions')
    question = models.ForeignKey(SecurityQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=200)
    custom_question = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'question']

class UserMessage(models.Model):
    MESSAGE_TYPES = (
        ('system', 'System Message'),
        ('task', 'Task Notification'),
        ('security', 'Security Alert'),
        ('group', 'Group Message'),
        ('gambling', 'Gambling Update'),
        ('notification', 'Notification'),
    )

    user = models.ForeignKey('User', on_delete=models.CASCADE)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_messages'

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient}: {self.subject}" 