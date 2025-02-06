from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.UserViews.register, name='register'),
    path('profile/', views.UserViews.profile, name='profile'),
    path('security-questions/', views.UserViews.add_security_questions, name='security_questions'),
    path('password-reset/', views.UserViews.password_reset, name='password_reset'),
    path('verify-email/<str:token>/', views.UserViews.verify_email, name='verify_email'),
] 