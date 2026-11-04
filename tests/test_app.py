"""
Comprehensive Unit Tests for Flask Application & REST API (app.py).
File: tests/test_app.py

Uses Flask test_client with an in-memory SQLite database and mocks the RAG service.
Covers all 26 required test cases:
1. Health endpoint
2. Successful chat request
3. Missing message
4. Empty message
5. Invalid JSON
6. Excessively long message
7. New session creation
8. Existing session reuse
9. Unknown session ID
10. User message persistence
11. Assistant message persistence
12. Sources returned correctly
13. Conversation history retrieval
14. Unknown history session
15. Conversation listing
16. Pagination validation
17. Conversation deletion
18. Unknown deletion session
19. Rename conversation
20. Invalid title
21. RAG exception handling
22. RAG offline fallback
23. Session isolation
24. CORS behavior
25. Database failure handling
26. Error response consistency
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app
from models.database import init_db


class TestFlaskApp(unittest.TestCase):
    """Test suite for LegalEase Flask backend endpoints and session handling."""

    def setUp(self):
        """Configure test app with in-memory database."""
        test_config = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret-key-123",
        }
        self.app = create_app("testing", test_config=test_config)
        self.client = self.app.test_client()

    # 1. Health endpoint
    def test_01_health_endpoint(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "LegalEase")

    # 2. Successful chat request
    @patch("app.generate_rag_response")
    def test_02_successful_chat_request(self, mock_rag):
        mock_rag.return_value = {
            "success": True,
            "answer": "Fundamental Rights are enshrined in Part III.",
            "sources": [{"title": "Constitution of India", "url": "https://www.indiacode.nic.in/"}],
            "model": "gemini-2.5-flash",
            "fallback_used": False,
        }

        payload = {"message": "What are my fundamental rights?"}
        resp = self.client.post("/api/chat", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertIn("Part III", data["answer"])
        self.assertIsNotNone(data["session_id"])
        self.assertEqual(len(data["sources"]), 1)

    # 3. Missing message field
    def test_03_missing_message_field(self):
        resp = self.client.post("/api/chat", json={"invalid_key": "test"})
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertFalse(data["success"])
        self.assertIn("required", data["error"])

    # 4. Empty message
    def test_04_empty_message(self):
        for empty_msg in ["", "   "]:
            resp = self.client.post("/api/chat", json={"message": empty_msg})
            self.assertEqual(resp.status_code, 400)
            data = resp.get_json()
            self.assertFalse(data["success"])
            self.assertIn("empty", data["error"].lower())

    # 5. Invalid JSON payload
    def test_05_invalid_json_payload(self):
        resp = self.client.post("/api/chat", data="not json", content_type="text/plain")
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertFalse(data["success"])
        self.assertIn("application/json", data["error"])

    # 6. Excessively long message
    def test_06_excessively_long_message(self):
        long_msg = "A" * 1005
        resp = self.client.post("/api/chat", json={"message": long_msg})
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertFalse(data["success"])
        self.assertIn("1000 characters", data["error"])

    # 7. New session creation when session_id omitted
    @patch("app.generate_rag_response")
    def test_07_new_session_creation(self, mock_rag):
        mock_rag.return_value = {"success": True, "answer": "Answer", "sources": [], "model": "gemini", "fallback_used": False}
        resp = self.client.post("/api/chat", json={"message": "First query"})
        self.assertEqual(resp.status_code, 200)
        sid = resp.get_json()["session_id"]
        self.assertIsNotNone(sid)
        self.assertTrue(len(sid) > 10)

    # 8. Existing session reuse
    @patch("app.generate_rag_response")
    def test_08_existing_session_reuse(self, mock_rag):
        mock_rag.return_value = {"success": True, "answer": "Reply", "sources": [], "model": "gemini", "fallback_used": False}

        # First request
        r1 = self.client.post("/api/chat", json={"message": "Question 1"})
        sid = r1.get_json()["session_id"]

        # Second request with same session_id
        r2 = self.client.post("/api/chat", json={"message": "Question 2", "session_id": sid})
        self.assertEqual(r2.get_json()["session_id"], sid)

        # Check history has both turns (2 user + 2 assistant = 4 messages)
        h_resp = self.client.get(f"/api/chat/{sid}")
        self.assertEqual(h_resp.status_code, 200)
        self.assertEqual(h_resp.get_json()["message_count"], 4)

    # 9. Unknown session ID creates session gracefully
    @patch("app.generate_rag_response")
    def test_09_unknown_session_id_handled(self, mock_rag):
        mock_rag.return_value = {"success": True, "answer": "Answer", "sources": [], "model": "gemini", "fallback_used": False}
        custom_sid = "custom-new-session-xyz"
        resp = self.client.post("/api/chat", json={"message": "Hello", "session_id": custom_sid})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["session_id"], custom_sid)

    # 10. User message persistence verified
    @patch("app.generate_rag_response")
    def test_10_user_message_persistence(self, mock_rag):
        mock_rag.return_value = {"success": True, "answer": "Answer", "sources": [], "model": "gemini", "fallback_used": False}
        r = self.client.post("/api/chat", json={"message": "Verify user persist"})
        sid = r.get_json()["session_id"]

        hist = self.client.get(f"/api/chat/{sid}").get_json()["messages"]
        self.assertEqual(hist[0]["role"], "user")
        self.assertEqual(hist[0]["content"], "Verify user persist")

    # 11. Assistant message persistence verified
    @patch("app.generate_rag_response")
    def test_11_assistant_message_persistence(self, mock_rag):
        mock_rag.return_value = {"success": True, "answer": "Verify assistant persist", "sources": [], "model": "gemini", "fallback_used": False}
        r = self.client.post("/api/chat", json={"message": "Test question"})
        sid = r.get_json()["session_id"]

        hist = self.client.get(f"/api/chat/{sid}").get_json()["messages"]
        self.assertEqual(hist[1]["role"], "assistant")
        self.assertEqual(hist[1]["content"], "Verify assistant persist")

    # 12. Sources returned correctly
    @patch("app.generate_rag_response")
    def test_12_sources_returned_correctly(self, mock_rag):
        expected_sources = [{"title": "India Code", "url": "https://www.indiacode.nic.in/", "type": "Official Legislation"}]
        mock_rag.return_value = {"success": True, "answer": "Answer with sources", "sources": expected_sources, "model": "gemini", "fallback_used": False}

        r = self.client.post("/api/chat", json={"message": "Sources question"})
        sources = r.get_json()["sources"]
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["url"], "https://www.indiacode.nic.in/")

    # 13. Conversation history retrieval
    @patch("app.generate_rag_response")
    def test_13_conversation_history_retrieval(self, mock_rag):
        mock_rag.return_value = {"success": True, "answer": "Ans", "sources": [], "model": "m", "fallback_used": False}
        r = self.client.post("/api/chat", json={"message": "History question"})
        sid = r.get_json()["session_id"]

        hist_resp = self.client.get(f"/api/chat/{sid}")
        self.assertEqual(hist_resp.status_code, 200)
        data = hist_resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["session_id"], sid)
        self.assertEqual(len(data["messages"]), 2)

    # 14. Unknown history session returns 404
    def test_14_unknown_history_session(self):
        resp = self.client.get("/api/chat/non-existent-session-12345")
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(resp.get_json()["success"])

    # 15. Conversation listing
    @patch("app.generate_rag_response")
    def test_15_conversation_listing(self, mock_rag):
        mock_rag.return_value = {"success": True, "answer": "Ans", "sources": [], "model": "m", "fallback_used": False}
        self.client.post("/api/chat", json={"message": "Topic 1"})
        self.client.post("/api/chat", json={"message": "Topic 2"})

        resp = self.client.get("/api/conversations")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(data["count"], 2)

    # 16. Pagination validation
    def test_16_pagination_validation(self):
        # Invalid integer
        bad_resp = self.client.get("/api/conversations?limit=abc&offset=xyz")
        self.assertEqual(bad_resp.status_code, 400)

        # Clamped limits
        valid_resp = self.client.get("/api/conversations?limit=200&offset=0")
        self.assertEqual(valid_resp.status_code, 200)
        self.assertEqual(valid_resp.get_json()["limit"], 100)  # Clamped to 100

    # 17. Conversation deletion
    @patch("app.generate_rag_response")
    def test_17_conversation_deletion(self, mock_rag):
        mock_rag.return_value = {"success": True, "answer": "Ans", "sources": [], "model": "m", "fallback_used": False}
        r = self.client.post("/api/chat", json={"message": "Delete me"})
        sid = r.get_json()["session_id"]

        del_resp = self.client.delete(f"/api/chat/{sid}")
        self.assertEqual(del_resp.status_code, 200)
        self.assertTrue(del_resp.get_json()["success"])

        # History should now be 404
        self.assertEqual(self.client.get(f"/api/chat/{sid}").status_code, 404)

    # 18. Unknown deletion session returns 404
    def test_18_unknown_deletion_session(self):
        resp = self.client.delete("/api/chat/phantom-session-id")
        self.assertEqual(resp.status_code, 404)

    # 19. Rename conversation
    @patch("app.generate_rag_response")
    def test_19_rename_conversation(self, mock_rag):
        mock_rag.return_value = {"success": True, "answer": "Ans", "sources": [], "model": "m", "fallback_used": False}
        r = self.client.post("/api/chat", json={"message": "Initial text"})
        sid = r.get_json()["session_id"]

        patch_resp = self.client.patch(f"/api/chat/{sid}", json={"title": "Custom Legal Discussion"})
        self.assertEqual(patch_resp.status_code, 200)
        self.assertEqual(patch_resp.get_json()["title"], "Custom Legal Discussion")

        # Verify from GET
        conv_info = self.client.get(f"/api/chat/{sid}").get_json()
        self.assertEqual(conv_info["title"], "Custom Legal Discussion")

    # 20. Invalid title on rename
    def test_20_invalid_title_rename(self):
        # Empty title
        r1 = self.client.patch("/api/chat/some-id", json={"title": ""})
        self.assertEqual(r1.status_code, 400)

        # Title too long
        r2 = self.client.patch("/api/chat/some-id", json={"title": "A" * 250})
        self.assertEqual(r2.status_code, 400)

    # 21. RAG exception handling (does not expose traceback)
    @patch("app.generate_rag_response")
    def test_21_rag_exception_handling(self, mock_rag):
        mock_rag.side_effect = RuntimeError("Fatal AI internal error")
        resp = self.client.post("/api/chat", json={"message": "Crashing question"})
        self.assertEqual(resp.status_code, 500)
        data = resp.get_json()
        self.assertFalse(data["success"])
        self.assertIn("internal error occurred", data["error"])
        # Ensure raw traceback string is NOT leaked
        self.assertNotIn("Fatal AI internal error", data["error"])

    # 22. RAG offline fallback handled gracefully
    @patch("app.generate_rag_response")
    def test_22_rag_offline_fallback(self, mock_rag):
        mock_rag.return_value = {
            "success": False,
            "answer": "Verified local statutory provision fallback.",
            "sources": [{"title": "India Code", "url": "https://www.indiacode.nic.in/"}],
            "model": "gemini-2.5-flash",
            "fallback_used": True,
            "error": "Quota limit reached",
        }
        resp = self.client.post("/api/chat", json={"message": "Fallback question"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["metadata"]["fallback_used"])
        self.assertIn("fallback", data["answer"].lower())

    # 23. Session isolation
    @patch("app.generate_rag_response")
    def test_23_session_isolation(self, mock_rag):
        mock_rag.return_value = {"success": True, "answer": "Answer", "sources": [], "model": "m", "fallback_used": False}

        r1 = self.client.post("/api/chat", json={"message": "User A Question"})
        s1 = r1.get_json()["session_id"]

        r2 = self.client.post("/api/chat", json={"message": "User B Question"})
        s2 = r2.get_json()["session_id"]

        h1 = self.client.get(f"/api/chat/{s1}").get_json()["messages"]
        h2 = self.client.get(f"/api/chat/{s2}").get_json()["messages"]

        self.assertNotEqual(s1, s2)
        self.assertEqual(h1[0]["content"], "User A Question")
        self.assertEqual(h2[0]["content"], "User B Question")

    # 24. CORS headers
    def test_24_cors_headers(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Access-Control-Allow-Origin", resp.headers)

    # 25. Database failure handling
    @patch("app.save_message")
    def test_25_database_failure_handling(self, mock_save):
        mock_save.side_effect = Exception("Disk write error")
        resp = self.client.post("/api/chat", json={"message": "DB error test"})
        self.assertEqual(resp.status_code, 500)
        data = resp.get_json()
        self.assertFalse(data["success"])
        self.assertIn("internal error occurred", data["error"])

    # 26. Error response consistency
    def test_26_error_response_consistency(self):
        # 404 test
        r_404 = self.client.get("/api/non-existent-route")
        self.assertEqual(r_404.status_code, 404)
        data = r_404.get_json()
        self.assertIn("success", data)
        self.assertFalse(data["success"])
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
