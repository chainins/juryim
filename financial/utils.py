import qrcode
import base64
from io import BytesIO
from user_notifications.models import Notification

def generate_qr_code(data):
    """Generate QR code and return as base64 string"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert image to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()

def create_financial_notification(user, title, message, priority='medium', link=None):
    """Create a financial notification for the user"""
    return Notification.objects.create(
        user=user,
        notification_type='financial_update',
        title=title,
        message=message,
        priority=priority,
        link=link
    ) 