from django.db import models
from django.conf import settings

class Task(models.Model):
    TASK_STATUS = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_basic_tasks'
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    status = models.CharField(
        max_length=20,
        choices=TASK_STATUS,
        default='pending'
    )
    reward = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class ArbitrationTask(models.Model):
    TASK_STATUS = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_arbitration_tasks'
    )
    arbitrator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='arbitrated_tasks'
    )
    status = models.CharField(
        max_length=20,
        choices=TASK_STATUS,
        default='pending'
    )
    reward = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class ArbitrationVote(models.Model):
    VOTE_CHOICES = (
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('abstain', 'Abstain')
    )

    task = models.ForeignKey(
        ArbitrationTask,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    arbitrator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='arbitration_votes'
    )
    vote = models.CharField(
        max_length=10,
        choices=VOTE_CHOICES
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('task', 'arbitrator')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.arbitrator.username}'s vote on {self.task.title}"
