from django.utils import timezone
from .models import UserIP

class IPTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Get IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Update or create IP record
            user_ip, created = UserIP.objects.get_or_create(
                user=request.user,
                ip_address=ip,
                defaults={'is_first_ip': not UserIP.objects.filter(user=request.user).exists()}
            )
            
            if not created:
                user_ip.last_used = timezone.now()
                user_ip.save()

        response = self.get_response(request)
        return response 