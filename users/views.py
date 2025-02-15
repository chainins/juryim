from django.contrib.auth import login, logout, authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from .forms import UserRegistrationForm, SecurityQuestionForm, SecurityQuestionVerificationForm, SecurityAnswerForm
from .services import UserAuthService
from .models import User, SecurityQuestion, UserSecurityQuestion, UserIP, UserMessage, Message, EmailVerification, UserIPAddress
from social_django.utils import load_strategy, load_backend
from social_core.actions import do_complete
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import login as do_login
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import uuid

class UserViews:
    @staticmethod
    @require_http_methods(["GET", "POST"])
    def register(request):
        print("Register view called")
        if request.method == 'POST':
            print("POST data:", request.POST)
            form = UserRegistrationForm(request.POST)
            print("Form created with POST data")
            
            if form.is_valid():
                print("Form is valid")
                user = form.save(commit=False)
                print(f"User object created: {user.username}")
                # Hash the password before saving
                user.set_password(form.cleaned_data['password'])
                user.is_active = True
                user.email_verification_token = str(uuid.uuid4())
                
                try:
                    # Save the user
                    user.save()
                    print(f"User saved to database: {user.id}")
                    
                    # Create security question with user's answer
                    security_question = SecurityQuestion.objects.create(
                        user=user,
                        question="What is your favorite color?",
                        answer=form.cleaned_data['security_answer']  # Use the user's answer
                    )
                    print(f"Created security question: {security_question.question}")
                    
                    messages.success(request, 'Registration successful! Please login with your credentials.')
                    return redirect('users:login')
                except Exception as e:
                    print(f"Error during registration: {str(e)}")
                    messages.error(request, 'An error occurred during registration.')
            else:
                print("Form errors:", form.errors)
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = UserRegistrationForm()
            print("GET request - empty form created")
        
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

    @staticmethod
    def verify_email(request, token):
        return render(request, 'users/verify_email.html')

    @staticmethod
    def login(request):
        print("Login view called")
        
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            print(f"Attempting to authenticate user: {username}")
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if not user.is_active:
                    print(f"User {username} is not active")  # Debug print
                    messages.error(request, 'Please verify your email before logging in.')
                    return render(request, 'users/login.html')
                    
                print(f"User authenticated successfully: {user.username}")
                current_ip = request.META.get('REMOTE_ADDR')
                
                try:
                    known_ip = UserIPAddress.objects.filter(user=user, ip_address=current_ip).exists()
                    
                    if known_ip:
                        auth_login(request, user)
                        print("User logged in successfully")
                        messages.success(request, 'Login successful!')
                        return redirect('home')
                    else:
                        request.session['pending_user_id'] = user.id
                        request.session['pending_ip'] = current_ip
                        return redirect('users:verify_ip')
                except Exception as e:
                    print(f"Error during login process: {str(e)}")
                    messages.error(request, 'An error occurred during login.')
            else:
                # Let's check if the user exists but password is wrong
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    user = User.objects.get(username=username)
                    if not user.is_active:
                        messages.error(request, 'Please verify your email before logging in.')
                    else:
                        messages.error(request, 'Invalid password')
                except User.DoesNotExist:
                    messages.error(request, 'Username does not exist')
        
        return render(request, 'users/login.html')

    @staticmethod
    def logout(request):
        from django.contrib.auth import logout as auth_logout
        is_admin = request.user.is_staff  # Store the status before logout
        auth_logout(request)
        messages.success(request, 'You have been logged out successfully')
        if is_admin:
            return redirect('/admin/login/')  # Use absolute URL for admin login
        return redirect('users:login')

    @staticmethod
    def settings(request):
        return render(request, 'users/settings.html')

    @staticmethod
    def password_reset(request):
        return render(request, 'users/password_reset.html')

    @staticmethod
    def verify_ip(request):
        print("Verify IP view called")
        if request.method == 'POST':
            print("POST data:", request.POST)  # Debug print
            form = SecurityAnswerForm(request.POST)
            print("Form bound:", form.is_bound)  # Debug print
            print("Form data:", form.data)  # Debug print
            
            if form.is_valid():
                user_answer = form.cleaned_data['security_answer']
                print(f"Valid form, answer: {user_answer}")  # Debug print
                
                try:
                    security_question = SecurityQuestion.objects.get(user=request.user)
                    print(f"Stored answer: {security_question.answer}")  # Debug print
                    
                    if security_question.answer.lower() == user_answer.lower():
                        UserIPAddress.objects.get_or_create(
                            user=request.user,
                            ip_address=request.META.get('REMOTE_ADDR')
                        )
                        messages.success(request, 'IP verification successful!')
                        return redirect('home')
                    else:
                        messages.error(request, 'Incorrect answer. Please try again.')
                except SecurityQuestion.DoesNotExist:
                    print("Security question not found for user:", request.user)  # Debug print
                    messages.error(request, 'Security question not found.')
            else:
                print("Form errors:", form.errors)  # Debug print
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = SecurityAnswerForm()
            print("New form created")  # Debug print
        
        return render(request, 'users/verify_ip.html', {
            'form': form,
            'debug': True  # Add debug flag for template
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
    questions = SecurityQuestion.objects.filter(user=request.user)
    return render(request, 'users/security_questions.html', {'questions': questions})

@login_required
def messages_view(request):
    user_messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'users/messages.html', {'messages': user_messages})

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

def verify_ip(request):
    print("\n=== Starting verify_ip view ===")
    pending_user_id = request.session.get('pending_user_id')
    pending_ip = request.session.get('pending_ip')
    
    if not pending_user_id or not pending_ip:
        messages.error(request, 'No pending verification found')
        return redirect('users:login')
    
    try:
        user = User.objects.get(id=pending_user_id)
        security_question = SecurityQuestion.objects.filter(user=user).first()
        
        if request.method == 'POST':
            answer = request.POST.get('security_answer')
            print(f"Received answer: {answer}")
            
            if security_question and security_question.verify_answer(answer):
                print("Answer verified successfully")
                UserIPAddress.objects.create(user=user, ip_address=pending_ip)
                auth_login(request, user)
                del request.session['pending_user_id']
                del request.session['pending_ip']
                messages.success(request, 'IP verified successfully')
                return redirect('home')
            else:
                print("Answer verification failed")
                messages.error(request, 'Incorrect answer')
        
        return render(request, 'users/verify_ip.html')
        
    except User.DoesNotExist:
        print(f"User not found with id: {pending_user_id}")
        messages.error(request, 'User not found')
        return redirect('users:login')

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

def send_verification_email(request, user):
    verification = EmailVerification.objects.create(user=user)
    
    verification_url = f"{request.scheme}://{request.get_host()}/users/verify-email/{verification.token}/"
    
    send_mail(
        'Verify your email',
        f'Please click this link to verify your email: {verification_url}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

@login_required
def verify_email(request, token):
    try:
        verification = EmailVerification.objects.get(token=token, verified=False)
        verification.verified = True
        verification.save()
        messages.success(request, 'Email verified successfully!')
    except EmailVerification.DoesNotExist:
        messages.error(request, 'Invalid verification token.')
    
    return redirect('users:profile') 