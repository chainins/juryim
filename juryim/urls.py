from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_required(TemplateView.as_view(template_name='home.html')), name='home'),
    path('users/', include('users.urls', namespace='users')),
    path('financial/', include('financial.urls', namespace='financial')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('notifications/', include('user_notifications.urls', namespace='user_notifications')),
]