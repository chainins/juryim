from django.core.mail import send_mass_mail
from django.utils import timezone
from django.db.models import Q
from .models import Task, ArbitrationTask, ArbitrationVote
from users.models import User
import random

class TaskService:
    @staticmethod
    def calculate_required_notifications(task):
        """Calculate number of users to notify based on previous tasks"""
        previous_tasks = Task.objects.filter(
            task_type='crowdsource',
            status='completed'
        ).order_by('-created_at')[:3]
        
        if not previous_tasks:
            return task.planned_participants * 3
            
        response_rates = []
        for pt in previous_tasks:
            if pt.notified_count > 0:
                response_rates.append(pt.response_count / pt.notified_count)
                
        if not response_rates:
            return task.planned_participants * 3
            
        avg_response_rate = sum(response_rates) / len(response_rates)
        return int(task.planned_participants / avg_response_rate)

    @staticmethod
    def select_arbitrators(arbitration_task):
        """Select random arbitrators based on criteria"""
        eligible_users = User.objects.filter(
            credit_score__gte=100,  # Basic score requirement
            financialaccount__balance__gte=arbitration_task.margin_requirement
        ).exclude(
            arbitrationvote__arbitration=arbitration_task
        )
        
        required_count = arbitration_task.required_arbitrators
        selected_users = random.sample(
            list(eligible_users),
            min(required_count, len(eligible_users))
        )
        
        return selected_users

    @staticmethod
    def notify_arbitrators(arbitration_task, arbitrators):
        """Send email notifications to selected arbitrators"""
        emails = []
        for arbitrator in arbitrators:
            emails.append((
                'Arbitration Task Invitation',
                f'''
                You have been selected as an arbitrator.
                Task: {arbitration_task.task.title}
                Reward: {arbitration_task.task.reward}
                Deadline: {arbitration_task.voting_deadline}
                Required Margin: {arbitration_task.margin_requirement}
                
                Please visit the platform to cast your vote.
                ''',
                'noreply@platform.com',
                [arbitrator.email],
            ))
        
        send_mass_mail(emails)

    @staticmethod
    def calculate_arbitration_result(arbitration_task):
        """Calculate final arbitration result based on 2/3 majority rule"""
        votes = ArbitrationVote.objects.filter(arbitration=arbitration_task)
        total_votes = votes.count()
        
        if total_votes == 0:
            return 'uncertain'
            
        vote_counts = {}
        for vote in votes:
            vote_counts[vote.vote_option] = vote_counts.get(vote.vote_option, 0) + 1
            
        for option, count in vote_counts.items():
            if count >= (total_votes * 2/3):
                return option
                
        return 'uncertain' 