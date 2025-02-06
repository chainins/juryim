from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from .forms import UserRegistrationForm
from .services import UserAuthService
from .models import User, SecurityQuestion, UserSecurityQuestion

class UserViews:
    @staticmethod
    @require_http_methods(["GET", "POST"])
    def register(request):
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.ip_address = request.META.get('REMOTE_ADDR')
                user.role = 'registered'
                user.save()
                
                # Generate new invitation code for the user
                user.invitation_code = UserAuthService.generate_invitation_code()
                user.save()
                
                login(request, user)
                return redirect('profile')
        else:
            form = UserRegistrationForm()
        return render(request, 'users/register.html', {'form': form})

    @staticmethod
    @login_required
    def profile(request):
        user = request.user
        security_questions = SecurityQuestion.objects.filter(
            usersecurityquestion__user=user
        )
        return render(request, 'users/profile.html', {
            'user': user,
            'security_questions': security_questions
        })

    @staticmethod
    @login_required
    def add_security_questions(request):
        if request.method == 'POST':
            questions = request.POST.getlist('questions[]')
            answers = request.POST.getlist('answers[]')
            
            # Limit to 5 questions
            for q, a in zip(questions[:5], answers[:5]):
                UserSecurityQuestion.objects.create(
                    user=request.user,
                    question_id=q,
                    answer=a
                )
            return redirect('profile')
            
        questions = SecurityQuestion.objects.filter(is_custom=False)
        return render(request, 'users/security_questions.html', {
            'questions': questions
        }) 