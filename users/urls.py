from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import UserViews

app_name = 'users'

urlpatterns = [
    # User authentication
    path('register/', UserViews.register, name='register'),
    path('verify-email/<str:token>/', UserViews.verify_email, name='verify_email'),
    path('login/', UserViews.login, name='login'),
    path('logout/', UserViews.logout, name='logout'),
    path('profile/', UserViews.profile, name='profile'),
    path('settings/', UserViews.settings, name='settings'),
    path('password-reset/', UserViews.password_reset, name='password_reset'),
    
    # New features
    path('security-questions/', views.security_questions, name='security_questions'),
    path('messages/', views.messages_view, name='messages'),
] 