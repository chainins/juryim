from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.UserViews.register, name='register'),
    path('profile/', views.UserViews.profile, name='profile'),
    path('security-questions/', views.UserViews.add_security_questions, name='security_questions'),
    path('password-reset/', views.UserViews.password_reset, name='password_reset'),
    path('verify-email/<str:token>/', views.UserViews.verify_email, name='verify_email'),
    path('security-questions/', views.security_questions, name='security_questions'),
    path('security-questions/delete/<int:question_id>/', 
         views.delete_security_question, name='delete_security_question'),
    path('verify-ip/', views.verify_ip_change, name='verify_ip'),
    path('messages/', views.message_box, name='message_box'),
    path('messages/<int:message_id>/read/', 
         views.mark_message_read, name='mark_message_read'),
    path('messages/delete/<int:message_id>/', 
         views.delete_message, name='delete_message'),
] 