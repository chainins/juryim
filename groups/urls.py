from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    path('create/', views.GroupViews.create_group, name='create_group'),
    path('list/', views.GroupViews.group_list, name='group_list'),
    path('<int:group_id>/', views.GroupViews.group_detail, name='group_detail'),
    path('<int:group_id>/vote/create/', views.GroupViews.create_vote, name='create_vote'),
    path('vote/<int:vote_id>/submit/', views.GroupViews.submit_vote, name='submit_vote'),
    path('<int:group_id>/chat/', views.GroupViews.chat_message, name='chat_message'),
] 