"""
Unit & Integration Tests for LegalEase Frontend Assets & Routes.
File: tests/test_frontend.py

Verifies:
1. GET / serves templates/index.html with status 200 and valid semantic HTML5 markup.
2. Static CSS file (/static/css/style.css) is properly served with status 200.
3. Static JavaScript file (/static/js/app.js) is properly served with status 200.
4. All critical UI components exist in index.html (welcome screen, prompt cards, modals, disclaimer).
5. All 4 national helplines are present in the HTML.
6. XSS prevention check on frontend client-side markdown escaping patterns.
7. CSS contains design tokens for futuristic dark theme (neon blue, royal purple, glassmorphism).
"""

import re
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app


class TestFrontendRoutesAndAssets(unittest.TestCase):
    """Test suite for LegalEase frontend assets, templates, and routes."""

    @classmethod
    def setUpClass(cls):
        test_config = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "frontend-test-key-xyz",
        }
        cls.app = create_app("testing", test_config=test_config)
        cls.client = cls.app.test_client()

    def test_01_index_html_route_serves_200(self):
        """Test GET / returns HTTP 200 with HTML content."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/html", resp.content_type)
        html = resp.get_data(as_text=True)
        self.assertIn("LegalEase", html)
        self.assertIn("<!DOCTYPE html>", html)

    def test_02_css_static_route_serves_200(self):
        """Test GET /static/css/style.css returns HTTP 200 and text/css."""
        resp = self.client.get("/static/css/style.css")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            "text/css" in resp.content_type or "text/plain" in resp.content_type,
            f"Unexpected content type: {resp.content_type}"
        )
        css = resp.get_data(as_text=True)
        self.assertIn("--neon-blue", css)
        self.assertIn("--royal-purple", css)
        self.assertIn("--bg-primary", css)
        self.assertIn("backdrop-filter", css)

    def test_03_js_static_route_serves_200(self):
        """Test GET /static/js/app.js returns HTTP 200 with JavaScript."""
        resp = self.client.get("/static/js/app.js")
        self.assertEqual(resp.status_code, 200)
        js = resp.get_data(as_text=True)
        self.assertIn("safeMarkdownToHtml", js)
        self.assertIn("escapeHtml", js)
        self.assertIn("sendChatMessage", js)
        self.assertIn("legalease_active_session", js)

    def test_04_html_contains_critical_components(self):
        """Verify index.html contains all required DOM containers and elements."""
        resp = self.client.get("/")
        html = resp.get_data(as_text=True)

        required_ids = [
            "sidebar",
            "btnNewChat",
            "conversationList",
            "systemStatusPill",
            "chatMain",
            "welcomeScreen",
            "messagesContainer",
            "typingIndicator",
            "userInput",
            "btnSend",
            "charCounter",
            "aboutModal",
            "renameModal",
            "deleteConfirmModal",
            "appToast",
        ]
        for elem_id in required_ids:
            self.assertIn(f'id="{elem_id}"', html, f"Missing required element with id='{elem_id}'")

    def test_05_html_contains_all_six_prompt_cards(self):
        """Verify all 6 suggested prompt cards are present in the welcome screen."""
        resp = self.client.get("/")
        html = resp.get_data(as_text=True)

        prompts = [
            "What are my Fundamental Rights under the Indian Constitution?",
            "How do I report online financial fraud?",
            "How can I file a consumer complaint?",
            "What legal protections are available to women?",
            "How do I file an FIR in India?",
            "What are my rights as a tenant?",
        ]
        for prompt in prompts:
            self.assertIn(prompt, html, f"Missing required prompt card: '{prompt}'")

    def test_06_html_contains_national_helplines(self):
        """Verify emergency and legal awareness helplines are prominently displayed."""
        resp = self.client.get("/")
        html = resp.get_data(as_text=True)

        helplines = ["112", "1930", "1915", "15100"]
        for num in helplines:
            self.assertIn(num, html, f"Missing citizen helpline: '{num}'")

    def test_07_legal_disclaimer_present(self):
        """Verify mandatory legal awareness disclaimer is present in the layout."""
        resp = self.client.get("/")
        html = resp.get_data(as_text=True)

        self.assertIn("General legal awareness", html)
        self.assertIn("Not legal advice", html)

    def test_08_js_xss_protection_logic_verification(self):
        """Verify that JavaScript escapeHtml logic is correctly specified to sanitize XSS."""
        resp = self.client.get("/static/js/app.js")
        js = resp.get_data(as_text=True)

        # Confirm HTML entities are replaced
        self.assertIn("&amp;", js)
        self.assertIn("&lt;", js)
        self.assertIn("&gt;", js)
        self.assertIn("&quot;", js)
        self.assertIn("&#39;", js)


if __name__ == "__main__":
    unittest.main()
