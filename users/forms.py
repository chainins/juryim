from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, SecurityQuestion, UserSecurityQuestion
from django.contrib.auth.hashers import make_password

class UserRegistrationForm(forms.ModelForm):
    invitation_code = forms.CharField(
        max_length=30, 
        required=True,
        initial='WELCOME2024',  # Default invitation code
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter invitation code'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    security_answer = forms.CharField(
        label="What is your favorite color?",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your favorite color'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password', 'invitation_code', 'security_answer')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username'
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists')
        return email

    def clean_invitation_code(self):
        code = self.cleaned_data.get('invitation_code')
        valid_codes = ['WELCOME2024', 'VIP2024']  # Add more valid codes as needed
        if code not in valid_codes:
            raise forms.ValidationError("Invalid invitation code")
        return code

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

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

class SecurityAnswerForm(forms.Form):
    security_answer = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your answer here'
        })
    )

    def clean_security_answer(self):
        answer = self.cleaned_data.get('security_answer')
        if not answer:
            raise forms.ValidationError("Security answer is required.")
        return answer.strip() 