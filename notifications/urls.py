from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationViews.notification_list, name='list'),
    path('preferences/', views.NotificationViews.preferences, name='preferences'),
    path('mark-read/<int:notification_id>/', 
         views.NotificationViews.mark_as_read, 
         name='mark_as_read'),
    path('mark-all-read/', 
         views.NotificationViews.mark_all_as_read, 
         name='mark_all_as_read'),
    path('unread-count/', 
         views.NotificationViews.get_unread_count, 
         name='unread_count'),
] 