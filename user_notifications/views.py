from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from .models import Notification

# Create your views here.

@login_required
def notification_list(request):
    """Display all notifications for the user"""
    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'user_notifications/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def mark_as_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

@login_required
def mark_all_as_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    return JsonResponse({'status': 'success'})
