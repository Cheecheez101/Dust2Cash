"""
Tests for the landing app.

This module contains tests for the landing page views and functionality.
"""

from django.test import TestCase, Client
from django.urls import reverse


class LandingPageTestCase(TestCase):
    """Test cases for the landing page."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_landing_page_status_code(self):
        """Test that the landing page returns a 200 status code."""
        # Note: Using 'landing' from core app as that's the root URL
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_landing_page_template(self):
        """Test that the landing page uses the correct template."""
        response = self.client.get('/')
        # The root URL currently uses core's landing template
        self.assertTemplateUsed(response, 'landing.html')

    def test_landing_app_index_view(self):
        """
        Test that the landing app index view works correctly.
        
        TODO: Enable this test when landing app is wired to a URL.
        Currently the core app handles the root URL.
        """
        # This is a placeholder test for when landing app is integrated
        # response = self.client.get(reverse('landing:index'))
        # self.assertEqual(response.status_code, 200)
        pass  # Placeholder - landing app can be integrated at different URL if needed
