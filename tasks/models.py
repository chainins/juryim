from django.db import models
from django.conf import settings
from decimal import Decimal

class Task(models.Model):
    TASK_TYPES = (
        ('single_specific', 'Specific Single-Person Task'),
        ('single_public', 'Public Single-Person Task'),
        ('crowdsource', 'Crowdsourcing Task'),
        ('arbitration', 'Arbitration Task'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    reward = models.DecimalField(max_digits=18, decimal_places=8)
    expiration_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # For specific single-person tasks
    assigned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_tasks'
    )
    
    # For crowdsourcing tasks
    planned_participants = models.IntegerField(null=True, blank=True)
    notified_count = models.IntegerField(default=0)
    response_count = models.IntegerField(default=0)
    participation_count = models.IntegerField(default=0)
    completion_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'tasks'

class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    file = models.FileField(upload_to='task_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_attachments'

class ArbitrationTask(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    voting_options = models.JSONField()  # Store options as JSON array
    required_arbitrators = models.IntegerField()
    margin_requirement = models.DecimalField(max_digits=18, decimal_places=8)
    voting_deadline = models.DateTimeField()
    result = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'arbitration_tasks'

class ArbitrationVote(models.Model):
    arbitration = models.ForeignKey(ArbitrationTask, on_delete=models.CASCADE)
    arbitrator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vote_option = models.CharField(max_length=100)
    voted_at = models.DateTimeField(auto_now_add=True)
    margin_locked = models.DecimalField(max_digits=18, decimal_places=8)

    class Meta:
        db_table = 'arbitration_votes' 