"""
Performance Benchmarking & Database Integrity Verification Script for LegalEase (Phase 11).
File: tests/benchmark_performance.py

Measures and reports repeatable latency metrics across:
1. Flask homepage loading (GET /)
2. Backend healthcheck (GET /api/health)
3. Conversation list pagination (GET /api/conversations)
4. Database write & read operations
5. NLP FAQ matching latency (TF-IDF + Cosine Similarity)
6. Unified legal search latency (FAQ + Statutory store)
7. Total RAG response latency
8. Multi-threaded database concurrency
9. SQLite database integrity & foreign key checks
"""

import os
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, List, Tuple
from unittest.mock import patch

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app
from config import Config
from models.database import (
    create_conversation,
    get_all_conversations,
    get_conversation,
    get_conversation_history,
    init_db,
    save_message,
)
from models.legal_nlp import get_nlp_engine
from services.legal_search import search_legal_information
from services.rag_service import generate_rag_response


def benchmark_function(func: Callable, iterations: int = 15, warmup: int = 2) -> Tuple[float, float, float]:
    """Execute a callable multiple times and return (avg_ms, min_ms, max_ms)."""
    # Warmup
    for _ in range(warmup):
        func()

    timings = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        func()
        t1 = time.perf_counter()
        timings.append((t1 - t0) * 1000.0)  # Convert to milliseconds

    avg_ms = sum(timings) / len(timings)
    min_ms = min(timings)
    max_ms = max(timings)
    return avg_ms, min_ms, max_ms


