from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from .models import (
    FinancialAccount, Transaction, WithdrawalRequest,
    DepositAddress, PaymentProvider
)
from groups.models import GroupFund
from decimal import Decimal
from .forms import WithdrawalForm, DepositAddressForm
from .services import FinancialService

class FinancialViews:
    @staticmethod
    @login_required
    def dashboard(request):
        account = FinancialAccount.objects.get_or_create(user=request.user)[0]
        recent_transactions = Transaction.objects.filter(
            account=account
        ).order_by('-created_at')[:10]
        
        balance_info = FinancialService.get_account_balance(request.user)
        
        return render(request, 'financial/dashboard.html', {
            'account': account,
            'balance_info': balance_info,
            'recent_transactions': recent_transactions
        })

    @staticmethod
    @login_required
    def transaction_history(request):
        account = FinancialAccount.objects.get(user=request.user)
        transaction_type = request.GET.get('type')
        
        transactions = FinancialService.get_transaction_history(
            account, transaction_type
        )
        
        return render(request, 'financial/transaction_history.html', {
            'transactions': transactions
        })

    @staticmethod
    @login_required
    def withdrawal(request):
        account = FinancialAccount.objects.get(user=request.user)
        provider = PaymentProvider.objects.filter(is_active=True).first()
        
        if request.method == 'POST':
            form = WithdrawalForm(
                request.POST,
                account=account,
                provider=provider
            )
            if form.is_valid():
                try:
                    withdrawal = form.save(commit=False)
                    withdrawal.account = account
                    withdrawal.fee = FinancialService.calculate_withdrawal_fee(
                        withdrawal.amount,
                        provider
                    )
                    withdrawal.save()
                    
                    FinancialService.process_withdrawal(withdrawal)
                    messages.success(request, 'Withdrawal request submitted successfully')
                    return redirect('financial:withdrawal_status', withdrawal.id)
                except ValueError as e:
                    messages.error(request, str(e))
        else:
            form = WithdrawalForm(account=account, provider=provider)
        
        return render(request, 'financial/withdrawal.html', {
            'form': form,
            'provider': provider
        })

    @staticmethod
    @login_required
    def withdrawal_status(request, withdrawal_id):
        withdrawal = get_object_or_404(
            WithdrawalRequest,
            id=withdrawal_id,
            account__user=request.user
        )
        return render(request, 'financial/withdrawal_status.html', {
            'withdrawal': withdrawal
        })

    @staticmethod
    @login_required
    def deposit(request):
        account = FinancialAccount.objects.get(user=request.user)
        providers = PaymentProvider.objects.filter(is_active=True)
        
        if request.method == 'POST':
            form = DepositAddressForm(
                request.POST,
                networks=[(p.provider_type, p.name) for p in providers]
            )
            if form.is_valid():
                network = form.cleaned_data['network']
                address = FinancialService.get_deposit_address(account, network)
                return render(request, 'financial/deposit_address.html', {
                    'address': address,
                    'network': network
                })
        else:
            form = DepositAddressForm(
                networks=[(p.provider_type, p.name) for p in providers]
            )
        
        return render(request, 'financial/deposit.html', {
            'form': form,
            'providers': providers
        })

    @staticmethod
    @login_required
    def get_balance(request):
        """AJAX endpoint for getting current balance"""
        balance_info = FinancialService.get_account_balance(request.user)
        return JsonResponse(balance_info)

    @staticmethod
    @login_required
    def account_overview(request):
        account = FinancialAccount.objects.get_or_create(user=request.user)[0]
        recent_transactions = Transaction.objects.filter(
            account=account
        ).order_by('-created_at')[:10]
        
        return render(request, 'financial/account_overview.html', {
            'account': account,
            'recent_transactions': recent_transactions
        })

    @staticmethod
    @login_required
    @transaction.atomic
    def transfer_to_group(request, fund_id):
        if request.method == 'POST':
            amount = Decimal(request.POST.get('amount', '0'))
            fund = get_object_or_404(GroupFund, id=fund_id)
            account = get_object_or_404(FinancialAccount, user=request.user)
            
            if amount <= 0:
                messages.error(request, 'Invalid transfer amount.')
                return redirect('groups:group_detail', group_id=fund.group.id)
                
            if account.balance < amount:
                messages.error(request, 'Insufficient funds.')
                return redirect('groups:group_detail', group_id=fund.group.id)
                
            # Create transaction record
            Transaction.objects.create(
                account=account,
                transaction_type='transfer',
                amount=-amount,
                reference_id=f'group_fund_{fund.id}',
                status='completed'
            )
            
            # Update balances
            account.balance -= amount
            account.save()
            
            fund.balance += amount
            fund.save()
            
            messages.success(request, f'Successfully transferred {amount} to group fund.')
            return redirect('groups:group_detail', group_id=fund.group.id)
            
        return redirect('financial:account_overview')

    @staticmethod
    @login_required
    @transaction.atomic
    def freeze_margin(request, amount):
        """Freeze margin for arbitration or gambling"""
        account = get_object_or_404(FinancialAccount, user=request.user)
        
        if account.balance < amount:
            return False
            
        account.balance -= amount
        account.frozen_balance += amount
        account.save()
        return True

    @staticmethod
    @login_required
    @transaction.atomic
    def unfreeze_margin(request, amount):
        """Unfreeze margin after arbitration or gambling"""
        account = get_object_or_404(FinancialAccount, user=request.user)
        
        if account.frozen_balance < amount:
            return False
            
        account.frozen_balance -= amount
        account.balance += amount
        account.save()
        return True 