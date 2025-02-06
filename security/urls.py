from django.urls import path
from . import views

app_name = 'security'

urlpatterns = [
    path('dashboard/', views.SecurityViews.security_dashboard, name='dashboard'),
    path('2fa/setup/', views.SecurityViews.setup_2fa, name='setup_2fa'),
    path('api-keys/', views.SecurityViews.manage_api_keys, name='manage_api_keys'),
    path('api-keys/<int:key_id>/revoke/', 
         views.SecurityViews.revoke_api_key, 
         name='revoke_api_key'),
] 