from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('create/', views.TaskViews.create_task, name='create_task'),
    path('create/arbitration/', views.TaskViews.create_arbitration, name='create_arbitration'),
    path('list/', views.TaskViews.task_list, name='task_list'),
    path('claim/<int:task_id>/', views.TaskViews.claim_task, name='claim_task'),
    path('arbitration/<int:arbitration_id>/vote/', 
         views.TaskViews.submit_arbitration_vote, 
         name='submit_arbitration_vote'),
] 