from django.db import models
from django.conf import settings

class NotificationManager(models.Manager):
    def unread(self):
        return self.filter(is_read=False)

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('task_update', 'Task Update'),
        ('group_invite', 'Group Invitation'),
        ('group_update', 'Group Update'),
        ('gambling_result', 'Gambling Result'),
        ('arbitration_request', 'Arbitration Request'),
        ('security_alert', 'Security Alert'),
        ('financial_update', 'Financial Update'),
    )
    
    PRIORITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    link = models.CharField(max_length=200, blank=True)  # URL to relevant page
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    objects = NotificationManager()

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

class NotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email_notifications = models.BooleanField(default=True)
    browser_notifications = models.BooleanField(default=True)
    task_updates = models.BooleanField(default=True)
    group_updates = models.BooleanField(default=True)
    gambling_updates = models.BooleanField(default=True)
    financial_updates = models.BooleanField(default=True)
    minimum_priority = models.CharField(
        max_length=10,
        choices=Notification.PRIORITY_LEVELS,
        default='low'
    )

    class Meta:
        db_table = 'notification_preferences'
