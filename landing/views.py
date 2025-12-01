"""
Views for the Dust2Cash landing page application.

This module provides simple views to render the landing page
that introduces users to Dust2Cash and encourages sign-up.
"""

from django.shortcuts import render


def index(request):
    """
    Render the main landing page.

    This view displays the Dust2Cash landing page with information
    about the platform and a call-to-action to sign up.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered landing page.

    TODO:
        - Add dynamic content (e.g., exchange rates, testimonials)
        - Integrate with authentication system for logged-in users
    """
    context = {
        'page_title': 'Dust2Cash - Convert Crypto to Cash',
    }
    return render(request, 'landing/index.html', context)
