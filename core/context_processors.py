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
