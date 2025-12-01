"""
Tests for the landing app.

This module contains tests for the landing page views and functionality.

Note: The landing app provides an alternative landing page that can be used
instead of or alongside the core app's landing page. See SETUP.md for
integration instructions.
"""

from django.test import TestCase, Client


class LandingPageTestCase(TestCase):
    """Test cases for the landing page functionality."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_root_url_returns_200(self):
        """Test that the root URL returns a 200 status code."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_root_url_uses_core_landing_template(self):
        """
        Test that the root URL uses the core app's landing template.
        
        The core app currently handles the root URL with 'landing.html'.
        The landing app's template is at 'landing/index.html' and can be
        integrated using the instructions in SETUP.md.
        """
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'landing.html')

    def test_landing_app_view_import(self):
        """Test that the landing app views can be imported correctly."""
        from landing.views import index
        self.assertIsNotNone(index)

    def test_landing_app_urls_import(self):
        """Test that the landing app URLs can be imported correctly."""
        from landing.urls import urlpatterns
        self.assertIsNotNone(urlpatterns)
        self.assertTrue(len(urlpatterns) > 0)
