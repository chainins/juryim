from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, SecurityQuestion, UserSecurityQuestion

class UserRegistrationForm(UserCreationForm):
    invitation_code = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'invitation_code')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists')
        return email

    def clean_invitation_code(self):
        code = self.cleaned_data.get('invitation_code')
        # Add invitation code validation logic here
        return code

class SecurityQuestionForm(forms.ModelForm):
    answer = forms.CharField(widget=forms.PasswordInput)
    custom_question = forms.CharField(required=False)
    
    class Meta:
        model = UserSecurityQuestion
        fields = ['question', 'answer', 'custom_question']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['question'].queryset = SecurityQuestion.objects.filter(is_custom=False)
        self.fields['question'].empty_label = "Select a security question"

class SecurityQuestionVerificationForm(forms.Form):
    answer = forms.CharField(widget=forms.PasswordInput)
    
    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['answer'].label = question 