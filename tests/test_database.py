"""
Unit Tests for Database Persistence Layer (models/database.py).
File: tests/test_database.py

Uses an in-memory SQLite database (sqlite:///:memory:) for fast, isolated execution.
Covers all 18 required test cases:
1. Database initialization
2. Conversation creation
3. Unique session IDs
4. User message persistence
5. Assistant message persistence
6. Message chronology
7. Conversation history retrieval
8. Sources persistence
9. Metadata persistence
10. Conversation listing
11. Message count
12. Conversation deletion
13. Cascading message deletion
14. Conversation title update
15. Missing conversation
16. Transaction rollback on failure
17. UTC timestamp behavior
18. Multiple conversation isolation
"""

import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from models.database import (
    Conversation,
    Message,
    create_conversation,
    delete_conversation,
    get_all_conversations,
    get_conversation,
    get_conversation_history,
    init_db,
    save_message,
    transaction_scope,
    update_conversation_title,
)


class TestDatabase(unittest.TestCase):
    """Test suite covering database entities, CRUD functions, and transactional integrity."""

    def setUp(self):
        """Initialize a fresh in-memory database for each test."""
        init_db("sqlite:///:memory:")

    # 1. Database initialization
    def test_01_db_initialization(self):
        with transaction_scope() as session:
            count = session.query(Conversation).count()
            self.assertEqual(count, 0)

    # 2. Conversation creation
    def test_02_conversation_creation(self):
        conv = create_conversation(title="Test Inquiry")
        self.assertIsNotNone(conv["id"])
        self.assertIsNotNone(conv["session_id"])
        self.assertEqual(conv["title"], "Test Inquiry")
        self.assertTrue(conv["is_active"])

    # 3. Unique session IDs
    def test_03_unique_session_ids(self):
        c1 = create_conversation()
        c2 = create_conversation()
        self.assertNotEqual(c1["session_id"], c2["session_id"])

        # Attempt to create duplicate session_id returns existing conversation
        c1_dup = create_conversation(session_id=c1["session_id"])
        self.assertEqual(c1["id"], c1_dup["id"])

    # 4. User message persistence
    def test_04_user_message_persistence(self):
        conv = create_conversation()
        sid = conv["session_id"]
        msg = save_message(sid, role="user", content="What are my rights?")
        self.assertIsNotNone(msg["id"])
        self.assertEqual(msg["role"], "user")
        self.assertEqual(msg["content"], "What are my rights?")

    # 5. Assistant message persistence
    def test_05_assistant_message_persistence(self):
        conv = create_conversation()
        sid = conv["session_id"]
        msg = save_message(sid, role="assistant", content="You have fundamental rights under Part III.")
        self.assertIsNotNone(msg["id"])
        self.assertEqual(msg["role"], "assistant")
        self.assertIn("Part III", msg["content"])

    # 6. Message chronology
    def test_06_message_chronology(self):
        conv = create_conversation()
        sid = conv["session_id"]
        save_message(sid, role="user", content="Question 1")
        save_message(sid, role="assistant", content="Answer 1")
        save_message(sid, role="user", content="Question 2")
        save_message(sid, role="assistant", content="Answer 2")

        history = get_conversation_history(sid)
        self.assertEqual(len(history), 4)
        self.assertEqual(history[0]["content"], "Question 1")
        self.assertEqual(history[1]["content"], "Answer 1")
        self.assertEqual(history[2]["content"], "Question 2")
        self.assertEqual(history[3]["content"], "Answer 2")

    # 7. Conversation history retrieval
    def test_07_conversation_history_retrieval(self):
        conv = create_conversation()
        sid = conv["session_id"]
        save_message(sid, role="user", content="Hello")
        save_message(sid, role="assistant", content="Hi")

        history = get_conversation_history(sid, limit=1)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["content"], "Hello")

    # 8. Sources persistence
    def test_08_sources_persistence(self):
        conv = create_conversation()
        sid = conv["session_id"]
        sample_sources = [
            {"title": "Constitution of India", "type": "Official Legislation", "url": "https://www.indiacode.nic.in/"}
        ]
        msg = save_message(sid, role="assistant", content="Right to equality", sources=sample_sources)
        self.assertEqual(len(msg["sources"]), 1)
        self.assertEqual(msg["sources"][0]["url"], "https://www.indiacode.nic.in/")

        # Verify from retrieval
        history = get_conversation_history(sid)
        self.assertEqual(history[0]["sources"][0]["title"], "Constitution of India")

    # 9. Metadata persistence
    def test_09_metadata_persistence(self):
        conv = create_conversation()
        sid = conv["session_id"]
        meta = {"model": "gemini-2.5-flash", "fallback_used": False}
        msg = save_message(sid, role="assistant", content="Verified answer", metadata=meta)
        self.assertEqual(msg["metadata"]["model"], "gemini-2.5-flash")
        self.assertFalse(msg["metadata"]["fallback_used"])

    # 10. Conversation listing
    def test_10_conversation_listing(self):
        c1 = create_conversation(title="Chat 1")
        c2 = create_conversation(title="Chat 2")
        convs = get_all_conversations(limit=10)
        self.assertGreaterEqual(len(convs), 2)
        titles = [c["title"] for c in convs]
        self.assertIn("Chat 1", titles)
        self.assertIn("Chat 2", titles)

    # 11. Message count accurately reported
    def test_11_message_count(self):
        conv = create_conversation()
        sid = conv["session_id"]
        save_message(sid, role="user", content="Q1")
        save_message(sid, role="assistant", content="A1")
        save_message(sid, role="user", content="Q2")

        fetched = get_conversation(sid, include_messages=False)
        self.assertEqual(fetched["message_count"], 3)

    # 12. Conversation deletion
    def test_12_conversation_deletion(self):
        conv = create_conversation()
        sid = conv["session_id"]
        self.assertTrue(delete_conversation(sid))
        self.assertIsNone(get_conversation(sid))
        # Deleting non-existent returns False
        self.assertFalse(delete_conversation("non-existent-sid"))

    # 13. Cascading message deletion
    def test_13_cascading_message_deletion(self):
        conv = create_conversation()
        sid = conv["session_id"]
        save_message(sid, role="user", content="Q1")
        save_message(sid, role="assistant", content="A1")

        # Confirm messages exist
        self.assertEqual(len(get_conversation_history(sid)), 2)

        # Delete conversation
        delete_conversation(sid)

        # Confirm messages are purged from table
        with transaction_scope() as session:
            msg_count = session.query(Message).filter_by(conversation_id=conv["id"]).count()
            self.assertEqual(msg_count, 0)

    # 14. Conversation title update
    def test_14_conversation_title_update(self):
        conv = create_conversation(title="Initial Title")
        sid = conv["session_id"]
        self.assertTrue(update_conversation_title(sid, "Renamed Legal Discussion"))
        updated = get_conversation(sid)
        self.assertEqual(updated["title"], "Renamed Legal Discussion")

    # 15. Missing conversation handling
    def test_15_missing_conversation(self):
        self.assertIsNone(get_conversation("unknown-id-xyz"))
        self.assertEqual(get_conversation_history("unknown-id-xyz"), [])
        self.assertFalse(update_conversation_title("unknown-id-xyz", "Title"))

    # 16. Transaction rollback on failure
    def test_16_transaction_rollback(self):
        conv = create_conversation()
        sid = conv["session_id"]

        try:
            with transaction_scope() as session:
                msg = Message(conversation_id=conv["id"], role="user", content="Test rollback")
                session.add(msg)
                # Force an integrity error
                raise RuntimeError("Simulated failure before commit")
        except RuntimeError:
            pass

        # Verify message was not saved
        history = get_conversation_history(sid)
        self.assertEqual(len(history), 0)

    # 17. UTC timestamp behavior
    def test_17_utc_timestamp_behavior(self):
        conv = create_conversation()
        created_at = datetime.fromisoformat(conv["created_at"])
        # Should be near current UTC time
        diff = abs((datetime.now(timezone.utc) - created_at).total_seconds())
        self.assertLess(diff, 5)

    # 18. Multiple conversation isolation
    def test_18_multiple_conversation_isolation(self):
        c1 = create_conversation()
        c2 = create_conversation()

        save_message(c1["session_id"], role="user", content="Msg for C1")
        save_message(c2["session_id"], role="user", content="Msg for C2")

        h1 = get_conversation_history(c1["session_id"])
        h2 = get_conversation_history(c2["session_id"])

        self.assertEqual(len(h1), 1)
        self.assertEqual(len(h2), 1)
        self.assertEqual(h1[0]["content"], "Msg for C1")
        self.assertEqual(h2[0]["content"], "Msg for C2")


if __name__ == "__main__":
    unittest.main()
