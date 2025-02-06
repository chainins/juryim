from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Task, ArbitrationTask, ArbitrationVote
from .forms import TaskForm, ArbitrationTaskForm
from .services import TaskService

class TaskViews:
    @staticmethod
    @login_required
    def create_task(request):
        if request.method == 'POST':
            form = TaskForm(request.POST)
            if form.is_valid():
                task = form.save(commit=False)
                task.creator = request.user
                task.status = 'open'
                task.save()
                
                if task.task_type == 'crowdsource':
                    required_notifications = TaskService.calculate_required_notifications(task)
                    # Handle notifications logic
                
                messages.success(request, 'Task created successfully!')
                return redirect('tasks:task_detail', task_id=task.id)
        else:
            form = TaskForm()
        return render(request, 'tasks/create_task.html', {'form': form})

    @staticmethod
    @login_required
    def create_arbitration(request):
        if request.method == 'POST':
            task_form = TaskForm(request.POST)
            arbitration_form = ArbitrationTaskForm(request.POST)
            
            if task_form.is_valid() and arbitration_form.is_valid():
                task = task_form.save(commit=False)
                task.creator = request.user
                task.task_type = 'arbitration'
                task.status = 'open'
                task.save()
                
                arbitration = arbitration_form.save(commit=False)
                arbitration.task = task
                arbitration.save()
                
                arbitrators = TaskService.select_arbitrators(arbitration)
                TaskService.notify_arbitrators(arbitration, arbitrators)
                
                messages.success(request, 'Arbitration task created successfully!')
                return redirect('tasks:arbitration_detail', arbitration_id=arbitration.id)
        else:
            task_form = TaskForm()
            arbitration_form = ArbitrationTaskForm()
            
        return render(request, 'tasks/create_arbitration.html', {
            'task_form': task_form,
            'arbitration_form': arbitration_form
        })

    @staticmethod
    @login_required
    def task_list(request):
        tasks = Task.objects.filter(
            Q(status='open') |
            Q(creator=request.user) |
            Q(assigned_user=request.user)
        ).order_by('-created_at')
        
        return render(request, 'tasks/task_list.html', {'tasks': tasks})

    @staticmethod
    @login_required
    def claim_task(request, task_id):
        task = get_object_or_404(Task, id=task_id)
        
        if task.status != 'open':
            messages.error(request, 'This task is not available for claiming.')
            return redirect('tasks:task_detail', task_id=task.id)
            
        if task.task_type.startswith('single_'):
            task.assigned_user = request.user
            task.status = 'in_progress'
            task.save()
            messages.success(request, 'Task claimed successfully!')
            
        return redirect('tasks:task_detail', task_id=task.id)

    @staticmethod
    @login_required
    def submit_arbitration_vote(request, arbitration_id):
        arbitration = get_object_or_404(ArbitrationTask, id=arbitration_id)
        
        if request.method == 'POST':
            vote_option = request.POST.get('vote_option')
            if vote_option in arbitration.voting_options:
                ArbitrationVote.objects.create(
                    arbitration=arbitration,
                    arbitrator=request.user,
                    vote_option=vote_option,
                    margin_locked=arbitration.margin_requirement
                )
                messages.success(request, 'Vote submitted successfully!')
                
                # Check if voting is complete
                if ArbitrationVote.objects.filter(arbitration=arbitration).count() >= arbitration.required_arbitrators:
                    result = TaskService.calculate_arbitration_result(arbitration)
                    arbitration.result = result
                    arbitration.save()
                    
                    if result != 'uncertain':
                        arbitration.task.status = 'completed'
                        arbitration.task.save()
                
                return redirect('tasks:arbitration_detail', arbitration_id=arbitration.id)
                
        return render(request, 'tasks/submit_vote.html', {'arbitration': arbitration}) 