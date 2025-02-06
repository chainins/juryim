from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Notification, NotificationPreference

class NotificationService:
    @staticmethod
    def create_notification(user, notification_type, title, message, priority='medium', link=''):
        """Create a new notification and send if appropriate"""
        # Check user preferences
        prefs, _ = NotificationPreference.objects.get_or_create(user=user)
        priority_levels = {'low': 0, 'medium': 1, 'high': 2, 'urgent': 3}
        
        if priority_levels[priority] >= priority_levels[prefs.minimum_priority]:
            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                link=link
            )
            
            # Send email if enabled
            if prefs.email_notifications:
                NotificationService.send_email_notification(notification)
                
            return notification
        return None

    @staticmethod
    def send_email_notification(notification):
        """Send email for notification"""
        subject = f'{notification.title} - {notification.get_priority_display()} Priority'
        message = f'''
        {notification.message}
        
        Priority: {notification.get_priority_display()}
        Type: {notification.get_notification_type_display()}
        
        View more details at: {settings.SITE_URL}{notification.link}
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [notification.user.email],
            fail_silently=True,
        )

    @staticmethod
    def mark_as_read(notification_id, user):
        """Mark a notification as read"""
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            if not notification.is_read:
                notification.is_read = True
                notification.read_at = timezone.now()
                notification.save()
            return True
        except Notification.DoesNotExist:
            return False

    @staticmethod
    def mark_all_as_read(user):
        """Mark all notifications as read for a user"""
        Notification.objects.filter(
            user=user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )

    @staticmethod
    def get_unread_count(user):
        """Get count of unread notifications"""
        return Notification.objects.filter(
            user=user,
            is_read=False
        ).count() 