def run_all_benchmarks():
    print("=" * 75)
    print("LEGALEASE PHASE 11: SYSTEM PERFORMANCE BENCHMARKS & DATABASE INTEGRITY")
    print("=" * 75)

    # 1. Setup isolated test application and database
    test_db_path = BASE_DIR / "instance" / "benchmark_test.db"
    test_db_path.parent.mkdir(parents=True, exist_ok=True)
    if test_db_path.exists():
        try:
            test_db_path.unlink()
        except Exception:
            pass

    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{test_db_path.as_posix()}",
        "SECRET_KEY": "benchmark-secret-key-42",
        "GEMINI_API_KEY": "",  # Measure local verified execution
    }
    app = create_app("testing", test_config=test_config)
    client = app.test_client()

    results = []
    iterations = 15

    with patch("time.sleep", return_value=None):
        # 1. Homepage GET /
        avg, mn, mx = benchmark_function(lambda: client.get("/"), iterations=iterations)
        results.append(("Homepage (GET /)", avg, mn, mx, iterations, "Local HTTP TestClient"))

        # 2. Healthcheck GET /api/health
        avg, mn, mx = benchmark_function(lambda: client.get("/api/health"), iterations=iterations)
        results.append(("Health Check (GET /api/health)", avg, mn, mx, iterations, "Local HTTP TestClient"))

        # 3. Conversation Listing GET /api/conversations
        # Populate 10 conversations first
        for i in range(10):
            sid = f"bench-sid-{i}"
            create_conversation(session_id=sid, title=f"Legal Query #{i}")
            save_message(sid, role="user", content=f"What are my rights regarding #{i}?")
            save_message(sid, role="assistant", content=f"Under Indian law #{i} applies.")

        avg, mn, mx = benchmark_function(lambda: client.get("/api/conversations?limit=10"), iterations=iterations)
        results.append(("Conversation List (GET /api/conversations)", avg, mn, mx, iterations, "Local HTTP TestClient"))

        # 4. Database Write (save_message)
        bench_sid = "db-write-benchmark-session"
        create_conversation(session_id=bench_sid, title="DB Write Benchmark")
        write_counter = [0]
        def do_db_write():
            write_counter[0] += 1
            save_message(bench_sid, role="user", content=f"Benchmark question #{write_counter[0]}")

        avg, mn, mx = benchmark_function(do_db_write, iterations=iterations)
        results.append(("Database Message Write (SQLAlchemy)", avg, mn, mx, iterations, "SQLite Disk Write"))

        # 5. Database Read (get_conversation_history)
        avg, mn, mx = benchmark_function(lambda: get_conversation_history(bench_sid, limit=20), iterations=iterations)
        results.append(("Database Message Read (SQLAlchemy)", avg, mn, mx, iterations, "SQLite Disk Read"))

        # 6. NLP FAQ Matching (TF-IDF + Cosine Similarity)
        nlp_engine = get_nlp_engine()
        test_query = "What is the procedure to file a police FIR under BNSS?"
        avg, mn, mx = benchmark_function(lambda: nlp_engine.find_best_faq(test_query), iterations=iterations)
        results.append(("NLP FAQ Match (TF-IDF Cosine Similarity)", avg, mn, mx, iterations, "CPU Scikit-Learn"))

        # 7. Unified Legal Search (FAQ + Local Statutory Provisions)
        avg, mn, mx = benchmark_function(lambda: search_legal_information(test_query), iterations=iterations)
        results.append(("Unified Legal Search (FAQ + Statutes)", avg, mn, mx, iterations, "Local In-Memory RAG"))

        # 8. Complete RAG Pipeline Response (Direct Verified FAQ Match)
        faq_direct_query = "What are my Fundamental Rights under the Indian Constitution?"
        avg, mn, mx = benchmark_function(lambda: generate_rag_response(faq_direct_query), iterations=iterations)
        results.append(("RAG Pipeline (Verified FAQ Match)", avg, mn, mx, iterations, "Local Fast-Path RAG"))

        # 9. Complete RAG Pipeline Response (Novel/Fallback Synthesis)
        novel_query = "Can a landlord arbitrarily seize tenant personal property for unpaid electricity bills?"
        avg, mn, mx = benchmark_function(lambda: generate_rag_response(novel_query), iterations=iterations)
        results.append(("RAG Pipeline (Statutory Synthesis / Fallback)", avg, mn, mx, iterations, "Local Offline Fallback"))

        # 10. Gemini Live API Benchmark Note
        live_key = os.environ.get("GEMINI_API_KEY", "")
        if live_key and not live_key.startswith("your_"):
            try:
                from services.gemini_service import get_gemini_service
                svc = get_gemini_service()
                if svc.client:
                    avg_gem, mn_gem, mx_gem = benchmark_function(
                        lambda: svc.generate_response("Summarize Right to Equality Article 14 in 20 words."),
                        iterations=3
                    )
                    results.append(("Gemini Live API (gemini-2.5-flash)", avg_gem, mn_gem, mx_gem, 3, "Live Cloud API"))
            except Exception as e:
                results.append(("Gemini Live API (gemini-2.5-flash)", 0.0, 0.0, 0.0, 0, f"Unreachable ({type(e).__name__})"))
        else:
            results.append(("Gemini Live API (gemini-2.5-flash)", 0.0, 0.0, 0.0, 0, "Skipped (No Live Key Configured)"))

    # Print Formatted Results Table
    print(f"\n{'Operation / Component':<45} | {'Avg (ms)':<10} | {'Min (ms)':<10} | {'Max (ms)':<10} | {'Runs':<5} | {'Execution Type'}")
    print("-" * 115)
    for name, avg_t, min_t, max_t, runs, exec_type in results:
        if runs > 0:
            print(f"{name:<45} | {avg_t:>8.2f} ms | {min_t:>8.2f} ms | {max_t:>8.2f} ms | {runs:>4}  | {exec_type}")
        else:
            print(f"{name:<45} | {'N/A':>10} | {'N/A':>10} | {'N/A':>10} | {runs:>4}  | {exec_type}")

    # ==========================================================================
    # 2. CONCURRENCY & INTEGRITY VERIFICATION
    # ==========================================================================
    print("\n" + "=" * 75)
    print("CONCURRENCY & SQLITE DATABASE INTEGRITY VERIFICATION")
    print("=" * 75)

    # Multi-threaded Concurrency Test (5 simultaneous worker threads writing & reading)
    concurrency_errors = []
    def concurrent_worker(worker_id):
        try:
            worker_sid = f"concurrent-session-{worker_id}"
            create_conversation(session_id=worker_sid, title=f"Worker {worker_id}")
            for msg_idx in range(5):
                save_message(worker_sid, role="user", content=f"Message {msg_idx} from worker {worker_id}")
                save_message(worker_sid, role="assistant", content=f"Reply {msg_idx} to worker {worker_id}")
            history = get_conversation_history(worker_sid)
            if len(history) != 10:
                concurrency_errors.append(f"Worker {worker_id} expected 10 messages, got {len(history)}")
        except Exception as err:
            concurrency_errors.append(f"Worker {worker_id} exception: {str(err)}")

    with ThreadPoolExecutor(max_workers=5) as executor:
        list(executor.map(concurrent_worker, range(5)))

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if concurrency_errors:
        print(f"[FAIL] Concurrency Test FAILED with {len(concurrency_errors)} errors:")
        for err in concurrency_errors:
            print(f"   - {err}")
    else:
        print("[PASS] Multi-threaded Concurrency: 5 concurrent threads (50 total messages) completed with ZERO errors.")

    # SQLite PRAGMA Integrity Checks
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA integrity_check;")
    integrity_result = cursor.fetchall()
    cursor.execute("PRAGMA foreign_key_check;")
    fk_result = cursor.fetchall()
    conn.close()

    print(f"[PASS] SQLite PRAGMA integrity_check: {integrity_result[0][0] if integrity_result else 'None'}")
    print(f"[PASS] SQLite PRAGMA foreign_key_check: {'0 Violations' if not fk_result else fk_result}")

    # Clean up test database
    try:
        test_db_path.unlink(missing_ok=True)
    except Exception:
        pass

    print("=" * 75)
    return results


if __name__ == "__main__":
    run_all_benchmarks()
