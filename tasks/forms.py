from django import forms
from .models import Task, ArbitrationTask

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'task_type', 'reward', 'expiration_time']
        widgets = {
            'expiration_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ArbitrationTaskForm(forms.ModelForm):
    voting_options = forms.CharField(
        widget=forms.Textarea,
        help_text="Enter each option on a new line"
    )

    class Meta:
        model = ArbitrationTask
        fields = ['voting_options', 'required_arbitrators', 'margin_requirement', 'voting_deadline']
        widgets = {
            'voting_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_voting_options(self):
        options = self.cleaned_data['voting_options'].split('\n')
        options = [opt.strip() for opt in options if opt.strip()]
        options.append('uncertain')  # Add mandatory uncertain option
        return options 