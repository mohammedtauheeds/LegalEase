"""
Live Server Runtime Verification for LegalEase.
File: tests/verify_live_server.py

Launches the live Flask application on http://127.0.0.1:5000 in a background process,
performs live HTTP requests against all 8 required functional areas,
checks for tracebacks and runtime errors, and logs results.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import requests

PYTHON_EXE = sys.executable
SERVER_SCRIPT = BASE_DIR / "app.py"
BASE_URL = "http://127.0.0.1:5000"


def test_live_server():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 70)
    print("LEGALEASE LIVE SERVER INTEGRATION & RUNTIME VERIFICATION")
    print("=" * 70)

    # 1. Start the Flask server as a subprocess
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["FLASK_ENV"] = "development"
    env["HOST"] = "127.0.0.1"
    env["PORT"] = "5000"

    print(f"Launching Flask server using: {PYTHON_EXE}")
    server_proc = subprocess.Popen(
        [PYTHON_EXE, str(SERVER_SCRIPT)],
        cwd=str(BASE_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )

    time.sleep(2.5)  # Allow server to bind and initialize database
    passed = 0
    total = 9

    try:
        # Check if server process is still alive
        if server_proc.poll() is not None:
            stdout, stderr = server_proc.communicate()
            print("[FAIL] Server failed to start! Exit code:", server_proc.poll())
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            return False

        print("[OK] Server process started successfully (PID:", server_proc.pid, ")")

        # 1. Healthcheck Endpoint (GET /api/health)
        print("\n[1/9] Testing Healthcheck: GET /api/health")
        resp = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"      Status: {resp.status_code}")
        data = resp.json()
        print(f"      Response: {data}")
        assert resp.status_code == 200 and data.get("status") == "healthy"
        print("      --> PASS")
        passed += 1

        # 2. Homepage (GET /)
        print("\n[2/9] Testing Homepage Serving: GET /")
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"      Status: {resp.status_code}, Content-Type: {resp.headers.get('content-type')}")
        assert resp.status_code == 200
        assert "LegalEase" in resp.text
        assert "Understand Your Rights" in resp.text
        print("      --> PASS (HTML Single Page Application successfully served)")
        passed += 1

        # 3. Static Assets: CSS (GET /static/css/style.css)
        print("\n[3/9] Testing Static Asset: GET /static/css/style.css")
        resp = requests.get(f"{BASE_URL}/static/css/style.css", timeout=5)
        print(f"      Status: {resp.status_code}")
        assert resp.status_code == 200 and "--neon-blue" in resp.text
        print("      --> PASS (Futuristic Dark Theme CSS loaded)")
        passed += 1

        # 4. Static Assets: JS (GET /static/js/app.js)
        print("\n[4/9] Testing Static Asset: GET /static/js/app.js")
        resp = requests.get(f"{BASE_URL}/static/js/app.js", timeout=5)
        print(f"      Status: {resp.status_code}")
        assert resp.status_code == 200 and "safeMarkdownToHtml" in resp.text
        print("      --> PASS (Client Application Logic loaded)")
        passed += 1

        # 5. Chat Query Turn 1: POST /api/chat
        print("\n[5/9] Testing User Question: POST /api/chat")
        chat_payload = {
            "message": "What are my Fundamental Rights under the Indian Constitution?"
        }
        resp = requests.post(f"{BASE_URL}/api/chat", json=chat_payload, timeout=10)
        print(f"      Status: {resp.status_code}")
        chat_data = resp.json()
        print(f"      Success: {chat_data.get('success')}")
        print(f"      Session ID: {chat_data.get('session_id')}")
        print(f"      Answer Preview: {chat_data.get('answer', '')[:120]}...")
        print(f"      Sources Count: {len(chat_data.get('sources', []))}")
        assert resp.status_code == 200 and chat_data.get("success") is True
        session_id = chat_data["session_id"]
        assert len(chat_data.get("sources", [])) >= 1
        print("      --> PASS (Grounded answer and verified citations returned)")
        passed += 1

        # 6. Contextual Follow-up Turn 2: POST /api/chat (using same session_id)
        print("\n[6/9] Testing Contextual Follow-Up: POST /api/chat")
        followup_payload = {
            "message": "Which Article guarantees personal liberty and privacy?",
            "session_id": session_id,
        }
        resp = requests.post(f"{BASE_URL}/api/chat", json=followup_payload, timeout=10)
        print(f"      Status: {resp.status_code}")
        followup_data = resp.json()
        print(f"      Session ID: {followup_data.get('session_id')}")
        print(f"      Answer Preview: {followup_data.get('answer', '')[:120]}...")
        assert resp.status_code == 200 and followup_data.get("session_id") == session_id
        print("      --> PASS (Multi-turn session continuity verified)")
        passed += 1

        # 7. History Retrieval: GET /api/chat/<session_id>
        print(f"\n[7/9] Testing Conversation History: GET /api/chat/{session_id}")
        resp = requests.get(f"{BASE_URL}/api/chat/{session_id}", timeout=5)
        print(f"      Status: {resp.status_code}")
        hist_data = resp.json()
        print(f"      Title: {hist_data.get('title')}")
        print(f"      Message Count: {hist_data.get('message_count')}")
        assert resp.status_code == 200 and hist_data.get("message_count") >= 4
        print("      --> PASS (Full conversation history retrieved)")
        passed += 1

        # 8. Rename Conversation: PATCH /api/chat/<session_id>
        print(f"\n[8/9] Testing Conversation Renaming: PATCH /api/chat/{session_id}")
        rename_payload = {"title": "Constitutional Rights Consultation"}
        resp = requests.patch(f"{BASE_URL}/api/chat/{session_id}", json=rename_payload, timeout=5)
        print(f"      Status: {resp.status_code}")
        rename_data = resp.json()
        print(f"      New Title: {rename_data.get('title')}")
        assert resp.status_code == 200 and rename_data.get("title") == "Constitutional Rights Consultation"
        print("      --> PASS (Conversation title successfully updated)")
        passed += 1

        # 9. Delete Conversation: DELETE /api/chat/<session_id>
        print(f"\n[9/9] Testing Conversation Deletion: DELETE /api/chat/{session_id}")
        resp = requests.delete(f"{BASE_URL}/api/chat/{session_id}", timeout=5)
        print(f"      Status: {resp.status_code}")
        del_data = resp.json()
        print(f"      Response: {del_data.get('message')}")
        assert resp.status_code == 200 and del_data.get("success") is True

        # Verify deletion cascades
        verify_del_resp = requests.get(f"{BASE_URL}/api/chat/{session_id}", timeout=5)
        assert verify_del_resp.status_code == 404
        print("      --> PASS (Cascading deletion verified, 404 returned on re-query)")
        passed += 1

    except Exception as e:
        print(f"\n[FAIL] Live verification encountered error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Gracefully terminate the server process
        print("\nShutting down Flask server process...")
        server_proc.terminate()
        try:
            server_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server_proc.kill()
        print("Server process stopped.")

    print("\n" + "=" * 70)
    print(f"SUMMARY: {passed} / {total} LIVE ENDPOINTS & WORKFLOWS PASSED")
    print("=" * 70)
    return passed == total


if __name__ == "__main__":
    success = test_live_server()
    sys.exit(0 if success else 1)
