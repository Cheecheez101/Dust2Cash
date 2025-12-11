from django.shortcuts import render, redirect, get_object_or_404
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from datetime import timedelta
from decimal import Decimal
import csv
import logging
from django.http import HttpResponse, Http404, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, FormView
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.db import transaction
from django.db.models import Count, Q, Exists, OuterRef
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.utils.html import strip_tags
from .forms import LoginForm, SignUpForm, ClientProfileForm, TransactionForm, AgentApplicationForm, PricingSettingsForm, OTPForm, IDUploadForm, OTPRequestForm
from .utils.africas_talking import send_otp, verify_otp
from .models import AccountVerification

from .decorators import agent_required, client_required
from .forms import LoginForm, SignUpForm, ClientProfileForm, TransactionForm, AgentApplicationForm, PricingSettingsForm
from .tasks import send_payment_confirmation_task

logger = logging.getLogger(__name__)

try:
    from services.email.sib_client import send_transactional_email, is_email_client_configured
except Exception:
    send_transactional_email = None
    is_email_client_configured = lambda: False


def _fallback_send_mail(to_email, subject, html_content=None, text_content=None):
    text_body = text_content or strip_tags(html_content or '')
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@michaelnganga.me')
    email = EmailMultiAlternatives(subject, text_body, from_email, [to_email])
    if html_content:
        email.attach_alternative(html_content, 'text/html')
    email.send(fail_silently=False)


def send_email_notification(*, to_email, subject, html_content=None, text_content=None):
    if not to_email:
        logger.warning("No recipient provided for subject '%s'", subject)
        return False
    try:
        if send_transactional_email:
            send_transactional_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content or text_content or '',
                text_content=text_content,
            )
        else:
            _fallback_send_mail(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
            )
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False


# Lazy-model loader to avoid importing Django models at module import time
_models_loaded = False
ClientProfile = AgentProfile = Transaction = AgentRequest = AdminProfile = AgentApplication = PricingSettings = None

def ensure_models_loaded():
    """Import models when first needed to avoid AppRegistryNotReady during module import."""
    global _models_loaded, ClientProfile, AgentProfile, Transaction, AgentRequest, AdminProfile, AgentApplication, PricingSettings
    if _models_loaded:
        return
    from . import models as _models
    ClientProfile = _models.ClientProfile
    AgentProfile = _models.AgentProfile
    Transaction = _models.Transaction
    AgentRequest = _models.AgentRequest
    AdminProfile = _models.AdminProfile
    AgentApplication = _models.AgentApplication
    PricingSettings = _models.PricingSettings
    _models_loaded = True



def landing(request):
    return render(request, 'landing.html')


def about_page(request):
    ensure_models_loaded()
    active_agents = AgentProfile.objects.filter(is_online=True).select_related('user').order_by('user__first_name')
    return render(request, 'about.html', {'active_agents': active_agents})


def contact_page(request):
    # Render form on GET; handle submission on POST
    email_backend = getattr(settings, 'EMAIL_BACKEND', '')
    context = {
        'email_ready': bool(send_transactional_email) or email_backend != 'django.core.mail.backends.dummy.EmailBackend'
    }
    if request.method == 'POST':
        name = f"{request.POST.get('first_name','').strip()} {request.POST.get('last_name','').strip()}".strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        message = request.POST.get('message', '').strip()
        contact_method = request.POST.get('contact_method', 'email')

        # Basic server-side validation
        if not name or not email or not message:
            messages.error(request, 'Please complete the form before submitting.')
            return render(request, 'contact.html', context)

        # Admin notification
        ADMIN_EMAIL = getattr(settings, 'ADMIN_EMAIL', os.getenv('ADMIN_EMAIL', 'michaelnganga678@gmail.com'))
        admin_html = f"""
        <h3>New Message from Portfolio Contact Form</h3>
        <p><b>Name:</b> {name}<br>
           <b>Email:</b> {email}<br>
           <b>Subject:</b> Contact form submission</p>
        <p><b>Message:</b><br>{message}</p>
        <p><b>Phone:</b> {phone}</p>
        <p><b>Preferred contact method:</b> {contact_method}</p>
        """
        text_body = (
            "New message from Dust2Cash contact form.\n"
            f"Name: {name}\nEmail: {email}\nPhone: {phone}\n"
            f"Preferred contact method: {contact_method}\n\nMessage:\n{message}"
        )

        admin_sent = send_email_notification(
            to_email=ADMIN_EMAIL,
            subject="Dust2Cash Contact Form Submission",
            html_content=admin_html,
            text_content=text_body,
        )
        if not admin_sent:
            messages.warning(
                request,
                'Message received, but we could not send the admin notification email.',
            )

        # Auto-reply to user
        user_html = f"""
        <h3>Hi {name.split(' ')[0] if name else 'there'},</h3>
        <p>Thank you for contacting <b>Michael Ng'ang'a</b>! I’ve received your message:</p>
        <blockquote>{message}</blockquote>
        <p>I’ll get back to you as soon as possible.</p>
        <br>
        <p>Best regards,<br>Michael Ng'ang'a</p>
        """
        user_sent = send_email_notification(
            to_email=email,
            subject="We received your Dust2Cash inquiry",
            html_content=user_html,
            text_content=f"Hi {name or 'there'},\n\nThanks for contacting Dust2Cash. We'll respond shortly.\n\nMessage: {message}",
        )
        if not user_sent:
            messages.info(
                request,
                'We received your message, but the confirmation email could not be delivered.',
            )

        messages.success(request, 'Thank you — your message has been sent. We\'ll reply shortly.')
        return redirect('contact')

    return render(request, 'contact.html', context)


