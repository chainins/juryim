from django.core.mail import send_mass_mail
from django.conf import settings
from django.utils import timezone
from .models import Group, GroupMember, GroupVote, GroupVoteResponse

class GroupService:
    @staticmethod
    def notify_vote_creation(vote):
        """Notify all group members about a new vote"""
        members = GroupMember.objects.filter(group=vote.group)
        emails = []
        
        for member in members:
            emails.append((
                f'New Vote in {vote.group.name}',
                f'''
                A new vote has been created:
                Title: {vote.title}
                Description: {vote.description}
                Deadline: {vote.deadline}
                
                Please login to cast your vote.
                ''',
                settings.DEFAULT_FROM_EMAIL,
                [member.user.email],
            ))
            
        send_mass_mail(emails)

    @staticmethod
    def check_manager_rights(user, group):
        """Check if user has manager rights"""
        if user == group.manager:
            return True
        if user == group.authorized_manager:
            return True
        return False

    @staticmethod
    def transfer_management(group, from_user, to_user):
        """Transfer group management rights"""
        if from_user != group.manager and from_user != group.authorized_manager:
            return False
            
        if from_user == group.manager:
            group.manager = to_user
            group.authorized_manager = None
        else:
            group.authorized_manager = to_user
            
        group.save()
        return True

    @staticmethod
    def calculate_vote_results(vote):
        """Calculate the results of a group vote"""
        responses = GroupVoteResponse.objects.filter(vote=vote)
        results = {}
        
        for response in responses:
            results[response.selected_option] = results.get(response.selected_option, 0) + 1
            
        return results 