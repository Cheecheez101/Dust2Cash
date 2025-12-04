from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    title = models.CharField(max_length=120, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Admin: {self.user.get_full_name() or self.user.username}"


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    phone_number = models.CharField(max_length=15)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_complete(self):
        return all([self.phone_number, self.first_name, self.last_name, self.email])

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"


class AgentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    is_online = models.BooleanField(default=False)
    last_online = models.DateTimeField(null=True, blank=True)

    def go_online(self):
        self.is_online = True
        self.last_online = timezone.now()
        self.save()

    def go_offline(self):
        self.is_online = False
        self.save()

    def __str__(self):
        return f"Agent: {self.user.username}"


class Transaction(models.Model):
    PLATFORM_CHOICES = [
        ('binance', 'Binance'),
        ('bybit', 'Bybit'),
        ('bitget', 'Bitget'),
    ]

    CURRENCY_CHOICES = [
        ('usdt', 'USDT'),
        ('worldcoin', 'WorldCoin'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('airtel', 'Airtel Money'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('agent_requested', 'Agent Requested'),
        ('agent_online', 'Agent Online'),
        ('address_provided', 'Address Provided'),
        ('crypto_received', 'Crypto Received'),
        ('payment_sent', 'Payment Sent'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='transactions')
    agent = models.ForeignKey(AgentProfile, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='transactions')

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    currency = models.CharField(max_length=20, choices=CURRENCY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    exchange_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('100.00'))
    transaction_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    amount_to_receive = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_phone = models.CharField(max_length=15)

    transfer_address = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    request_timeout = models.DateTimeField(null=True, blank=True)

    def calculate_amount_to_receive(self):
        # Ensure all operands are Decimal for precision
        total = (self.amount * Decimal(self.exchange_rate)) - self.transaction_fee
        self.amount_to_receive = total
        return total

    def __str__(self):
        return f"Transaction {self.id} - {self.client} - {self.amount} {self.currency}"

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"


class AgentRequest(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='agent_request')
    requested_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_accepted = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)

    def check_expiry(self):
        if timezone.now() > self.expires_at and not self.is_accepted:
            self.is_expired = True
            self.save()
            return True
        return False

    def __str__(self):
        return f"Request for Transaction {self.transaction.id}"
