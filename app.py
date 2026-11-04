"""
LegalEase - Flask Web Application & REST API Service.
File: app.py

Implements the application factory pattern, Flask-CORS configuration,
SQLite persistence initialization, and REST endpoints for:
- GET  /api/health            (Service health verification)
- POST /api/chat              (Chat message processing via Hybrid RAG)
- GET  /api/chat/<session_id> (Retrieve message history for session)
- GET  /api/conversations     (List recent conversations with pagination)
- DELETE /api/chat/<session_id> (Cascade delete conversation)
- PATCH  /api/chat/<session_id> (Rename conversation title)
- GET  /                      (Serve chatbot UI or welcome status)
"""

import logging
import os
import secrets
from pathlib import Path
from typing import Any, Dict, Optional

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from config import Config, get_config
from models.database import (
    create_conversation,
    delete_conversation,
    get_all_conversations,
    get_conversation,
    get_conversation_history,
    init_db,
    save_message,
    update_conversation_title,
)
from services.rag_service import generate_rag_response

BASE_DIR = Path(__file__).resolve().parent

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("legalease.app")


def create_app(config_name: Optional[str] = None, test_config: Optional[Dict[str, Any]] = None) -> Flask:
    """
    Application factory pattern for LegalEase.
    Accepts config_name ('development', 'testing', 'production') and optional test_config overrides.
    """
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    # 1. Load Configuration
    cfg_class = get_config(config_name)
    app.config.from_object(cfg_class)

    if test_config:
        app.config.update(test_config)

    # 2. CORS Configuration
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=False,
    )

    # 3. Initialize Database
    db_url = app.config.get("SQLALCHEMY_DATABASE_URI")
    init_db(db_url)

    # ==============================================================================
    # ROUTE DEFINITIONS
    # ==============================================================================

    @app.route("/", methods=["GET"])
    def index():
        """Serve the frontend chatbot UI if available, or return status."""
        template_file = Path(app.template_folder) / "index.html"
        if template_file.exists():
            return render_template("index.html")
        return jsonify({
            "service": "LegalEase",
            "version": Config.APP_VERSION,
            "status": "online",
            "message": "Welcome to LegalEase - AI-Powered Indian Legal Awareness Chatbot API."
        }), 200

    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Endpoint 1: Health Check."""
        return jsonify({
            "success": True,
            "status": "healthy",
            "service": "LegalEase",
            "version": Config.APP_VERSION
        }), 200

    @app.route("/api/chat", methods=["POST"])
    def chat_endpoint():
        """
        Endpoint 2: Send Chat Message.
        Receives user prompt, coordinates RAG retrieval, saves messages, and returns answer.
        """
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Request payload must be formatted as application/json.",
                "status_code": 400
            }), 400

        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({
                "success": False,
                "error": "Request payload must be a JSON object.",
                "status_code": 400
            }), 400

        raw_message = data.get("message")
        session_id = data.get("session_id")

        # Validate message
        if raw_message is None or not isinstance(raw_message, str):
            return jsonify({
                "success": False,
                "error": "Field 'message' is required and must be a string.",
                "status_code": 400
            }), 400

        clean_message = raw_message.strip()
        if not clean_message:
            return jsonify({
                "success": False,
                "error": "Message cannot be empty or whitespace only.",
                "status_code": 400
            }), 400

        if len(clean_message) > 1000:
            return jsonify({
                "success": False,
                "error": "Message exceeds the maximum limit of 1000 characters.",
                "status_code": 400
            }), 400

        # Validate or create session_id
        if not session_id or not isinstance(session_id, str) or not session_id.strip():
            session_id = secrets.token_urlsafe(16)
            create_conversation(session_id=session_id)
        else:
            session_id = session_id.strip()
            # Ensure conversation exists
            existing_conv = get_conversation(session_id, include_messages=False)
            if not existing_conv:
                create_conversation(session_id=session_id)

        try:
            # 1. Save user message to database
            save_message(session_id, role="user", content=clean_message)

            # 2. Retrieve recent conversation history for RAG context (up to 6 preceding turns)
            raw_history = get_conversation_history(session_id, limit=50)
            formatted_history = [
                {"role": m.get("role", "user"), "content": m.get("content", "")}
                for m in raw_history[:-1][-6:]  # Exclude current message, take up to 6 most recent preceding turns
            ]

            # 3. Call Hybrid RAG Pipeline (Phase 7)
            rag_output = generate_rag_response(clean_message, conversation_history=formatted_history)

            answer = rag_output.get("answer", "No response could be generated.")
            sources = rag_output.get("sources", [])
            model_used = rag_output.get("model", Config.GEMINI_MODEL)
            fallback_used = rag_output.get("fallback_used", False)

            # 4. Save assistant response and sources to database
            metadata = {
                "model": model_used,
                "fallback_used": fallback_used,
                "retrieval": rag_output.get("retrieval", {})
            }
            save_message(
                session_id,
                role="assistant",
                content=answer,
                sources=sources,
                metadata=metadata
            )

            # 5. Return standardized API response
            return jsonify({
                "success": True,
                "session_id": session_id,
                "answer": answer,
                "sources": sources,
                "metadata": {
                    "model": model_used,
                    "fallback_used": fallback_used
                }
            }), 200

        except Exception as e:
            logger.error(f"Error processing chat message: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "error": "An internal error occurred while processing your legal awareness question. Please try again.",
                "status_code": 500
            }), 500

    @app.route("/api/chat/<session_id>", methods=["GET"])
    def get_chat_history(session_id: str):
        """Endpoint 3: Retrieve Conversation History."""
        if not session_id or not session_id.strip():
            return jsonify({"success": False, "error": "Invalid session ID.", "status_code": 400}), 400

        conv = get_conversation(session_id.strip(), include_messages=True)
        if not conv:
            return jsonify({
                "success": False,
                "error": f"No conversation found for session ID '{session_id}'.",
                "status_code": 404
            }), 404

        return jsonify({
            "success": True,
            "session_id": conv["session_id"],
            "title": conv["title"],
            "created_at": conv["created_at"],
            "updated_at": conv["updated_at"],
            "message_count": conv["message_count"],
            "messages": conv.get("messages", [])
        }), 200

    @app.route("/api/conversations", methods=["GET"])
    def list_conversations():
        """Endpoint 4: List Recent Conversations with pagination."""
        try:
            limit = int(request.args.get("limit", 20))
            offset = int(request.args.get("offset", 0))
        except ValueError:
            return jsonify({
                "success": False,
                "error": "Query parameters 'limit' and 'offset' must be valid integers.",
                "status_code": 400
            }), 400

        # Enforce bounds
        limit = min(max(1, limit), 100)
        offset = max(0, offset)

        conversations = get_all_conversations(limit=limit, offset=offset)
        return jsonify({
            "success": True,
            "count": len(conversations),
            "limit": limit,
            "offset": offset,
            "conversations": conversations
        }), 200

    @app.route("/api/chat/<session_id>", methods=["DELETE"])
    def delete_chat_session(session_id: str):
        """Endpoint 5: Delete Conversation & Messages (Cascade)."""
        if not session_id or not session_id.strip():
            return jsonify({"success": False, "error": "Invalid session ID.", "status_code": 400}), 400

        deleted = delete_conversation(session_id.strip())
        if not deleted:
            return jsonify({
                "success": False,
                "error": f"No conversation found to delete for session ID '{session_id}'.",
                "status_code": 404
            }), 404

        return jsonify({
            "success": True,
            "message": f"Conversation session '{session_id}' and all associated messages successfully deleted."
        }), 200

    @app.route("/api/chat/<session_id>", methods=["PATCH"])
    def rename_chat_session(session_id: str):
        """Endpoint 6: Rename Conversation Title."""
        if not request.is_json:
            return jsonify({"success": False, "error": "Request payload must be JSON.", "status_code": 400}), 400

        data = request.get_json() or {}
        new_title = data.get("title")

        if not new_title or not isinstance(new_title, str) or not new_title.strip():
            return jsonify({
                "success": False,
                "error": "Field 'title' must be a non-empty string.",
                "status_code": 400
            }), 400

        clean_title = new_title.strip()
        if len(clean_title) > 200:
            return jsonify({
                "success": False,
                "error": "Title exceeds maximum allowed length of 200 characters.",
                "status_code": 400
            }), 400

        updated = update_conversation_title(session_id.strip(), clean_title)
        if not updated:
            return jsonify({
                "success": False,
                "error": f"No conversation found for session ID '{session_id}'.",
                "status_code": 404
            }), 404

        return jsonify({
            "success": True,
            "session_id": session_id,
            "title": clean_title,
            "message": "Conversation title updated successfully."
        }), 200

    # ==============================================================================
    # ERROR HANDLERS (Safe JSON responses without exposing stack traces)
    # ==============================================================================

    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({"success": False, "error": "Bad Request.", "status_code": 400}), 400

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"success": False, "error": "Resource Not Found.", "status_code": 404}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return jsonify({"success": False, "error": "HTTP Method Not Allowed.", "status_code": 405}), 405

    @app.errorhandler(500)
    def handle_server_error(e):
        return jsonify({"success": False, "error": "Internal Server Error.", "status_code": 500}), 500

    return app


# Application entry point for development
if __name__ == "__main__":
    app_instance = create_app()
    logger.info(f"Starting {Config.APP_NAME} server on http://{Config.HOST}:{Config.PORT}")
    app_instance.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
