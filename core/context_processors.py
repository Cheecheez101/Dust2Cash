# core/context_processors.py
from .models import PricingSettings
from django.utils import timezone


def dust2cash_settings(request):
    pricing = PricingSettings.get_solo()
    return {
        'settings': {
            'buying_rate_per_usdt': float(pricing.exchange_rate),
            'transaction_fee_percent': float(pricing.transaction_fee_percent),
            'min_trade_amount_usdt': 5.00,
        },
        'now': {
            'year': timezone.now().year if hasattr(timezone, 'now') else 2025
        }
    }

def user_portal(request):
    dashboard_url = None
    role = 'guest'

    if request.user.is_authenticated:
        if request.user.is_staff:
            dashboard_url = 'admin_dashboard'
            role = 'admin'
        else:
            try:
                if request.user.agent_profile:
                    dashboard_url = 'agent_portal'
                    role = 'agent'
            except Exception:
                try:
                    if request.user.client_profile:
                        dashboard_url = 'client_dashboard'
                        role = 'client'
                except Exception:
                    role = 'user'

    return {
        'user_portal': {
            'dashboard_url': dashboard_url,
            'role': role,
        }
    }
