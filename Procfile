web: gunicorn dust2cash.wsgi:application --timeout 120
worker: celery -A dust2cash worker --loglevel=info
beat: celery -A dust2cash beat --loglevel=info

