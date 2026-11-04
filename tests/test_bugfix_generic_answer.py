"""
Unit and Integration Tests for Bug Fix: Resolving Identical Generic Answers in LegalEase.
File: tests/test_bugfix_generic_answer.py

Proves:
1. Different legal questions generate different, relevant, and specific answers.
2. FAQ matching and NLP reference extraction extract the correct statutory sections.
3. RAG retrieves appropriate statutory context for theft, common law, 420, FIR, and rights.
4. Missing/placeholder API configuration produces a clear diagnostic notice rather than an opaque generic string.
5. Gemini generative pipeline functions properly when configured and falls back gracefully.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import Config
from models.legal_nlp import find_best_faq, get_nlp_engine
from services.legal_search import search_legal_information
from services.gemini_service import GeminiService
from services.rag_service import generate_rag_response


@patch("time.sleep", return_value=None)
class TestBugfixGenericAnswer(unittest.TestCase):
    """Test suite proving diverse, specific answers replace identical generic responses."""

    def test_01_different_questions_generate_different_answers(self, mock_sleep):
        """Verify that distinct legal questions produce unique, tailored answers."""
        queries = [
            "Theft case",
            "Common law rule",
            "420 case explanation",
            "How do I file an FIR?",
            "What are my fundamental rights?"
        ]

        answers = {}
        for q in queries:
            res = generate_rag_response(q)
            self.assertIsNotNone(res.get("answer"))
            self.assertGreater(len(res["answer"]), 50)
            answers[q] = res["answer"]

        # Ensure all queries generate distinct responses
        unique_answers = set(answers.values())
        self.assertEqual(len(unique_answers), len(queries), "Every distinct query must receive a distinct answer!")

    def test_02_theft_query_retrieval(self, mock_sleep):
        """Verify 'Theft case' retrieves Section 303 BNS and Section 378 IPC."""
        search_res = search_legal_information("Theft case")
        statutes = search_res.get("statutes", [])
        sections = [s.get("section") for s in statutes]
        self.assertTrue(any(sec in ("303", "378") for sec in sections), f"Expected section 303 or 378, got {sections}")

        rag_res = generate_rag_response("Theft case")
        self.assertIn("303", rag_res["answer"])
        self.assertTrue("theft" in rag_res["answer"].lower() or "movable property" in rag_res["answer"].lower())

    def test_03_common_law_retrieval(self, mock_sleep):
        """Verify 'Common law rule' retrieves Article 141 (doctrine of precedent) and explains stare decisis."""
        search_res = search_legal_information("Common law rule")
        statutes = search_res.get("statutes", [])
        sections = [s.get("section") for s in statutes]
        self.assertIn("141", sections, f"Expected constitutional Article 141, got {sections}")

        rag_res = generate_rag_response("Common law rule")
        self.assertIn("141", rag_res["answer"])
        self.assertTrue("precedent" in rag_res["answer"].lower() or "stare decisis" in rag_res["answer"].lower())

    def test_04_420_case_retrieval(self, mock_sleep):
        """Verify '420 case explanation' retrieves Section 420 IPC and Section 318 BNS."""
        search_res = search_legal_information("420 case explanation")
        statutes = search_res.get("statutes", [])
        sections = [s.get("section") for s in statutes]
        self.assertTrue(any(sec in ("420", "318") for sec in sections), f"Expected 420 or 318, got {sections}")

        rag_res = generate_rag_response("420 case explanation")
        self.assertIn("318", rag_res["answer"])
        self.assertTrue("cheating" in rag_res["answer"].lower())

    def test_05_fir_procedure_retrieval(self, mock_sleep):
        """Verify 'How do I file an FIR?' retrieves Section 173 BNSS."""
        search_res = search_legal_information("How do I file an FIR?")
        statutes = search_res.get("statutes", [])
        sections = [s.get("section") for s in statutes]
        self.assertIn("173", sections, f"Expected Section 173 BNSS, got {sections}")

        rag_res = generate_rag_response("How do I file an FIR?")
        self.assertIn("173", rag_res["answer"])
        self.assertTrue("fir" in rag_res["answer"].lower())

    def test_06_fundamental_rights_retrieval(self, mock_sleep):
        """Verify 'What are my fundamental rights?' retrieves Part III of the Constitution."""
        rag_res = generate_rag_response("What are my fundamental rights?")
        self.assertTrue("equality" in rag_res["answer"].lower() or "freedom" in rag_res["answer"].lower())
        self.assertIn("Constitution", rag_res["answer"])

    def test_07_missing_api_key_clear_diagnostic(self, mock_sleep):
        """Verify missing or placeholder API configuration gives a clear diagnostic in error and answer."""
        svc = GeminiService(api_key="your_gemini_api_key_here", model="gemini-2.5-flash")
        res = svc.generate_legal_answer("Theft case")
        self.assertFalse(res["success"])
        self.assertTrue(res["fallback_used"])
        self.assertIn("GEMINI_API_KEY", res["error"])
        # Clear notice appended to the answer
        self.assertIn("Notice:", res["answer"])
        self.assertIn("Section 303", res["answer"])

    def test_08_no_generic_default_when_provisions_exist(self, mock_sleep):
        """Verify specific queries never receive the uninformative generic string."""
        old_generic_string = "Regarding your inquiry, Indian law provides specific statutory protections under the Constitution and relevant central legislation."
        for q in ["Theft case", "Common law rule", "420 case explanation", "How do I file an FIR?"]:
            res = generate_rag_response(q)
            self.assertNotIn(old_generic_string, res["answer"], f"Query '{q}' returned the uninformative generic string!")

    def test_09_gemini_invoked_when_configured(self, mock_sleep):
        """Verify Gemini API is invoked when a client is active and question requires generation."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Grounded generative explanation: Under BNS Section 303, theft is punishable with up to 3 years."
        mock_client.models.generate_content.return_value = mock_response

        svc = GeminiService(api_key="valid-mock-key-12345", model="gemini-2.5-flash")
        svc.client = mock_client
        svc._init_error = None

        with patch("services.rag_service.get_gemini_service", return_value=svc):
            res = svc.generate_legal_answer("Explain theft under Indian law in detail.")
            self.assertTrue(res["success"])
            self.assertFalse(res["fallback_used"])
            self.assertIn("BNS Section 303", res["answer"])
            self.assertTrue(mock_client.models.generate_content.called)


if __name__ == "__main__":
    unittest.main()
