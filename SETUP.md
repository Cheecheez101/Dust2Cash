# Landing App Setup Guide

This document describes how to integrate the `landing` app into the Dust2Cash Django project.

## Current Configuration

The Dust2Cash project currently uses the `core` app's landing view at the root URL (`/`). The `landing` app provides an alternative, standalone landing page that can be used instead or alongside the existing setup.

## Option 1: Use the Landing App at Root URL

To replace the existing landing page with the new `landing` app:

1. **Update `dust2cash/urls.py`:**

   ```python
   from django.contrib import admin
   from django.urls import path, include

   urlpatterns = [
       path('admin/', admin.site.urls),
       path('', include('landing.urls')),  # Landing app at root
       path('app/', include('core.urls')),  # Move core app to /app/
   ]
   ```

2. **Update links in core templates** to use the new URL prefix (e.g., `/app/login/`).

## Option 2: Use the Landing App at a Different URL

To keep the existing setup and add the landing app at a different URL:

1. **Update `dust2cash/urls.py`:**

   ```python
   from django.contrib import admin
   from django.urls import path, include

   urlpatterns = [
       path('admin/', admin.site.urls),
       path('', include('core.urls')),          # Keep existing setup
       path('landing/', include('landing.urls')), # Landing app at /landing/
   ]
   ```

2. Access the new landing page at `/landing/`.

## Option 3: Replace Core Landing View Only

To use the landing app's template while keeping core app URLs:

1. **Update `core/views.py`:**

   ```python
   def landing(request):
       return render(request, 'landing/index.html', {
           'page_title': 'Dust2Cash - Convert Crypto to Cash',
       })
   ```

2. This uses the new template without changing URL configuration.

## Static Files

The landing app includes its own static files. After making changes, collect static files:

```bash
python manage.py collectstatic
```

## Testing

Run tests to ensure the landing app works correctly:

```bash
python manage.py test landing
```

## TODO

- [ ] Integrate Daraja API credentials for M-Pesa payouts
- [ ] Add real email verification for sign-up
- [ ] Configure PostgreSQL for production
- [ ] Add SSL/TLS for secure connections