def pricing_page(request):
    return render(request, 'pricing.html')


def how_it_works_page(request):
    return render(request, 'how_it_works.html')


def features_page(request):
    return render(request, 'features.html')


def redirect_user_by_role(user):
    if user.is_staff:
        return redirect('admin_dashboard')
    if hasattr(user, 'agent_profile'):
        return redirect('agent_portal')
    if hasattr(user, 'client_profile'):
        return redirect('client_dashboard')
    return redirect('landing')


def login_view(request):
    ensure_models_loaded()
    if request.user.is_authenticated:
        return redirect_user_by_role(request.user)

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        identifier = form.cleaned_data['identifier']
        password = form.cleaned_data['password']
        try:
            if '@' in identifier:
                user = User.objects.get(email=identifier)
            else:
                user = User.objects.get(username=identifier)
            user = authenticate(request, username=user.username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Welcome back!')
                if user.is_staff:
                    ensure_models_loaded()
                    AdminProfile.objects.get_or_create(user=user)
                return redirect_user_by_role(user)
            else:
                messages.error(request, 'Invalid credentials')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email')
    
    return render(request, 'auth/login.html', {'form': form})


def signup_view(request):
    ensure_models_loaded()
    if request.user.is_authenticated:
        return redirect_user_by_role(request.user)

    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        
        ClientProfile.objects.create(
            user=user,
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=form.cleaned_data['email'],
        )
        if user.is_staff:
            AdminProfile.objects.get_or_create(user=user)

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
    ensure_models_loaded()
    try:
        profile = request.user.client_profile
    except ClientProfile.DoesNotExist:
        profile = ClientProfile.objects.create(user=request.user)
    verification, _ = AccountVerification.objects.get_or_create(user=request.user)

    form = ClientProfileForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('client_dashboard')
    
    return render(request, 'client/profile.html', {'form': form, 'profile': profile, 'account_verification': verification})


@login_required
def client_dashboard(request):
    ensure_models_loaded()
    try:
        profile = request.user.client_profile
        if not profile.is_complete():
            messages.warning(request, 'Please complete your profile to start transactions')
            return redirect('client_profile')
    except ClientProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first')
        return redirect('client_profile')
    verification, _ = AccountVerification.objects.get_or_create(user=request.user)

    agent_online = AgentProfile.objects.filter(is_online=True).exists()
    
    transactions = Transaction.objects.filter(client=profile).order_by('-created_at')
    requestable_transaction = transactions.filter(status__in=['pending', 'agent_requested']).first()

    pricing = PricingSettings.get_solo()
    context = {
        'profile': profile,
        'agent_online': agent_online,
        'transactions': transactions,
        'requestable_transaction': requestable_transaction,
        'pricing': pricing,
        'account_verification': verification,
    }
    return render(request, 'client/dashboard.html', context)


@login_required
def create_transaction(request):
    ensure_models_loaded()
    try:
        profile = request.user.client_profile
        if not profile.is_complete():
            messages.warning(request, 'Please complete your profile first')
            return redirect('client_profile')
    except ClientProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile first')
        return redirect('client_profile')

    active_agents = AgentProfile.objects.filter(is_online=True)

    form = TransactionForm(request.POST or None, active_agents=active_agents)
    pricing = PricingSettings.get_solo()
    if request.method == "POST" and form.is_valid():
        transaction = form.save(commit=False)
        transaction.client = profile
        transaction.exchange_rate = pricing.exchange_rate
        fee_percent = pricing.transaction_fee_percent / Decimal('100')
        transaction.transaction_fee = transaction.amount * fee_percent * Decimal(pricing.exchange_rate)
        transaction.calculate_amount_to_receive()
        selected_agent = form.cleaned_data.get('agent')

        if selected_agent:
            transaction.agent = selected_agent
            transaction.status = 'agent_online'
        else:
            transaction.status = 'pending'
        transaction.save()

        if selected_agent:
            messages.success(
                request,
                f'Transaction created! {transaction.agent.user.get_full_name() or transaction.agent.user.username} will assist you.'
            )
            return redirect('request_address', transaction_id=transaction.id)

        messages.info(request, 'Transaction captured. Request an agent to get assistance when one comes online.')
        return redirect('request_agent', transaction_id=transaction.id)

    return render(request, 'client/create_transaction.html', {
        'form': form,
        'active_agents': active_agents,
        'pricing': pricing,
    })


@login_required
def request_agent(request, transaction_id):
    ensure_models_loaded()
    transaction = get_object_or_404(Transaction, id=transaction_id, client=request.user.client_profile)

    if transaction.status not in ['pending', 'agent_requested']:
        messages.warning(request, 'This transaction is already being handled by an agent.')
        return redirect('client_dashboard')

    agent_request = getattr(transaction, 'agent_request', None)
    if agent_request:
        agent_request.check_expiry()

    if request.method == "POST":
        if agent_request and not agent_request.is_expired and not agent_request.is_accepted:
            messages.info(request, 'You already have an active agent request. Please wait for a response.')
            return redirect('client_dashboard')

        expires_at = timezone.now() + timedelta(minutes=15)
        if agent_request:
            agent_request.requested_at = timezone.now()
            agent_request.expires_at = expires_at
            agent_request.is_expired = False
            agent_request.is_accepted = False
            agent_request.save(update_fields=['requested_at', 'expires_at', 'is_expired', 'is_accepted'])
        else:
            agent_request = AgentRequest.objects.create(
                transaction=transaction,
                expires_at=expires_at
            )

        transaction.status = 'agent_requested'
        transaction.request_timeout = expires_at
        transaction.save(update_fields=['status', 'request_timeout'])

        send_notification_to_agent(transaction)

        messages.success(request, 'Agent request sent! You have 15 minutes to wait for a response.')
        return redirect('client_dashboard')

    return render(request, 'client/request_agent.html', {
        'transaction': transaction,
        'agent_request': agent_request,
    })


@login_required
def request_address(request, transaction_id):
    ensure_models_loaded()
    transaction = get_object_or_404(Transaction, id=transaction_id, client=request.user.client_profile)
    
    if transaction.status == 'pending' or transaction.status == 'agent_requested':
        messages.warning(request, 'Waiting for agent to come online')
        return redirect('client_dashboard')
    
    return render(request, 'client/request_address.html', {'transaction': transaction})


@agent_required
def agent_portal(request):
    ensure_models_loaded()
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
    ensure_models_loaded()
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
    ensure_models_loaded()
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
    
    return render(request, 'agent/provide_address.html', {'transaction': transaction, 'agent': agent})


@agent_required
def agent_confirm_receipt(request, transaction_id):
    ensure_models_loaded()
    agent = request.user.agent_profile
    transaction = get_object_or_404(Transaction, id=transaction_id, agent=agent)
    
    if request.method == "POST":
        transaction.status = 'crypto_received'
        transaction.save()
        messages.success(request, 'Crypto receipt confirmed. Please send payment now.')
        return redirect('agent_send_payment', transaction_id=transaction.id)
    
    return render(request, 'agent/confirm_receipt.html', {'transaction': transaction, 'agent': agent})


@agent_required
def agent_send_payment(request, transaction_id):
    ensure_models_loaded()
    agent = request.user.agent_profile
    transaction = get_object_or_404(Transaction, id=transaction_id, agent=agent)
    
    if request.method == "POST":
        transaction.status = 'payment_sent'
        transaction.save()

        send_payment_confirmation_task.delay(transaction.id)

        messages.success(request, 'Payment marked as sent!')
        return redirect('agent_portal')
    
    return render(request, 'agent/send_payment.html', {'transaction': transaction, 'agent': agent})

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
                send_email_notification(
                    to_email=agent.user.email,
                    subject='New Client Request on Dust2Cash',
                    text_content=message,
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
                send_email_notification(
                    to_email=client_email,
                    subject='Agent is Now Online - Dust2Cash',
                    text_content=message,
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
            send_email_notification(
                to_email=client_email,
                subject='Agent Accepted Your Request - Dust2Cash',
                text_content=message,
            )
        except Exception as e:
            print(f"Error sending email: {e}")


@method_decorator(staff_member_required, name='dispatch')
class AdminDashboardView(TemplateView):
    template_name = 'admin/dashboard.html'

    def get_context_data(self, **kwargs):
        ensure_models_loaded()
        context = super().get_context_data(**kwargs)
        verified_clients = AccountVerification.objects.filter(limits_unlocked=True).count()
        context.update({
            'client_count': ClientProfile.objects.count(),
            'agent_count': AgentProfile.objects.count(),
            'transaction_count': Transaction.objects.count(),
            'reports_count': Transaction.objects.count(),
            'verified_client_count': verified_clients,
            'application_count': AgentApplication.objects.filter(status=AgentApplication.STATUS_PENDING).count(),
            'pricing': PricingSettings.get_solo(),
        })
        return context


class AdminClientListView(ListView):
    template_name = 'admin/clients_list.html'
    context_object_name = 'clients'

    def dispatch(self, request, *args, **kwargs):
        ensure_models_loaded()
        self.model = ClientProfile
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.model.objects.all().select_related('user').annotate(
            is_verified=Exists(
                AccountVerification.objects.filter(user=OuterRef('user_id'), limits_unlocked=True)
            )
        )
        status = self.request.GET.get('verification')
        if status == 'verified':
            qs = qs.filter(is_verified=True)
        elif status == 'pending':
            qs = qs.filter(is_verified=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_filter'] = self.request.GET.get('verification', '')
        context['verified_summary'] = AccountVerification.objects.aggregate(
            verified=Count('id', filter=Q(limits_unlocked=True)),
            pending=Count('id', filter=Q(limits_unlocked=False))
        )
        return context


class AdminClientCreateView(CreateView):
    template_name = 'admin/client_form.html'
    success_url = reverse_lazy('admin_clients')
    fields = ['first_name', 'last_name', 'phone_number', 'email']

    def dispatch(self, request, *args, **kwargs):
        ensure_models_loaded()
        self.model = ClientProfile
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email']
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user = User.objects.create_user(
            username=username,
            email=email,
            password=User.objects.make_random_password()
        )
        form.instance.user = user
        return super().form_valid(form)


class AdminClientUpdateView(UpdateView):
    template_name = 'admin/client_form.html'
    success_url = reverse_lazy('admin_clients')
    fields = ['first_name', 'last_name', 'phone_number', 'email']

    def dispatch(self, request, *args, **kwargs):
        ensure_models_loaded()
        self.model = ClientProfile
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object.user
        if user:
            user.email = self.object.email
            user.save(update_fields=['email'])
        return response


class AdminClientDeleteView(DeleteView):
    template_name = 'admin/client_confirm_delete.html'
    success_url = reverse_lazy('admin_clients')

    def dispatch(self, request, *args, **kwargs):
        ensure_models_loaded()
        self.model = ClientProfile
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.object.user
        response = super().delete(request, *args, **kwargs)
        if user:
            user.delete()
        return response


class AdminAgentListView(ListView):
    template_name = 'admin/agents_list.html'
    context_object_name = 'agents'

    def dispatch(self, request, *args, **kwargs):
        ensure_models_loaded()
        self.model = AgentProfile
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.all()


class AdminAgentCreateView(CreateView):
    template_name = 'admin/agent_form.html'
    success_url = reverse_lazy('admin_agents')
    fields = ['user', 'is_online']

    def dispatch(self, request, *args, **kwargs):
        ensure_models_loaded()
        self.model = AgentProfile
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['user'].queryset = User.objects.filter(agent_profile__isnull=True)
        return form


class AdminAgentUpdateView(UpdateView):
    template_name = 'admin/agent_form.html'
    success_url = reverse_lazy('admin_agents')
    fields = ['is_online']

    def dispatch(self, request, *args, **kwargs):
        ensure_models_loaded()
        self.model = AgentProfile
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['is_online'].label = 'Currently online'
        return form


class AdminAgentDeleteView(DeleteView):
    template_name = 'admin/agent_confirm_delete.html'
    success_url = reverse_lazy('admin_agents')

    def dispatch(self, request, *args, **kwargs):
        ensure_models_loaded()
        self.model = AgentProfile
        return super().dispatch(request, *args, **kwargs)


class AdminTransactionListView(ListView):
    template_name = 'admin/transactions_list.html'
    context_object_name = 'transactions'
    ordering = ['-created_at']

    def dispatch(self, request, *args, **kwargs):
        ensure_models_loaded()
        self.model = Transaction
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.order_by('-created_at')


class AdminTransactionUpdateView(UpdateView):
    template_name = 'admin/transaction_form.html'
    success_url = reverse_lazy('admin_transactions')
    fields = ['status', 'exchange_rate', 'transaction_fee', 'amount_to_receive']

    def dispatch(self, request, *args, **kwargs):
        ensure_models_loaded()
        self.model = Transaction
        return super().dispatch(request, *args, **kwargs)


class AdminTransactionDeleteView(DeleteView):
    template_name = 'admin/transaction_confirm_delete.html'
    success_url = reverse_lazy('admin_transactions')

    def dispatch(self, request, *args, **kwargs):
        ensure_models_loaded()
        self.model = Transaction
        return super().dispatch(request, *args, **kwargs)


class AdminReportsView(TemplateView):
    template_name = 'admin/reports.html'

    def get_context_data(self, **kwargs):
        ensure_models_loaded()
        context = super().get_context_data(**kwargs)
        clients = ClientProfile.objects.select_related('user').order_by('-created_at')[:25]
        agents = AgentProfile.objects.select_related('user').order_by('-last_online')[:25]
        transactions_qs = Transaction.objects.select_related('client__user', 'agent__user').order_by('-created_at')
        status_filter = self.request.GET.get('status') or ''
        platform_filter = self.request.GET.get('platform') or ''
        if status_filter:
            transactions_qs = transactions_qs.filter(status=status_filter)
        if platform_filter:
            transactions_qs = transactions_qs.filter(platform=platform_filter)
        context.update({
            'clients_preview': clients,
            'agents_preview': agents,
            'transactions_preview': transactions_qs[:50],
            'transaction_status_choices': Transaction.STATUS_CHOICES,
            'transaction_platform_choices': Transaction.PLATFORM_CHOICES,
            'active_filters': {
                'status': status_filter,
                'platform': platform_filter,
            },
            'verified_summary': AccountVerification.objects.aggregate(
                verified=Count('id', filter=Q(limits_unlocked=True)),
                pending=Count('id', filter=Q(limits_unlocked=False)),
            ),
        })
        return context


@method_decorator(staff_member_required, name='dispatch')
class AdminAgentApplicationListView(ListView):
    template_name = 'admin/applications_list.html'
    context_object_name = 'applications'
    paginate_by = 25

    def dispatch(self, request, *args, **kwargs):
        ensure_models_loaded()
        self.model = AgentApplication
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.model.objects.all()
        status_filter = self.request.GET.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


@method_decorator(staff_member_required, name='dispatch')
class AdminAgentApplicationDeleteView(DeleteView):
    template_name = 'admin/application_confirm_delete.html'
    success_url = reverse_lazy('admin_applications')

    def dispatch(self, request, *args, **kwargs):
        ensure_models_loaded()
        self.model = AgentApplication
        return super().dispatch(request, *args, **kwargs)


@method_decorator(staff_member_required, name='dispatch')
class AdminApplicationCreateUserView(FormView):
    template_name = 'admin/application_create_user.html'
    form_class = UserCreationForm

    def dispatch(self, request, *args, **kwargs):
        self.application = get_object_or_404(AgentApplication, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.first_name = self.application.full_name.split(' ')[0]
        user.last_name = ' '.join(self.application.full_name.split(' ')[1:])
        user.email = self.application.email
        user.is_staff = False
        user.is_superuser = False
        user.save()
        AgentProfile.objects.get_or_create(user=user)
        messages.success(self.request, 'Admin user created and linked to application.')
        return redirect('admin_application_detail', pk=self.application.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = self.application
        return context


@login_required
@staff_member_required
def admin_pricing_settings(request):
    pricing = PricingSettings.get_solo()
    form = PricingSettingsForm(request.POST or None, instance=pricing)
    if request.method == "POST" and form.is_valid():
        updated_pricing = form.save(commit=False)
        if request.user.is_authenticated:
            updated_pricing.updated_by = request.user
        updated_pricing.save()
        messages.success(request, 'Pricing settings updated successfully.')
        return redirect('admin_pricing_settings')
    return render(request, 'admin/pricing_settings.html', {'form': form, 'pricing': pricing})


@staff_member_required
def export_clients_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="clients.csv"'
    writer = csv.writer(response)
    writer.writerow(['First Name', 'Last Name', 'Email', 'Phone', 'Created'])
    for client in ClientProfile.objects.all():
        writer.writerow([client.first_name, client.last_name, client.email, client.phone_number, client.created_at])
    return response


@staff_member_required
def export_agents_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="agents.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Online', 'Last Online'])
    for agent in AgentProfile.objects.select_related('user'):
        writer.writerow([agent.user.username, agent.user.email, agent.is_online, agent.last_online])
    return response


@staff_member_required
def export_transactions_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Client', 'Agent', 'Amount', 'Currency', 'Status', 'Created'])
    for tx in Transaction.objects.select_related('client', 'agent'):
        writer.writerow([tx.id, str(tx.client), str(tx.agent) if tx.agent else '', tx.amount, tx.get_currency_display(), tx.get_status_display(), tx.created_at])
    return response


def apply_agent(request):
    if request.method == 'POST':
        form = AgentApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application submitted! Our compliance team will reach out soon.')
            return redirect('apply_agent')
    else:
        form = AgentApplicationForm()
    return render(request, 'agent/apply.html', {'form': form})


@method_decorator(staff_member_required, name='dispatch')
class AdminAgentApplicationDetailView(TemplateView):
    template_name = 'admin/application_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = get_object_or_404(AgentApplication, pk=kwargs['pk'])
        context['application'] = application
        return context

    def post(self, request, *args, **kwargs):
        application = get_object_or_404(AgentApplication, pk=kwargs['pk'])
        application.review_notes = request.POST.get('review_notes', '').strip()
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.save(update_fields=['review_notes', 'reviewed_by', 'reviewed_at'])
        messages.success(request, 'Review notes updated.')
        return redirect('admin_application_detail', pk=application.pk)


@staff_member_required
def admin_application_verify(request, pk):
    ensure_models_loaded()
    application = get_object_or_404(AgentApplication, pk=pk)
    names = application.full_name.split()
    first_name = names[0]
    last_name = ' '.join(names[1:]) if len(names) > 1 else ''
    password = None
    if not application.created_user:
        base_username = application.email.split('@')[0]
        candidate = base_username
        UserModel = get_user_model()
        while UserModel.objects.filter(username=candidate).exists():
            candidate = f"{base_username}{get_random_string(4)}"
        password = get_random_string(12)
        with transaction.atomic():
            user = UserModel.objects.create_user(
                username=candidate,
                email=application.email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=False,
                is_superuser=False,
            )
            AgentProfile.objects.get_or_create(user=user)
            application.created_user = user
    application.status = AgentApplication.STATUS_VERIFIED
    application.reviewed_by = request.user
    application.reviewed_at = timezone.now()
    application.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'created_user'])
    if password:
        send_email_notification(
            to_email=application.email,
            subject='Welcome to Dust2Cash Agent Network',
            text_content=(
                f"Hi {application.full_name},\n\n"
                f"Your agent application has been approved.\n"
                f"Username: {application.created_user.username}\n"
                f"Temporary password: {password}\n\n"
                "Please log in and update your credentials."
            ),
        )
    messages.success(request, 'Application marked as verified.')
    return redirect('admin_application_detail', pk=pk)


@staff_member_required
def admin_application_cancel(request, pk):
    application = get_object_or_404(AgentApplication, pk=pk)
    application.status = AgentApplication.STATUS_CANCELLED
    application.reviewed_by = request.user
    application.reviewed_at = timezone.now()
    application.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])
    messages.success(request, 'Application marked as cancelled.')
    return redirect('admin_application_detail', pk=pk)


@method_decorator(staff_member_required, name='dispatch')
class AdminAgentApplicationDeleteView(DeleteView):
    template_name = 'admin/application_confirm_delete.html'
    success_url = reverse_lazy('admin_applications')

    def dispatch(self, request, *args, **kwargs):
        ensure_models_loaded()
        self.model = AgentApplication
        return super().dispatch(request, *args, **kwargs)


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('landing')


@login_required
@agent_required
def agent_profile(request):
    ensure_models_loaded()
    user = request.user
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        user.first_name = first_name
        user.last_name = last_name
        if email:
            user.email = email
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('agent_portal')

    context = {
        'agent': getattr(request.user, 'agent_profile', None),
        'user': user,
    }
    return render(request, 'agent/edit_profile.html', context)


@login_required
def change_password(request):
    ensure_models_loaded()
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was updated successfully.')
            next_url = request.POST.get('next') or request.GET.get('next') or (request.user.agent_profile and reverse_lazy('agent_portal')) or reverse_lazy('client_dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'auth/change_password.html', {'form': form})


@login_required
def client_interactions(request):
    ensure_models_loaded()
    profile = request.user.client_profile
    pending_requests = getattr(profile, 'pending_requests', [])
    conversations = []
    context = {
        'pending_requests': pending_requests,
        'conversations': conversations,
    }
    return render(request, 'client/interactions.html', context)


@login_required
@agent_required
def agent_interactions(request):
    ensure_models_loaded()
    agent = request.user.agent_profile
    waiting_clients = []
    conversations = []
    context = {
        'waiting_clients': waiting_clients,
        'conversations': conversations,
        'agent': agent,
    }
    return render(request, 'agent/interactions.html', context)


@login_required
def request_otp_view(request):
    form = OTPRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        phone = form.cleaned_data['phone_number']
        try:
            send_otp(phone)
            messages.success(request, "OTP sent successfully")
            return redirect("verify_otp")
        except ValueError as exc:
            form.add_error('phone_number', str(exc))
        except Exception:
            messages.error(request, 'We could not send the OTP right now. Please try again in a moment.')
    return render(request, "auth/request_otp.html", {'form': form})


@login_required
def verify_otp_view(request):
    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone_number"]
            otp = form.cleaned_data["otp"]
            if verify_otp(phone, otp, user=request.user):
                messages.success(request, "Phone verified successfully!")
                return redirect("client_dashboard")
            else:
                messages.error(request, "Invalid OTP. Try again.")
    else:
        form = OTPForm()
    return render(request, "auth/verify_otp.html", {"form": form})


@login_required
def upload_id_view(request):
    verification, _ = AccountVerification.objects.get_or_create(user=request.user)
    form = IDUploadForm(request.POST or None, request.FILES or None, instance=verification)
    if request.method == 'POST' and form.is_valid():
        form.save(user=request.user)
        messages.success(request, 'Government ID uploaded successfully!')
        return redirect('client_dashboard')
    return render(request, 'auth/upload_id.html', {'form': form, 'account_verification': verification})


@csrf_exempt
def sms_delivery_report(request):
    data = request.POST.dict() if request.method == 'POST' else {}
    logger.info('Africa\'s Talking delivery report: %s', data)
    return JsonResponse({'status': 'ok'})


@login_required
def verify_phone_view(request):
    template = 'client/verify_phone.html'
    if request.method == 'POST':
        phone = request.POST.get('phone')
        if not phone:
            messages.error(request, 'Enter the phone number linked to your account.')
            return render(request, template)
        try:
            send_otp(phone)
            request.session['otp_phone'] = phone
            messages.success(request, 'OTP sent successfully.')
            return redirect('verify_otp')
        except ValueError as exc:
            messages.error(request, str(exc))
        except Exception:
            messages.error(request, 'Could not send OTP. Try again in a moment.')
    return render(request, template)
