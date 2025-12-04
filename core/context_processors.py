# core/context_processors.py

def dust2cash_settings(request):
    return {
        'settings': {
            'buying_rate_per_usdt': 100.00,
            'transaction_fee_percent': 1.50,
            'min_trade_amount_usdt': 5.00,
        },
        'now': {
            'year': 2025  # you can replace with datetime.now().year
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
