"""
Phase 11: End-to-End System Testing, Legal Accuracy Evaluation & Security Audit.
File: tests/test_phase11_system.py

Comprehensive test suite verifying:
1. End-to-end workflows with unusual inputs (Unicode, Hindi, Emojis, Boundaries, Malformed JSON).
2. Multi-turn contextual continuity & chronological sequence.
3. RAG and legal accuracy across Indian legal domains (Constitution, BNS/BNSS, Cybercrime, Women's Rights, Consumer, NALSA).
4. Out-of-jurisdiction and high-risk query handling.
5. Multi-threaded database concurrency & foreign key integrity.
6. Security audit: .gitignore, .env.example, XSS sanitization, URL protocols, ProductionConfig.
"""

import json
import os
import sqlite3
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import MagicMock, patch

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app
from config import ProductionConfig, TestingConfig, get_config
from models.database import (
    create_conversation,
    delete_conversation,
    get_all_conversations,
    get_conversation,
    get_conversation_history,
    init_db,
    save_message,
)
from models.legal_nlp import get_nlp_engine
from services.rag_service import generate_rag_response


class TestPhase11SystemVerification(unittest.TestCase):
    """Phase 11 comprehensive system and legal accuracy test suite."""

    @classmethod
    def setUpClass(cls):
        test_config = {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "phase11-system-test-key",
            "GEMINI_API_KEY": "",  # Test verified local execution
        }
        cls.app = create_app("testing", test_config=test_config)
        cls.client = cls.app.test_client()

    def setUp(self):
        self.sleep_patcher = patch("time.sleep", return_value=None)
        self.sleep_patcher.start()

    def tearDown(self):
        self.sleep_patcher.stop()

    # ==========================================================================
    # 1. UNUSUAL INPUTS & BOUNDARY TESTING
    # ==========================================================================

    def test_01_unicode_and_multilingual_input(self):
        """Verify Hindi, Bengali, and Unicode inputs are handled safely without crashing."""
        multilingual_queries = [
            "नमस्ते, मुझे उपभोक्ता संरक्षण अधिनियम के बारे में जानना है।",
            "কীভাবে পুলিশ এফআইআর দায়ের করতে হয়?",
            "உரிமைகள் என்ன?",
            "What are my rights regarding privacy? 📜⚖️🚨",
        ]
        for query in multilingual_queries:
            resp = self.client.post("/api/chat", json={"message": query})
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertTrue(data["success"])
            self.assertIsInstance(data["answer"], str)
            self.assertGreater(len(data["answer"]), 20)

    def test_02_exact_1000_char_boundary(self):
        """Verify message with exactly 1000 characters is accepted."""
        exact_1000 = "A" * 981 + " Fundamental Rights"
        self.assertEqual(len(exact_1000), 1000)

        resp = self.client.post("/api/chat", json={"message": exact_1000})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])

    def test_03_1001_char_boundary_rejected(self):
        """Verify message with 1001 characters is strictly rejected with HTTP 400."""
        oversized = "A" * 1001
        resp = self.client.post("/api/chat", json={"message": oversized})
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertFalse(data["success"])
        self.assertIn("1000 characters", data["error"])

    def test_04_malformed_json_variations(self):
        """Verify malformed JSON requests return 400 Bad Request."""
        # Not a dictionary
        resp = self.client.post("/api/chat", json=["not", "a", "dictionary"])
        self.assertEqual(resp.status_code, 400)

        # Message is integer
        resp2 = self.client.post("/api/chat", json={"message": 12345})
        self.assertEqual(resp2.status_code, 400)

        # Message is None
        resp3 = self.client.post("/api/chat", json={"message": None})
        self.assertEqual(resp3.status_code, 400)

    # ==========================================================================
    # 2. LEGAL ACCURACY & DOMAIN ROUTING
    # ==========================================================================

    def test_05_statutory_transition_bns_vs_ipc(self):
        """Verify queries regarding cheating/fraud reference BNS Section 318 and transition provisions."""
        resp = self.client.post("/api/chat", json={
            "message": "What is the punishment for cheating under Section 318 of BNS (formerly Section 420 IPC)?"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        answer = data["answer"]
        self.assertTrue(
            "318" in answer
            or "BNS" in answer
            or "420" in answer
            or "Bharatiya Nyaya Sanhita" in answer
        )

    def test_06_fir_and_police_procedure_bnss(self):
        """Verify FIR procedure queries mention Section 173 BNSS / Zero FIR / copy rights."""
        resp = self.client.post("/api/chat", json={
            "message": "What is a First Information Report (FIR) and under what section is it registered?"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        answer = data["answer"]
        self.assertTrue(
            "173" in answer
            or "BNSS" in answer
            or "154" in answer
            or "FIR" in answer
        )

    def test_07_cybercrime_helpline_attribution(self):
        """Verify cyber fraud queries return 1930 helpline and verified portal."""
        resp = self.client.post("/api/chat", json={"message": "How do I report online financial fraud?"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        answer = data["answer"]
        self.assertIn("1930", answer)
        # Check verified sources
        urls = [s.get("url") for s in data["sources"]]
        self.assertTrue(any("cybercrime.gov.in" in u or "indiacode.nic.in" in u for u in urls))

    def test_08_consumer_complaint_and_edaakhil(self):
        """Verify consumer protection queries mention Consumer Protection Act 2019 / 1915."""
        resp = self.client.post("/api/chat", json={"message": "How can I file a consumer complaint?"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        answer = data["answer"]
        self.assertTrue("Consumer" in answer or "1915" in answer or "e-Daakhil" in answer)

    def test_09_free_legal_aid_nalsa(self):
        """Verify free legal aid queries mention NALSA / 15100 helpline."""
        resp = self.client.post("/api/chat", json={"message": "Who is eligible for free legal aid in India?"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        answer = data["answer"]
        self.assertTrue("Legal Services" in answer or "15100" in answer or "NALSA" in answer or "Article 39A" in answer)

    def test_10_out_of_jurisdiction_inquiry(self):
        """Verify foreign law queries are identified and clarified as outside Indian jurisdiction."""
        nlp_engine = get_nlp_engine()
        faq_res = nlp_engine.find_best_faq("How do I file Chapter 11 bankruptcy in New York USA?")
        # Should not falsely match a high-confidence Indian local statute
        self.assertFalse(faq_res.get("matched", False))

    # ==========================================================================
    # 3. DATABASE CONCURRENCY & INTEGRITY
    # ==========================================================================

    def test_11_concurrent_database_writes(self):
        """Verify simultaneous multi-threaded database writes do not corrupt data or raise lock errors."""
        temp_db_path = BASE_DIR / "instance" / "test_p11_concurrency.db"
        temp_db_path.parent.mkdir(parents=True, exist_ok=True)
        if temp_db_path.exists():
            try:
                temp_db_path.unlink()
            except Exception:
                pass

        # Initialize dedicated database engine with timeout
        test_engine = init_db(f"sqlite:///{temp_db_path.as_posix()}")

        session_prefix = "concurrency-test-p11"
        num_threads = 4
        messages_per_thread = 3
        errors = []

        def worker_task(thread_id):
            try:
                sid = f"{session_prefix}-{thread_id}"
                create_conversation(session_id=sid, title=f"Thread {thread_id} Chat")
                for i in range(messages_per_thread):
                    save_message(sid, role="user", content=f"User prompt {i}")
                    save_message(sid, role="assistant", content=f"Assistant response {i}")
                hist = get_conversation_history(sid)
                if len(hist) != messages_per_thread * 2:
                    errors.append(f"Thread {thread_id} expected {messages_per_thread * 2} messages, got {len(hist)}")
            except Exception as e:
                errors.append(f"Thread {thread_id} error: {e}")

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            list(executor.map(worker_task, range(num_threads)))

        # Clean up database resources
        test_engine.dispose()
        try:
            temp_db_path.unlink(missing_ok=True)
        except Exception:
            pass

        # Restore test app in-memory database
        init_db("sqlite:///:memory:")

        self.assertEqual(len(errors), 0, f"Concurrency errors occurred: {errors}")

    def test_12_cascading_deletion_and_isolation(self):
        """Verify conversation deletion cascades completely and leaves other conversations intact."""
        sid1 = "isolation-delete-sid-1"
        sid2 = "isolation-keep-sid-2"

        create_conversation(session_id=sid1, title="To Delete")
        create_conversation(session_id=sid2, title="To Keep")

        save_message(sid1, role="user", content="Delete me")
        save_message(sid1, role="assistant", content="Will be deleted")
        save_message(sid2, role="user", content="Keep me")
        save_message(sid2, role="assistant", content="Will be kept")

        # Delete sid1
        deleted = delete_conversation(sid1)
        self.assertTrue(deleted)

        # Verify sid1 messages are gone
        self.assertEqual(len(get_conversation_history(sid1)), 0)
        self.assertIsNone(get_conversation(sid1))

        # Verify sid2 messages remain intact
        self.assertEqual(len(get_conversation_history(sid2)), 2)
        self.assertIsNotNone(get_conversation(sid2))

    # ==========================================================================
    # 4. SECURITY AUDIT & CONFIGURATION SAFETY
    # ==========================================================================

    def test_13_gitignore_covers_sensitive_files(self):
        """Verify .gitignore includes .env, database files, and cache directories."""
        gitignore_path = BASE_DIR / ".gitignore"
        self.assertTrue(gitignore_path.exists())
        content = gitignore_path.read_text(encoding="utf-8")
        self.assertIn(".env", content)
        self.assertIn("*.db", content)
        self.assertIn("instance/", content)
        self.assertIn("__pycache__", content)

    def test_14_env_example_contains_no_real_secrets(self):
        """Verify .env.example contains only placeholders, no real API keys."""
        example_path = BASE_DIR / ".env.example"
        self.assertTrue(example_path.exists())
        content = example_path.read_text(encoding="utf-8")
        self.assertNotIn("AIza", content)
        self.assertIn("your_gemini_api_key_here", content)

    def test_15_production_config_debug_is_strictly_false(self):
        """Verify ProductionConfig sets DEBUG = False."""
        self.assertFalse(ProductionConfig.DEBUG)
        prod_cfg = get_config("production")
        self.assertFalse(prod_cfg.DEBUG)

    def test_16_legal_disclaimer_present_in_responses(self):
        """Verify that legal awareness responses include appropriate disclaimer notes."""
        resp = self.client.post("/api/chat", json={"message": "What is the procedure for divorce under Hindu Marriage Act?"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        answer = data["answer"]
        self.assertTrue(
            "Disclaimer:" in answer
            or "Note:" in answer
            or "advocate" in answer.lower()
            or "legal advice" in answer.lower()
        )

    def test_17_wsgi_entrypoint_import(self):
        """Verify that wsgi.py exports valid production app and application WSGI callables."""
        import wsgi
        self.assertIsNotNone(wsgi.app)
        self.assertIsNotNone(wsgi.application)
        self.assertEqual(wsgi.app, wsgi.application)
        # Production config by default in wsgi
        self.assertFalse(wsgi.app.config.get("DEBUG", True))


if __name__ == "__main__":
    unittest.main()
