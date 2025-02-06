from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from .models import Notification, NotificationPreference
from .forms import NotificationPreferenceForm
from .services import NotificationService

class NotificationViews:
    @staticmethod
    @login_required
    def notification_list(request):
        notifications = Notification.objects.filter(user=request.user)
        unread_count = NotificationService.get_unread_count(request.user)
        
        return render(request, 'notifications/notification_list.html', {
            'notifications': notifications,
            'unread_count': unread_count
        })

    @staticmethod
    @login_required
    def preferences(request):
        prefs, created = NotificationPreference.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            form = NotificationPreferenceForm(request.POST, instance=prefs)
            if form.is_valid():
                form.save()
                messages.success(request, 'Notification preferences updated successfully!')
                return redirect('notifications:preferences')
        else:
            form = NotificationPreferenceForm(instance=prefs)
            
        return render(request, 'notifications/preferences.html', {'form': form})

    @staticmethod
    @login_required
    def mark_as_read(request, notification_id):
        if NotificationService.mark_as_read(notification_id, request.user):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            messages.success(request, 'Notification marked as read.')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error'}, status=404)
            messages.error(request, 'Notification not found.')
            
        return redirect('notifications:list')

    @staticmethod
    @login_required
    def mark_all_as_read(request):
        NotificationService.mark_all_as_read(request.user)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
            
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications:list')

    @staticmethod
    @login_required
    def get_unread_count(request):
        """AJAX endpoint for getting unread notification count"""
        count = NotificationService.get_unread_count(request.user)
        return JsonResponse({'count': count}) 