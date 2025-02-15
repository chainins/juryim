from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import UserViews

app_name = 'users'

urlpatterns = [
    # User authentication
    path('register/', views.UserViews.register, name='register'),
    path('verify-email/<str:token>/', views.UserViews.verify_email, name='verify_email'),
    path('login/', views.UserViews.login, name='login'),
    path('logout/', views.UserViews.logout, name='logout'),
    path('profile/', views.UserViews.profile, name='profile'),
    path('settings/', views.UserViews.settings, name='settings'),
    path('password-reset/', views.UserViews.password_reset, name='password_reset'),
    
    # New features
    path('security-questions/', views.security_questions, name='security_questions'),
    path('messages/', views.messages_view, name='messages'),
    
    # Add new URL for email verification
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('verify-ip/', views.UserViews.verify_ip, name='verify_ip'),
] 