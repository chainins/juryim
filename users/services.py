import secrets
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import UserSecurityQuestion

class UserAuthService:
    @staticmethod
    def generate_temp_code():
        """Generate a 30-character temporary code for password reset"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(chars) for _ in range(30))

    @staticmethod
    def generate_invitation_code():
        """Generate a 30-character invitation code"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(chars) for _ in range(30))

    @staticmethod
    def send_reset_password_email(user, temp_code):
        """Send password reset email with temporary code"""
        subject = 'Password Reset Request'
        message = f'''
        You have requested to reset your password.
        Your temporary code is: {temp_code}
        This code will expire in 30 minutes.
        '''
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

    @staticmethod
    def verify_security_questions(user, answers):
        """Verify user's security question answers"""
        user_questions = UserSecurityQuestion.objects.filter(user=user)
        for q in user_questions:
            if q.answer != answers.get(str(q.id)):
                return False
        return True 