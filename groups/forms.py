from django import forms
from .models import Group, GroupVote, GroupFund

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description']

class GroupVoteForm(forms.ModelForm):
    options = forms.CharField(
        widget=forms.Textarea,
        help_text="Enter each option on a new line"
    )

    class Meta:
        model = GroupVote
        fields = ['title', 'description', 'deadline', 'options']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_options(self):
        options = self.cleaned_data['options'].split('\n')
        options = [opt.strip() for opt in options if opt.strip()]
        if len(options) < 2:
            raise forms.ValidationError("At least two options are required")
        return options

class GroupFundForm(forms.ModelForm):
    class Meta:
        model = GroupFund
        fields = ['name', 'description'] 