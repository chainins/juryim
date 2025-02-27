from django.utils import timezone
from .models import UserIPAddress
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve

class IPTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Skip verification for these paths
            if any([
                request.path.startswith('/static/'),
                request.path.startswith('/admin/'),
                request.path.startswith('/users/logout/'),
                request.path == '/users/verify-ip/',
                'login' in request.path,
            ]):
                return self.get_response(request)

            try:
                # Check if this IP is verified
                current_ip = request.META.get('REMOTE_ADDR')
                UserIPAddress.objects.get(user=request.user, ip_address=current_ip)
                return self.get_response(request)
            except UserIPAddress.DoesNotExist:
                # Only redirect if not already on verify-ip page
                if not request.path.endswith('/verify-ip/'):
                    return redirect('users:verify_ip')

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 