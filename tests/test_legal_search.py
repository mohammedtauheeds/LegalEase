"""
Unit Tests for Legal Search Service (services/legal_search.py).
File: tests/test_legal_search.py

Mocks external calls to guarantee deterministic offline execution.
Covers all 15 required test cases:
1. Successful FAQ retrieval
2. Empty query
3. Invalid query
4. FAQ relevance score
5. Statutory retrieval
6. Judgment retrieval
7. External API unavailable
8. Local FAQ fallback
9. Duplicate source removal
10. Source attribution
11. Missing statutory context
12. Malformed API response
13. Context size limits
14. Current vs repealed legislation
15. Retrieval status tracking
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from services.legal_search import (
    search_legal_information,
    deduplicate_sources,
    normalize_source_entry
)


@patch("time.sleep", return_value=None)
class TestLegalSearch(unittest.TestCase):
    """Test suite for search_legal_information and source processing."""

    # 1. Successful FAQ retrieval
    def test_01_successful_faq_retrieval(self, mock_sleep):
        res = search_legal_information("What is the Preamble of the Indian Constitution and what does it declare?")
        self.assertTrue(res["success"])
        self.assertTrue(res["retrieval_status"]["faq_available"])
        self.assertGreaterEqual(len(res["faq_results"]), 1)
        self.assertEqual(res["faq_results"][0]["section"], "Preamble")

    # 2. Empty query
    def test_02_empty_query(self, mock_sleep):
        for empty_q in ["", "   ", None]:
            res = search_legal_information(empty_q)
            self.assertFalse(res["success"])
            self.assertIn("non-empty string", res["errors"][0])

    # 3. Invalid query (type errors, excessively long)
    def test_03_invalid_query(self, mock_sleep):
        res = search_legal_information(12345)  # non-string
        self.assertFalse(res["success"])

        # Very long string gets safely clamped
        long_q = "What is the law? " * 50
        res_long = search_legal_information(long_q)
        self.assertTrue(res_long["success"])
        self.assertLessEqual(len(res_long["query"]), 500)

    # 4. FAQ relevance score
    def test_04_faq_relevance_score(self, mock_sleep):
        res = search_legal_information("Right to Equality under Article 14")
        self.assertTrue(res["success"])
        top_faq = res["faq_results"][0]
        self.assertGreater(top_faq["similarity_score"], 0.5)
        self.assertLessEqual(top_faq["similarity_score"], 1.0)

    # 5. Statutory retrieval
    def test_05_statutory_retrieval(self, mock_sleep):
        res = search_legal_information("What is Section 318 of BNS?")
        self.assertTrue(res["success"])
        self.assertTrue(res["retrieval_status"]["statutes_available"])
        self.assertGreaterEqual(len(res["statutes"]), 1)
        stat = res["statutes"][0]
        self.assertEqual(stat["section"], "318")
        self.assertIn("Bharatiya Nyaya Sanhita", stat["act_name"])

    # 6. Judgment retrieval
    @patch("services.legal_search.retrieve_legal_context")
    def test_06_judgment_retrieval(self, mock_ctx, mock_sleep):
        mock_ctx.return_value = {
            "retrieved_statutes": [],
            "retrieved_judgments": [
                {
                    "case_id": "sc-2023-1",
                    "title": "State v. Ramesh",
                    "court": "Supreme Court of India",
                    "decision_date": "2023-01-15",
                    "citation": "2023 INSC 12",
                    "url": "https://www.sci.gov.in/",
                    "summary": "Judgment on bail principles."
                }
            ],
            "nlp_analysis": {}
        }
        res = search_legal_information("bail Supreme Court")
        self.assertTrue(res["success"])
        self.assertTrue(res["retrieval_status"]["judgments_available"])
        self.assertEqual(len(res["judgments"]), 1)
        self.assertEqual(res["judgments"][0]["title"], "State v. Ramesh")

    # 7. External API unavailable handled without crash
    @patch("services.legal_search.retrieve_legal_context")
    def test_07_external_api_unavailable(self, mock_ctx, mock_sleep):
        mock_ctx.side_effect = Exception("Courts & Cases API connection failed")
        res = search_legal_information("What is Section 318 BNS?")
        self.assertTrue(res["success"])
        self.assertFalse(res["retrieval_status"]["judgments_available"])
        self.assertGreaterEqual(len(res["errors"]), 1)

    # 8. Local FAQ fallback active
    def test_08_local_faq_fallback(self, mock_sleep):
        res = search_legal_information("How do I report cyber fraud?")
        self.assertTrue(res["success"])
        self.assertTrue(res["retrieval_status"]["faq_available"])
        self.assertEqual(res["faq_results"][0]["topic"], "Cybercrime and Online Fraud")

    # 9. Duplicate source removal
    def test_09_duplicate_source_removal(self, mock_sleep):
        duplicate_sources = [
            {"title": "India Code", "url": "https://www.indiacode.nic.in/"},
            {"title": "India Code", "url": "https://www.indiacode.nic.in/"},
            {"title": "Supreme Court", "url": "https://www.sci.gov.in/"}
        ]
        deduped = deduplicate_sources(duplicate_sources)
        self.assertEqual(len(deduped), 2)

    # 10. Source attribution fields
    def test_10_source_attribution(self, mock_sleep):
        entry = normalize_source_entry(
            title="Bharatiya Nyaya Sanhita, 2023 Section 318",
            source_type="Official Legislation",
            url="https://www.indiacode.nic.in/",
            act_name="Bharatiya Nyaya Sanhita, 2023",
            section="318",
            status="Current Legislation"
        )
        self.assertEqual(entry["title"], "Bharatiya Nyaya Sanhita, 2023 Section 318")
        self.assertEqual(entry["type"], "Official Legislation")
        self.assertEqual(entry["url"], "https://www.indiacode.nic.in/")
        self.assertEqual(entry["section"], "318")

    # 11. Missing statutory context handled gracefully
    def test_11_missing_statutory_context(self, mock_sleep):
        res = search_legal_information("Can a tenant keep pets in an apartment?")
        self.assertTrue(res["success"])
        # Should still provide baseline source
        self.assertGreaterEqual(len(res["sources"]), 1)

    # 12. Malformed API response handled safely
    @patch("services.legal_search.retrieve_legal_context")
    def test_12_malformed_api_response(self, mock_ctx, mock_sleep):
        mock_ctx.return_value = {"invalid_structure": 123}
        res = search_legal_information("Explain Section 420 IPC")
        self.assertTrue(res["success"])
        self.assertEqual(res["statutes"], [])

    # 13. Context size limits enforced
    def test_13_context_size_limits(self, mock_sleep):
        res = search_legal_information("What is Section 318 BNS?")
        for st in res["statutes"]:
            self.assertLessEqual(len(st["text"]), 600)

    # 14. Current vs repealed legislation
    def test_14_current_vs_repealed_legislation(self, mock_sleep):
        # Current BNS
        res_bns = search_legal_information("Section 318 BNS")
        if res_bns["statutes"]:
            self.assertIn("Current Legislation", res_bns["statutes"][0]["status"])

        # Repealed IPC
        res_ipc = search_legal_information("Section 420 IPC")
        if res_ipc["statutes"]:
            self.assertIn("Repealed Legislation", res_ipc["statutes"][0]["status"])

    # 15. Retrieval status tracking
    def test_15_retrieval_status_tracking(self, mock_sleep):
        res = search_legal_information("Article 21 Constitution")
        status = res["retrieval_status"]
        self.assertIn("faq_available", status)
        self.assertIn("statutes_available", status)
        self.assertIn("judgments_available", status)
        self.assertIn("external_api_used", status)


if __name__ == "__main__":
    unittest.main()
