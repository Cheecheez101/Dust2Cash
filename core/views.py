from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from decimal import Decimal

from .models import ClientProfile, AgentProfile, Transaction, AgentRequest
from .forms import LoginForm, SignUpForm, ClientProfileForm, TransactionForm
from .decorators import agent_required, client_required


def landing(request):
    return render(request, 'landing.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('client_dashboard')
    
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Welcome back!')
                return redirect('client_dashboard')
            else:
                messages.error(request, 'Invalid credentials')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email')
    
    return render(request, 'auth/login.html', {'form': form})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('client_dashboard')
    
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        
        ClientProfile.objects.create(
            user=user,
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=form.cleaned_data['email'],
        )
        
        login(request, user)
        messages.success(request, 'Account created successfully! Please complete your profile.')
        return redirect('client_profile')
    
    return render(request, 'auth/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('landing')


@login_required
def client_profile(request):
    try:
        profile = request.user.client_profile
    except ClientProfile.DoesNotExist:
        profile = ClientProfile.objects.create(user=request.user)
    
    form = ClientProfileForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('client_dashboard')
    
    return render(request, 'client/profile.html', {'form': form, 'profile': profile})


@login_required
def client_dashboard(request):
    try:
        profile = request.user.client_profile
        if not profile.is_complete():
            messages.warning(request, 'Please complete your profile to start transactions')
            return redirect('client_profile')
    except ClientProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first')
        return redirect('client_profile')
    
    agent_online = AgentProfile.objects.filter(is_online=True).exists()
    
    transactions = Transaction.objects.filter(client=profile).order_by('-created_at')
    
    context = {
        'profile': profile,
        'agent_online': agent_online,
        'transactions': transactions,
    }
    return render(request, 'client/dashboard.html', context)


@login_required
def create_transaction(request):
    try:
        profile = request.user.client_profile
        if not profile.is_complete():
            messages.warning(request, 'Please complete your profile first')
            return redirect('client_profile')
    except ClientProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first')
        return redirect('client_profile')
    
    agent_online = AgentProfile.objects.filter(is_online=True).exists()
    
    form = TransactionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        transaction = form.save(commit=False)
        transaction.client = profile
        transaction.calculate_amount_to_receive()
        
        if agent_online:
            available_agent = AgentProfile.objects.filter(is_online=True).first()
            transaction.agent = available_agent
            transaction.status = 'agent_online'
            transaction.save()
            messages.success(request, 'Transaction created! Agent is online.')
            return redirect('request_address', transaction_id=transaction.id)
        else:
            transaction.status = 'pending'
            transaction.save()
            messages.info(request, 'No agent is currently online. You can request assistance.')
            return redirect('request_agent', transaction_id=transaction.id)
    
    return render(request, 'client/create_transaction.html', {
        'form': form,
        'agent_online': agent_online
    })


@login_required
def request_agent(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, client=request.user.client_profile)
    
    if request.method == "POST":
        expires_at = timezone.now() + timedelta(minutes=15)
        agent_request = AgentRequest.objects.create(
            transaction=transaction,
            expires_at=expires_at
        )
        transaction.status = 'agent_requested'
        transaction.request_timeout = expires_at
        transaction.save()
        
        send_notification_to_agent(transaction)
        
        messages.success(request, 'Agent request sent! You have 15 minutes to wait for a response.')
        return redirect('client_dashboard')
    
    return render(request, 'client/request_agent.html', {'transaction': transaction})


@login_required
def request_address(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, client=request.user.client_profile)
    
    if transaction.status == 'pending' or transaction.status == 'agent_requested':
        messages.warning(request, 'Waiting for agent to come online')
        return redirect('client_dashboard')
    
    return render(request, 'client/request_address.html', {'transaction': transaction})


def agent_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None and hasattr(user, 'agent_profile'):
            login(request, user)
            return redirect('agent_portal')
        else:
            messages.error(request, 'Invalid credentials or not an agent.')
            return redirect('agent_login')

    return render(request, 'agent/login.html')


@agent_required
def agent_portal(request):
    agent = request.user.agent_profile
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'go_online':
            agent.go_online()
            notify_waiting_clients(agent)
            messages.success(request, 'You are now online!')
        elif action == 'go_offline':
            agent.go_offline()
            messages.success(request, 'You are now offline')
    
    pending_requests = AgentRequest.objects.filter(
        is_accepted=False,
        is_expired=False
    ).select_related('transaction').order_by('-requested_at')
    
    active_transactions = Transaction.objects.filter(
        agent=agent,
        status__in=['agent_online', 'address_provided', 'crypto_received']
    ).order_by('-created_at')
    
    completed_transactions = Transaction.objects.filter(
        agent=agent,
        status__in=['payment_sent', 'completed']
    ).order_by('-created_at')[:10]
    
    context = {
        'agent': agent,
        'pending_requests': pending_requests,
        'active_transactions': active_transactions,
        'completed_transactions': completed_transactions,
    }
    return render(request, 'agent/portal.html', context)


@agent_required
def agent_accept_request(request, request_id):
    agent = request.user.agent_profile
    agent_request = get_object_or_404(AgentRequest, id=request_id)
    
    if not agent_request.check_expiry():
        agent_request.is_accepted = True
        agent_request.save()
        
        transaction = agent_request.transaction
        transaction.agent = agent
        transaction.status = 'agent_online'
        transaction.save()
        
        send_agent_online_notification(transaction)
        
        messages.success(request, 'Request accepted!')
    else:
        messages.warning(request, 'This request has expired')
    
    return redirect('agent_portal')


@agent_required
def agent_provide_address(request, transaction_id):
    agent = request.user.agent_profile
    transaction = get_object_or_404(Transaction, id=transaction_id, agent=agent)
    
    if request.method == "POST":
        address = request.POST.get('transfer_address')
        if address:
            transaction.transfer_address = address
            transaction.status = 'address_provided'
            transaction.save()
            messages.success(request, 'Address provided to client')
            return redirect('agent_portal')
    
    return render(request, 'agent/provide_address.html', {'transaction': transaction})


@agent_required
def agent_confirm_receipt(request, transaction_id):
    agent = request.user.agent_profile
    transaction = get_object_or_404(Transaction, id=transaction_id, agent=agent)
    
    if request.method == "POST":
        transaction.status = 'crypto_received'
        transaction.save()
        messages.success(request, 'Crypto receipt confirmed. Please send payment now.')
        return redirect('agent_send_payment', transaction_id=transaction.id)
    
    return render(request, 'agent/confirm_receipt.html', {'transaction': transaction})


@agent_required
def agent_send_payment(request, transaction_id):
    agent = request.user.agent_profile
    transaction = get_object_or_404(Transaction, id=transaction_id, agent=agent)
    
    if request.method == "POST":
        transaction.status = 'payment_sent'
        transaction.save()
        
        send_payment_confirmation(transaction)
        
        messages.success(request, 'Payment marked as sent!')
        return redirect('agent_portal')
    
    return render(request, 'agent/send_payment.html', {'transaction': transaction})


def send_notification_to_agent(transaction):
    try:
        agents = AgentProfile.objects.all()
        for agent in agents:
            if agent.user.email:
                message = f"""
New Client Request on Dust2Cash

A client needs assistance with a crypto conversion:

Transaction Details:
- Client: {transaction.client.first_name} {transaction.client.last_name}
- Platform: {transaction.get_platform_display()}
- Currency: {transaction.get_currency_display()}
- Amount: {transaction.amount} {transaction.get_currency_display()}
- Payment Method: {transaction.get_payment_method_display()}
- Amount to Pay: KSH {transaction.amount_to_receive}

The request will expire in 15 minutes if not accepted.

To accept this request, please log in to the agent portal:
https://dust2cash.com/agent/portal/

Best regards,
Dust2Cash Team
"""
                send_mail(
                    'New Client Request on Dust2Cash',
                    message,
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@dust2cash.com',
                    [agent.user.email],
                    fail_silently=True,
                )
    except Exception as e:
        print(f"Error sending email: {e}")


def notify_waiting_clients(agent):
    pending_requests = AgentRequest.objects.filter(
        is_accepted=False,
        is_expired=False
    )
    
    for agent_request in pending_requests:
        transaction = agent_request.transaction
        client_email = transaction.client.email
        if client_email:
            try:
                message = f"""
Agent is Now Online - Dust2Cash

Good news! An agent has come online and is ready to assist with your transaction.

Your Transaction:
- Platform: {transaction.get_platform_display()}
- Amount: {transaction.amount} {transaction.get_currency_display()}
- To Receive: KSH {transaction.amount_to_receive}

Please log in to your dashboard to check the status:
https://dust2cash.com/client/dashboard/

The agent will review your request shortly.

Best regards,
Dust2Cash Team
"""
                send_mail(
                    'Agent is Now Online - Dust2Cash',
                    message,
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@dust2cash.com',
                    [client_email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Error sending email: {e}")


def send_agent_online_notification(transaction):
    client_email = transaction.client.email
    if client_email:
        try:
            message = f"""
Agent Accepted Your Request - Dust2Cash

Great news! An agent has accepted your request and is ready to process your transaction.

Transaction Details:
- Platform: {transaction.get_platform_display()}
- Currency: {transaction.get_currency_display()}
- Amount: {transaction.amount} {transaction.get_currency_display()}
- You Will Receive: KSH {transaction.amount_to_receive}
- Payment Method: {transaction.get_payment_method_display()} - {transaction.payment_phone}

Next Steps:
1. Log in to your dashboard
2. View the transfer address provided by the agent
3. Send your crypto to the address
4. Wait for confirmation and payment

View your transaction here:
https://dust2cash.com/client/dashboard/

Best regards,
Dust2Cash Team
"""
            send_mail(
                'Agent Accepted Your Request - Dust2Cash',
                message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@dust2cash.com',
                [client_email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error sending email: {e}")


def send_payment_confirmation(transaction):
    client_email = transaction.client.email
    if client_email:
        try:
            message = f"""
Payment Sent - Dust2Cash

Your payment has been processed and sent!

Transaction Summary:
- Crypto Sent: {transaction.amount} {transaction.get_currency_display()}
- Exchange Rate: KSH {transaction.exchange_rate} per {transaction.get_currency_display()}
- Payment Amount: KSH {transaction.amount_to_receive}
- Payment Method: {transaction.get_payment_method_display()}
- Payment Phone: {transaction.payment_phone}

The payment has been sent to your {transaction.get_payment_method_display()} number. 
You should receive it shortly.

Thank you for using Dust2Cash!

If you have any issues, please contact our support team.

Best regards,
Dust2Cash Team
"""
            send_mail(
                'Payment Sent - Dust2Cash',
                message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@dust2cash.com',
                [client_email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Error sending email: {e}")
