from celery import shared_task
from django.utils import timezone

from .models import Transaction, AgentRequest


@shared_task
def send_payment_confirmation_task(transaction_id):
    from .views import send_payment_confirmation

    transaction = Transaction.objects.get(id=transaction_id)
    send_payment_confirmation(transaction)


@shared_task
def expire_agent_requests():
    now = timezone.now()
    requests = AgentRequest.objects.filter(is_expired=False, is_accepted=False, expires_at__lt=now)
    updated = requests.update(is_expired=True)
    for agent_request in AgentRequest.objects.filter(pk__in=requests.values_list('pk', flat=True)):
        transaction = agent_request.transaction
        transaction.status = 'cancelled'
        transaction.save(update_fields=['status'])
    return updated
