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
from .services import FinancialService, WithdrawalService
from .utils import generate_qr_code  # Import our QR code utility
from django.utils.decorators import method_decorator
from django.conf import settings

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
    @method_decorator(login_required)
    def withdrawal(request):
        # Initialize withdrawal service
        withdrawal_service = WithdrawalService()
        
        # Get user's balances
        balances = {
            'BTC': request.user.financialaccount.balance,
            'ETH': request.user.financialaccount.balance,
            'USDT': request.user.financialaccount.balance,
        }
        
        # Available networks for withdrawal
        networks = [
            {
                'code': 'BTC',
                'name': 'Bitcoin',
                'fee': settings.NETWORK_FEES['BTC'],
                'min_amount': settings.MIN_DEPOSIT['BTC'],
            },
            {
                'code': 'ETH',
                'name': 'Ethereum',
                'fee': settings.NETWORK_FEES['ETH'],
                'min_amount': settings.MIN_DEPOSIT['ETH'],
            },
            {
                'code': 'USDT',
                'name': 'USDT (TRC20)',
                'fee': settings.NETWORK_FEES['USDT'],
                'min_amount': settings.MIN_DEPOSIT['USDT'],
            },
        ]
        
        if request.method == 'POST':
            try:
                # Get form data
                network = request.POST.get('network')
                amount = Decimal(request.POST.get('amount'))
                address = request.POST.get('address')
                
                # Create withdrawal request
                withdrawal = withdrawal_service.create_withdrawal_request(
                    user=request.user,
                    network=network,
                    amount=amount,
                    address=address
                )
                
                messages.success(request, 'Withdrawal request submitted successfully')
                return redirect('financial:withdrawal_status', withdrawal_id=withdrawal.id)
                
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, 'An error occurred. Please try again.')
                print(f"Withdrawal error: {str(e)}")
        
        # Get recent withdrawals
        recent_withdrawals = WithdrawalRequest.objects.filter(
            account=request.user.financialaccount
        ).order_by('-created_at')[:5]
        
        context = {
            'balances': balances,
            'networks': networks,
            'recent_withdrawals': recent_withdrawals,
        }
        
        return render(request, 'financial/withdrawal.html', context)

    @staticmethod
    @method_decorator(login_required)
    def withdrawal_status(request, withdrawal_id):
        try:
            withdrawal = WithdrawalRequest.objects.get(
                id=withdrawal_id,
                account=request.user.financialaccount
            )
            
            context = {
                'withdrawal': withdrawal,
            }
            
            return render(request, 'financial/withdrawal_status.html', context)
            
        except WithdrawalRequest.DoesNotExist:
            messages.error(request, 'Withdrawal request not found')
            return redirect('financial:withdrawal')

    @staticmethod
    @login_required
    def deposit(request):
        # Available networks for deposits
        networks = [
            {'code': 'BTC', 'name': 'Bitcoin'},
            {'code': 'ETH', 'name': 'Ethereum'},
            {'code': 'USDT', 'name': 'USDT (TRC20)'},
        ]
        
        # Get selected network from query params
        selected_network = request.GET.get('network')
        
        # Get or create deposit address for selected network
        address = None
        qr_code = None
        if selected_network:
            address, created = DepositAddress.objects.get_or_create(
                account=request.user.financialaccount,
                network=selected_network,
                defaults={
                    'min_deposit': '0.001' if selected_network in ['BTC', 'ETH'] else '1.00',
                    'confirmations_required': 2 if selected_network == 'USDT' else 3
                }
            )
            # Generate QR code for the address
            if address:
                qr_code = generate_qr_code(address.address)
        
        # Get recent deposits
        recent_deposits = Transaction.objects.filter(
            account=request.user.financialaccount,
            transaction_type='deposit'
        ).order_by('-created_at')[:5]
        
        context = {
            'networks': networks,
            'selected_network': selected_network,
            'address': address,
            'qr_code': qr_code,
            'recent_deposits': recent_deposits,
        }
        
        return render(request, 'financial/deposit.html', context)

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

@login_required
def dashboard(request):
    """Financial dashboard view"""
    context = {
        'balance': request.user.balance if hasattr(request.user, 'balance') else 0,
        'transactions': Transaction.objects.filter(account__user=request.user).order_by('-created_at')[:5]
    }
    return render(request, 'financial/dashboard.html', context)

@login_required
def deposit(request):
    """Deposit view"""
    if request.method == 'POST':
        amount = request.POST.get('amount')
        # Add deposit logic here
        messages.success(request, 'Deposit initiated successfully')
        return redirect('financial_dashboard')
    return render(request, 'financial/deposit.html')

@login_required
def withdraw(request):
    """Withdraw view"""
    if request.method == 'POST':
        amount = request.POST.get('amount')
        # Add withdrawal logic here
        messages.success(request, 'Withdrawal initiated successfully')
        return redirect('financial_dashboard')
    return render(request, 'financial/withdraw.html')

@login_required
def transactions(request):
    """Transaction history view"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'financial/transactions.html', {'transactions': transactions}) 