from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse

class NotificationService:
    @staticmethod
    def send_withdrawal_request_email(withdrawal):
        """Send withdrawal request notification to user"""
        if not settings.WITHDRAWAL_NOTIFICATIONS:
            return

        context = {
            'withdrawal': withdrawal,
            'user': withdrawal.account.user,
            'status_url': reverse('financial:withdrawal_status', 
                                args=[withdrawal.id])
        }

        # Send to user
        send_mail(
            subject=f'Withdrawal Request {withdrawal.id} Received',
            message=render_to_string(
                'financial/email/withdrawal_request.txt', 
                context
            ),
            html_message=render_to_string(
                'financial/email/withdrawal_request.html', 
                context
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[withdrawal.account.user.email],
            fail_silently=True
        )

        # Send to admin
        send_mail(
            subject=f'New Withdrawal Request {withdrawal.id}',
            message=render_to_string(
                'financial/email/withdrawal_request_admin.txt', 
                context
            ),
            html_message=render_to_string(
                'financial/email/withdrawal_request_admin.html', 
                context
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True
        )

    @staticmethod
    def send_withdrawal_status_email(withdrawal):
        """Send withdrawal status update notification"""
        if not settings.WITHDRAWAL_NOTIFICATIONS:
            return

        context = {
            'withdrawal': withdrawal,
            'user': withdrawal.account.user,
            'status_url': reverse('financial:withdrawal_status', 
                                args=[withdrawal.id])
        }

        send_mail(
            subject=f'Withdrawal {withdrawal.id} Status: {withdrawal.status}',
            message=render_to_string(
                'financial/email/withdrawal_status.txt', 
                context
            ),
            html_message=render_to_string(
                'financial/email/withdrawal_status.html', 
                context
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[withdrawal.account.user.email],
            fail_silently=True
        ) 