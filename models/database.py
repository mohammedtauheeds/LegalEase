"""
LegalEase - Database Persistence Layer & SQLAlchemy Models.
File: models/database.py

Defines persistent SQLite entities for:
- Conversation (UUID session tracking, titles, timestamps, active status)
- Message (User & Assistant exchanges, chronological order, JSON sources, metadata)
Provides robust transactional CRUD helpers, cascade deletion, and thread-safe session management.
"""

import json
import logging
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
    desc,
    func,
)
from sqlalchemy.orm import (
    declarative_base,
    relationship,
    scoped_session,
    sessionmaker,
)

from config import Config

logger = logging.getLogger("legalease.database")

Base = declarative_base()


def utc_now() -> datetime:
    """Return current timestamp in UTC timezone."""
    return datetime.now(timezone.utc)


class Conversation(Base):
    """Database model representing a chat conversation / session."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=True, default="New Legal Inquiry")
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(DateTime, nullable=False, default=utc_now, onupdate=utc_now)
    is_active = Column(Boolean, nullable=False, default=True)

    # Cascading one-to-many relationship to Message
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at.asc(), Message.id.asc()",
    )

    def to_dict(self, include_messages: bool = False) -> Dict[str, Any]:
        """Serialize conversation to dictionary."""
        data = {
            "id": self.id,
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "message_count": len(self.messages) if self.messages else 0,
        }
        if include_messages and self.messages:
            data["messages"] = [m.to_dict() for m in self.messages]
        return data


class Message(Base):
    """Database model representing an individual message turn."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=utc_now)
    sources = Column(Text, nullable=True)  # JSON-serialized list of sources
    metadata_json = Column(Text, nullable=True)  # JSON-serialized metadata dict

    conversation = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index("idx_messages_conv_created", "conversation_id", "created_at"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize message to dictionary."""
        parsed_sources = []
        if self.sources:
            try:
                parsed_sources = json.loads(self.sources)
            except Exception:
                parsed_sources = []

        parsed_metadata = {}
        if self.metadata_json:
            try:
                parsed_metadata = json.loads(self.metadata_json)
            except Exception:
                parsed_metadata = {}

        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "sources": parsed_sources,
            "metadata": parsed_metadata,
        }


# Database Engine and Session Factory State
_ENGINE = None
_SESSION_FACTORY = None


def init_db(db_url: Optional[str] = None):
    """
    Initialize SQLite database engine and create tables.
    Supports in-memory SQLite (sqlite:///:memory:) for isolated testing.
    """
    global _ENGINE, _SESSION_FACTORY

    url = db_url or Config.SQLALCHEMY_DATABASE_URI
    # SQLite connection arguments
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        connect_args["timeout"] = 30

    _ENGINE = create_engine(url, connect_args=connect_args)
    _SESSION_FACTORY = scoped_session(sessionmaker(bind=_ENGINE, autoflush=False, autocommit=False))

    Base.metadata.create_all(_ENGINE)
    logger.info(f"Database initialized with schema at: {url}")
    return _ENGINE


def get_db_session():
    """Return a thread-safe scoped SQLAlchemy session."""
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        init_db()
    return _SESSION_FACTORY()


@contextmanager
def transaction_scope():
    """Context manager for atomic transaction management with automatic rollback."""
    session = get_db_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database transaction rollback triggered: {e}")
        raise
    finally:
        session.close()


# ==============================================================================
# CRUD HELPER OPERATIONS
# ==============================================================================


def create_conversation(session_id: Optional[str] = None, title: Optional[str] = None) -> Dict[str, Any]:
    """Create a new conversation session with a unique UUID."""
    sid = session_id.strip() if session_id and session_id.strip() else str(uuid.uuid4())
    conv_title = title.strip() if title and title.strip() else "New Legal Inquiry"

    with transaction_scope() as session:
        # Check if session already exists
        existing = session.query(Conversation).filter_by(session_id=sid).first()
        if existing:
            return existing.to_dict()

        conv = Conversation(session_id=sid, title=conv_title)
        session.add(conv)
        session.flush()
        return conv.to_dict()


def get_conversation(session_id: str, include_messages: bool = True) -> Optional[Dict[str, Any]]:
    """Retrieve conversation details and messages for a session ID."""
    if not session_id or not isinstance(session_id, str):
        return None

    with transaction_scope() as session:
        conv = session.query(Conversation).filter_by(session_id=session_id.strip()).first()
        if not conv:
            return None
        return conv.to_dict(include_messages=include_messages)


def save_message(
    session_id: str,
    role: str,
    content: str,
    sources: Optional[List[Dict[str, Any]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Save a user or assistant message turn under an existing or newly created conversation.
    """
    if not session_id or not content or not role:
        return None

    clean_sid = session_id.strip()
    sources_json = json.dumps(sources) if sources is not None else None
    meta_json = json.dumps(metadata) if metadata is not None else None

    with transaction_scope() as session:
        conv = session.query(Conversation).filter_by(session_id=clean_sid).first()
        if not conv:
            # Auto-create conversation if not yet created
            conv = Conversation(session_id=clean_sid, title="New Legal Inquiry")
            session.add(conv)
            session.flush()

        msg = Message(
            conversation_id=conv.id,
            role=role,
            content=content.strip(),
            sources=sources_json,
            metadata_json=meta_json,
            created_at=utc_now(),
        )
        session.add(msg)
        conv.updated_at = utc_now()

        # If user message and title is default, update title to user prompt summary
        if role == "user" and (conv.title == "New Legal Inquiry" or not conv.title):
            summary_title = content.strip()[:60]
            if len(content.strip()) > 60:
                summary_title += "..."
            conv.title = summary_title

        session.flush()
        return msg.to_dict()


def get_conversation_history(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve chronological messages for a conversation session."""
    if not session_id:
        return []

    with transaction_scope() as session:
        conv = session.query(Conversation).filter_by(session_id=session_id.strip()).first()
        if not conv:
            return []

        messages = (
            session.query(Message)
            .filter_by(conversation_id=conv.id)
            .order_by(Message.created_at.asc(), Message.id.asc())
            .limit(limit)
            .all()
        )
        return [m.to_dict() for m in messages]


def get_all_conversations(limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """Retrieve recent conversations ordered by last update."""
    with transaction_scope() as session:
        convs = (
            session.query(Conversation)
            .filter_by(is_active=True)
            .order_by(desc(Conversation.updated_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [c.to_dict(include_messages=False) for c in convs]


def delete_conversation(session_id: str) -> bool:
    """Delete a conversation and its messages via cascade."""
    if not session_id:
        return False

    with transaction_scope() as session:
        conv = session.query(Conversation).filter_by(session_id=session_id.strip()).first()
        if not conv:
            return False
        session.delete(conv)
        return True


def update_conversation_title(session_id: str, title: str) -> bool:
    """Rename a conversation session."""
    if not session_id or not title or not title.strip():
        return False

    clean_title = title.strip()[:200]
    with transaction_scope() as session:
        conv = session.query(Conversation).filter_by(session_id=session_id.strip()).first()
        if not conv:
            return False
        conv.title = clean_title
        conv.updated_at = utc_now()
        return True
