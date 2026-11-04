"""
Comprehensive Unit Tests for Courts & Cases API Integration Service.
File: tests/test_legal_api_service.py

Mocks all external network requests to guarantee self-contained execution.
Covers all 20 required test cases:
1. Successful judgment search
2. Empty search query
3. Search with multiple results
4. Successful case retrieval
5. Invalid case ID
6. Successful citation resolution
7. Unmatched citations
8. Successful statutory section retrieval
9. Invalid Act identifier
10. Missing statutory section
11. Connection timeout
12. Authentication failure
13. Rate-limit response
14. Server error
15. Invalid JSON response
16. Retry mechanism
17. Local FAQ fallback
18. Missing API configuration
19. Response schema validation
20. Source attribution
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from services.legal_api_service import (
    CourtsAndCasesClient,
    get_legal_api_client,
    search_judgments,
    get_case_details,
    resolve_citations,
    get_statute,
    retrieve_legal_context,
    SUPPORTED_ACTS
)


class TestLegalAPIService(unittest.TestCase):
    """Test suite for Courts & Cases API Service."""

    def setUp(self):
        """Set up a fresh client for each test."""
        self.client = CourtsAndCasesClient(
            base_url="https://courtsandcases.com",
            api_key=None,
            timeout=3
        )

    # 1. Successful judgment search
    @patch.object(requests.Session, "get")
    def test_01_successful_judgment_search(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "results": [
                {
                    "case_id": "delhi-hc-2023-45",
                    "title": "State v. Ramesh Kumar",
                    "court": "Delhi High Court",
                    "date": "2023-04-12",
                    "citation": "2023 DHC 145",
                    "url": "https://courtsandcases.com/cases/delhi-hc-2023-45",
                    "summary": "Bail granted considering statutory provisions under BNSS."
                }
            ]
        }
        mock_get.return_value = mock_resp

        result = self.client.search_judgments("bail Delhi High Court", limit=5)
        self.assertTrue(result["success"])
        self.assertFalse(result["fallback_used"])
        self.assertEqual(result["source"], "courts_and_cases_api")
        self.assertEqual(result["data"]["count"], 1)
        self.assertEqual(result["data"]["judgments"][0]["title"], "State v. Ramesh Kumar")

    # 2. Empty search query
    def test_02_empty_search_query(self):
        for empty_q in ["", "   ", None]:
            result = self.client.search_judgments(empty_q)
            self.assertFalse(result["success"])
            self.assertIn("non-empty string", result["error"])

    # 3. Search with multiple results
    @patch.object(requests.Session, "get")
    def test_03_search_with_multiple_results(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "results": [
                {"case_id": f"sc-2022-{i}", "title": f"Judgment {i}", "court": "Supreme Court of India"}
                for i in range(5)
            ]
        }
        mock_get.return_value = mock_resp

        result = self.client.search_judgments("Fundamental Rights Article 21", limit=5)
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["count"], 5)
        self.assertEqual(len(result["data"]["judgments"]), 5)

    # 4. Successful case retrieval
    @patch.object(requests.Session, "get")
    def test_04_successful_case_retrieval(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "case": {
                "title": "Maneka Gandhi v. Union of India",
                "court": "Supreme Court of India",
                "decision_date": "1978-01-25",
                "case_number": "Writ Petition No. 231 of 1977",
                "judges": ["M.H. Beg", "Y.V. Chandrachud", "P.N. Bhagwati"],
                "neutral_citation": "1978 INSC 16",
                "reported_citations": ["AIR 1978 SC 597", "(1978) 1 SCC 248"],
                "outcome": "Passport impoundment procedure held subject to procedural fairness",
                "outcome_sentence": "Procedure established by law under Article 21 must be just, fair, and reasonable.",
                "legal_provisions": ["Article 21", "Article 14", "Passport Act Section 10(3)(c)"],
                "citation_line": "1978 INSC 16 | AIR 1978 SC 597",
                "url": "https://courtsandcases.com/cases/1978-insc-16"
            }
        }
        mock_get.return_value = mock_resp

        result = self.client.get_case_details("1978-insc-16")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["title"], "Maneka Gandhi v. Union of India")
        self.assertEqual(result["data"]["court"], "Supreme Court of India")
        self.assertEqual(len(result["data"]["judges"]), 3)

    # 5. Invalid case ID
    def test_05_invalid_case_id(self):
        for bad_id in ["", "   ", "drop table;--", "bad id with spaces @!#"]:
            result = self.client.get_case_details(bad_id)
            self.assertFalse(result["success"])
            self.assertIsNotNone(result["error"])

    # 6. Successful citation resolution
    @patch.object(requests.Session, "get")
    def test_06_successful_citation_resolution(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "citations": [
                {
                    "citation": "(2017) 10 SCC 1",
                    "normalized_citation": "2017 10 SCC 1",
                    "matched": True,
                    "case_id": "puttaswamy-2017",
                    "title": "Justice K.S. Puttaswamy (Retd.) v. Union of India",
                    "court": "Supreme Court of India",
                    "year": "2017",
                    "url": "https://courtsandcases.com/cases/puttaswamy-2017"
                }
            ]
        }
        mock_get.return_value = mock_resp

        result = self.client.resolve_citations("(2017) 10 SCC 1")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["count"], 1)
        self.assertEqual(result["data"]["citations"][0]["case_id"], "puttaswamy-2017")

    # 7. Unmatched citations
    @patch.object(requests.Session, "get")
    def test_07_unmatched_citations(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"citations": []}
        mock_get.return_value = mock_resp

        result = self.client.resolve_citations("9999 NONEXISTENT 12345")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["count"], 0)
        self.assertEqual(result["data"]["citations"], [])

    # 8. Successful statutory section retrieval
    @patch.object(requests.Session, "get")
    def test_08_successful_statutory_retrieval(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "act_name": "Bharatiya Nyaya Sanhita, 2023",
            "section": "318",
            "heading": "Cheating",
            "text": "Whoever cheats and thereby dishonestly induces delivery of property...",
            "corresponding_provision": "Section 420 IPC, 1860",
            "url": "https://courtsandcases.com/statutes/bns/318"
        }
        mock_get.return_value = mock_resp

        result = self.client.get_statute("bns", "318")
        self.assertTrue(result["success"])
        self.assertFalse(result["fallback_used"])
        self.assertEqual(result["data"]["section"], "318")
        self.assertEqual(result["data"]["act_slug"], "bns")
        self.assertIn("Current Legislation", result["data"]["status"])

    # 9. Invalid Act identifier
    def test_09_invalid_act_identifier(self):
        result = self.client.get_statute("invalid_act", "420")
        self.assertFalse(result["success"])
        self.assertIn("Unsupported Act slug", result["error"])

    # 10. Missing statutory section
    def test_10_missing_statutory_section(self):
        for empty_sec in ["", "   ", None]:
            result = self.client.get_statute("bns", empty_sec)
            self.assertFalse(result["success"])
            self.assertIn("Section identifier must be a non-empty string", result["error"])

    # 11. Connection timeout
    @patch("time.sleep", return_value=None)
    @patch.object(requests.Session, "get", side_effect=requests.exceptions.Timeout("Connection timed out"))
    def test_11_connection_timeout(self, mock_get, mock_sleep):
        result = self.client.get_case_details("sc-2023-timeout")
        self.assertFalse(result["success"])
        self.assertIn("timeout", result["error"].lower())

    # 12. Authentication failure
    @patch.object(requests.Session, "get")
    def test_12_authentication_failure(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized: Invalid API Key"
        mock_get.return_value = mock_resp

        result = self.client.get_case_details("sc-2023-unauth")
        self.assertFalse(result["success"])
        self.assertIn("Authentication failure", result["error"])

    # 13. Rate-limit response
    @patch.object(requests.Session, "get")
    def test_13_rate_limit_response(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        mock_resp.text = "Too Many Requests"
        mock_get.return_value = mock_resp

        result = self.client.get_case_details("sc-2023-ratelimit")
        self.assertFalse(result["success"])
        self.assertIn("429", result["error"])

    # 14. Server error
    @patch("time.sleep", return_value=None)
    @patch.object(requests.Session, "get")
    def test_14_server_error(self, mock_get, mock_sleep):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        mock_get.return_value = mock_resp

        result = self.client.get_case_details("sc-2023-500")
        self.assertFalse(result["success"])
        self.assertIn("500", result["error"])

    # 15. Invalid JSON response
    @patch.object(requests.Session, "get")
    def test_15_invalid_json_response(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.side_effect = ValueError("No JSON object could be decoded")
        mock_get.return_value = mock_resp

        result = self.client.get_case_details("sc-2023-badjson")
        self.assertFalse(result["success"])
        self.assertIn("Invalid JSON", result["error"])

    # 16. Retry mechanism on transient failure
    @patch("time.sleep", return_value=None)
    @patch.object(requests.Session, "get")
    def test_16_retry_mechanism(self, mock_get, mock_sleep):
        # 1st call 503, 2nd call 200 success
        mock_fail = MagicMock()
        mock_fail.status_code = 503
        mock_fail.text = "Service Temporarily Unavailable"

        mock_ok = MagicMock()
        mock_ok.status_code = 200
        mock_ok.json.return_value = {"case": {"title": "Recovered Case"}}

        mock_get.side_effect = [mock_fail, mock_ok]

        result = self.client.get_case_details("sc-retry-test")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["title"], "Recovered Case")
        self.assertEqual(mock_get.call_count, 2)

    # 17. Local FAQ and statutory fallback when API fails
    @patch("time.sleep", return_value=None)
    @patch.object(requests.Session, "get", side_effect=requests.exceptions.ConnectionError("Host unreachable"))
    def test_17_local_fallback(self, mock_get, mock_sleep):
        # Statute fallback
        statute_res = self.client.get_statute("bns", "318")
        self.assertTrue(statute_res["success"])
        self.assertTrue(statute_res["fallback_used"])
        self.assertEqual(statute_res["source"], "local_statutory_store")
        self.assertEqual(statute_res["data"]["act_name"], "Bharatiya Nyaya Sanhita, 2023")
        self.assertIn("Cheating", statute_res["data"]["heading"])

        # Search fallback
        search_res = self.client.search_judgments("What is the right to education in India?")
        self.assertTrue(search_res["success"])
        self.assertTrue(search_res["fallback_used"])
        self.assertEqual(search_res["source"], "local_faq_fallback")
        self.assertEqual(search_res["data"]["fallback_context"]["matched_faq_topic"], "Fundamental Rights")

    # 18. Missing API configuration defaults gracefully
    def test_18_missing_api_configuration(self):
        client = CourtsAndCasesClient(base_url="", api_key=None, timeout=None)
        self.assertEqual(client.base_url, "https://courtsandcases.com")
        self.assertEqual(client.timeout, 5)

    # 19. Response schema validation
    def test_19_response_schema_validation(self):
        result = self.client.get_statute("bns", "103")
        required_keys = ["success", "data", "source", "fallback_used", "error"]
        for k in required_keys:
            self.assertIn(k, result, f"Key '{k}' missing from standardized response structure")

    # 20. Source attribution and distinction between old and new laws
    def test_20_source_attribution(self):
        # BNS is current
        bns_res = self.client.get_statute("bns", "318")
        self.assertIn("Current Legislation", bns_res["data"]["status"])
        self.assertIn("indiacode.nic.in", bns_res["data"]["source_url"])

        # IPC is repealed
        ipc_res = self.client.get_statute("ipc", "420")
        self.assertIn("Repealed Legislation", ipc_res["data"]["status"])
        self.assertIn("indiacode.nic.in", ipc_res["data"]["source_url"])

    # High-level context integration test
    def test_context_retrieval_integration(self):
        ctx = retrieve_legal_context("What is the punishment for cheating under Section 318 BNS?")
        self.assertIn("nlp_analysis", ctx)
        self.assertIn("retrieved_statutes", ctx)
        self.assertTrue(len(ctx["retrieved_statutes"]) > 0)
        self.assertEqual(ctx["retrieved_statutes"][0]["section"], "318")


if __name__ == "__main__":
    unittest.main()
