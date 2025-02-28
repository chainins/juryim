from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

def send_notification(user, notification):
    """
    Send notification through WebSocket
    notification: Notification model instance
    """
    channel_layer = get_channel_layer()
    notification_data = {
        'id': notification.id,
        'title': notification.title,
        'message': notification.message,
        'link': notification.link,
        'created_at': notification.created_at.isoformat(),
        'type': notification.notification_type,
        'priority': notification.priority
    }
    
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "notification_message",
            "notification": notification_data
        }
    ) 