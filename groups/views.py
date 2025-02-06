from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Group, GroupMember, GroupVote, GroupChat, GroupFund, GroupVoteResponse
from .forms import GroupForm, GroupVoteForm, GroupFundForm
from .services import GroupService

class GroupViews:
    @staticmethod
    @login_required
    def create_group(request):
        if request.method == 'POST':
            form = GroupForm(request.POST)
            if form.is_valid():
                group = form.save(commit=False)
                group.manager = request.user
                group.save()
                
                # Add creator as member
                GroupMember.objects.create(group=group, user=request.user)
                
                messages.success(request, 'Group created successfully!')
                return redirect('groups:group_detail', group_id=group.id)
        else:
            form = GroupForm()
        return render(request, 'groups/create_group.html', {'form': form})

    @staticmethod
    @login_required
    def group_list(request):
        user_groups = Group.objects.filter(
            Q(groupmember__user=request.user) |
            Q(manager=request.user) |
            Q(authorized_manager=request.user)
        ).distinct()
        
        return render(request, 'groups/group_list.html', {'groups': user_groups})

    @staticmethod
    @login_required
    def group_detail(request, group_id):
        group = get_object_or_404(Group, id=group_id)
        is_member = GroupMember.objects.filter(group=group, user=request.user).exists()
        is_manager = GroupService.check_manager_rights(request.user, group)
        
        if not (is_member or is_manager):
            messages.error(request, 'You do not have access to this group.')
            return redirect('groups:group_list')
            
        context = {
            'group': group,
            'is_member': is_member,
            'is_manager': is_manager,
            'members': GroupMember.objects.filter(group=group),
            'recent_chats': GroupChat.objects.filter(group=group).order_by('-created_at')[:50],
            'active_votes': GroupVote.objects.filter(group=group, status='active'),
            'funds': GroupFund.objects.filter(group=group)
        }
        return render(request, 'groups/group_detail.html', context)

    @staticmethod
    @login_required
    def create_vote(request, group_id):
        group = get_object_or_404(Group, id=group_id)
        if not GroupService.check_manager_rights(request.user, group):
            messages.error(request, 'Only managers can create votes.')
            return redirect('groups:group_detail', group_id=group.id)
            
        if request.method == 'POST':
            form = GroupVoteForm(request.POST)
            if form.is_valid():
                vote = form.save(commit=False)
                vote.group = group
                vote.creator = request.user
                vote.save()
                
                GroupService.notify_vote_creation(vote)
                messages.success(request, 'Vote created successfully!')
                return redirect('groups:group_detail', group_id=group.id)
        else:
            form = GroupVoteForm()
            
        return render(request, 'groups/create_vote.html', {
            'form': form,
            'group': group
        })

    @staticmethod
    @login_required
    def submit_vote(request, vote_id):
        vote = get_object_or_404(GroupVote, id=vote_id)
        if vote.status != 'active':
            messages.error(request, 'This vote is no longer active.')
            return redirect('groups:group_detail', group_id=vote.group.id)
            
        if request.method == 'POST':
            selected_option = request.POST.get('option')
            if selected_option in vote.options:
                GroupVoteResponse.objects.create(
                    vote=vote,
                    user=request.user,
                    selected_option=selected_option
                )
                messages.success(request, 'Vote submitted successfully!')
            else:
                messages.error(request, 'Invalid option selected.')
                
        return redirect('groups:group_detail', group_id=vote.group.id)

    @staticmethod
    @login_required
    def chat_message(request, group_id):
        if request.method == 'POST':
            group = get_object_or_404(Group, id=group_id)
            message = request.POST.get('message', '').strip()
            
            if message:
                GroupChat.objects.create(
                    group=group,
                    user=request.user,
                    message=message
                )
                
        return redirect('groups:group_detail', group_id=group_id) 