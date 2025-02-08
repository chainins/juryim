from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from .forms import UserRegistrationForm, SecurityQuestionForm, SecurityQuestionVerificationForm
from .services import UserAuthService
from .models import User, SecurityQuestion, UserSecurityQuestion, UserIP, UserMessage
from social_django.utils import load_strategy, load_backend
from social_core.actions import do_complete
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import login as do_login

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

def require_email(request):
    """Handle email collection for social auth"""
    strategy = load_strategy()
    partial_token = request.GET.get('partial_token')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            partial = strategy.partial_load(partial_token)
            partial.data['email'] = email
            strategy.partial_store(partial)
            
            backend_name = partial.data['backend']
            backend = load_backend(strategy, backend_name, None)
            
            return do_complete(backend, do_login)
    
    return render(request, 'users/require_email.html')

@login_required
def security_questions(request):
    """Manage security questions"""
    user_questions = UserSecurityQuestion.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = SecurityQuestionForm(request.POST)
        if form.is_valid():
            if user_questions.count() >= 5:
                messages.error(request, 'You can only have up to 5 security questions.')
                return redirect('security_questions')
                
            question = form.save(commit=False)
            question.user = request.user
            question.save()
            messages.success(request, 'Security question added successfully.')
            return redirect('security_questions')
    else:
        form = SecurityQuestionForm()
    
    return render(request, 'users/security_questions.html', {
        'form': form,
        'user_questions': user_questions
    })

@login_required
def delete_security_question(request, question_id):
    """Delete a security question"""
    try:
        question = UserSecurityQuestion.objects.get(id=question_id, user=request.user)
        question.delete()
        messages.success(request, 'Security question deleted successfully.')
    except UserSecurityQuestion.DoesNotExist:
        messages.error(request, 'Security question not found.')
    
    return redirect('security_questions')

def verify_ip_change(request):
    """Verify user when IP changes"""
    if not request.session.get('needs_verification'):
        return redirect('home')
        
    user = request.user
    question = UserSecurityQuestion.objects.filter(user=user).first()
    
    if not question:
        # If no security questions, just verify and continue
        del request.session['needs_verification']
        return redirect('home')
    
    if request.method == 'POST':
        form = SecurityQuestionVerificationForm(question.question_text, request.POST)
        if form.is_valid():
            if form.cleaned_data['answer'] == question.answer:
                # Update IP record
                UserIP.objects.create(
                    user=user,
                    ip_address=request.META.get('REMOTE_ADDR'),
                )
                del request.session['needs_verification']
                messages.success(request, 'Identity verified successfully.')
                return redirect('home')
            else:
                messages.error(request, 'Incorrect answer.')
    else:
        form = SecurityQuestionVerificationForm(question.question_text)
    
    return render(request, 'users/verify_ip.html', {'form': form})

@login_required
def message_box(request):
    """User message box view"""
    messages_list = UserMessage.objects.filter(user=request.user)
    
    # Filter by type if specified
    message_type = request.GET.get('type')
    if message_type:
        messages_list = messages_list.filter(message_type=message_type)
    
    # Pagination
    paginator = Paginator(messages_list, 20)  # 20 messages per page
    page = request.GET.get('page')
    messages = paginator.get_page(page)
    
    # Count unread messages
    unread_count = messages_list.filter(is_read=False).count()
    
    return render(request, 'users/message_box.html', {
        'messages': messages,
        'unread_count': unread_count,
        'current_type': message_type
    })

@login_required
def mark_message_read(request, message_id):
    """Mark message as read"""
    try:
        message = UserMessage.objects.get(id=message_id, user=request.user)
        message.is_read = True
        message.save()
        messages.success(request, 'Message marked as read.')
    except UserMessage.DoesNotExist:
        messages.error(request, 'Message not found.')
    
    return redirect('message_box')

@login_required
def delete_message(request, message_id):
    """Delete a message"""
    try:
        message = UserMessage.objects.get(id=message_id, user=request.user)
        message.delete()
        messages.success(request, 'Message deleted successfully.')
    except UserMessage.DoesNotExist:
        messages.error(request, 'Message not found.')
    
    return redirect('message_box') 