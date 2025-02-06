from django import forms
from .models import NotificationPreference

class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        fields = [
            'email_notifications',
            'browser_notifications',
            'task_updates',
            'group_updates',
            'gambling_updates',
            'financial_updates',
            'minimum_priority'
        ]
        widgets = {
            'minimum_priority': forms.Select(attrs={'class': 'form-select'})
        } 