from celery import shared_task

from .models import Transaction


@shared_task
def send_payment_confirmation_task(transaction_id):
    from .views import send_payment_confirmation

    transaction = Transaction.objects.get(id=transaction_id)
    send_payment_confirmation(transaction)
