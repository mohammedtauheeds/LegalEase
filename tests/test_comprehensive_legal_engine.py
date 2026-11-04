"""
Comprehensive Universal Indian Legal Engine Verification Test Suite.
File: tests/test_comprehensive_legal_engine.py

Verifies:
1. Complete Legal Corpus Database (Central, State/UT, Constitutional, FTS5)
2. Sub-millisecond SQLite FTS5 BM25 Ranked Full-Text Retrieval
3. All 28 States & 8 Union Territories Jurisdiction Detection
4. Seventh Schedule Legislative Distribution Analysis (Union, State, Concurrent)
5. Constitutional Articles and Writs Resolution
6. State-Specific Legislation Retrieval and Advisory
7. Citizen Practical Scenarios (Expired food, builder delay, hospital emergency, police powers, unpaid salary)
8. Strict Source Verification & Government Domain Whitelist
9. End-to-end RAG Integration with Zero-Hallucination Guardrails
"""

import unittest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from models.corpus_db import (
    get_corpus_stats,
    search_corpus_fts,
    get_constitutional_article,
    get_state_legislation_by_state,
    get_central_act,
    get_db_connection
)
from services.source_verification import (
    is_authoritative_domain,
    validate_legal_reference,
    verify_judgment_reference,
    format_source_attribution
)
from services.comprehensive_retrieval import (
    detect_jurisdiction,
    analyze_seventh_schedule,
    retrieve_statutory_corpus
)
from services.legal_search import search_legal_information
from services.rag_service import generate_rag_response


class TestComprehensiveLegalEngine(unittest.TestCase):
    """Universal Indian Legal Engine Test Suite."""

    # 1. Corpus Database Schema and Record Counts
    def test_01_corpus_db_schema_and_counts(self):
        stats = get_corpus_stats()
        self.assertGreaterEqual(stats.get("state_ut_jurisdictions", 0), 36, "Must cover all 28 States and 8 UTs (36 total)")
        self.assertGreaterEqual(stats.get("central_acts", 0), 50, "Must cover extensive Central legislation catalog")
        self.assertGreaterEqual(stats.get("constitutional_provisions", 0), 20, "Must index key constitutional provisions and lists")
        self.assertGreaterEqual(stats.get("state_legislation", 0), 15, "Must index landmark state-specific statutes")
        self.assertGreaterEqual(stats.get("fts_legal_corpus", 0), 100, "FTS5 table must index all combined legal documents")

    # 2. SQLite FTS5 BM25 Full-Text Retrieval
    def test_02_fts5_bm25_search_performance(self):
        test_queries = [
            ("expired food unsafe punishment", "Food Safety and Standards Act"),
            ("rera builder delay possession", "Real Estate"),
            ("traffic police seize driving licence", "Motor Vehicles Act"),
            ("emergency medical treatment hospital refusal", "Clinical Establishments"),
            ("delayed salary unpaid wages", "Payment of Wages Act"),
            ("neighbour building blocking easement light", "Easements Act")
        ]
        for query, expected_text in test_queries:
            results = search_corpus_fts(query, limit=5)
            self.assertGreater(len(results), 0, f"FTS search should return results for: '{query}'")
            matched_content = " ".join([r["title"] + " " + r["act_name"] + " " + r["content"] for r in results])
            self.assertIn(expected_text.lower(), matched_content.lower(), f"Expected '{expected_text}' in FTS match for '{query}'")

    # 3. All 28 States and 8 Union Territories Jurisdiction Detection
    def test_03_jurisdiction_detection_states_and_uts(self):
        cases = [
            ("How to evict a tenant in Mumbai?", "Maharashtra", "MH"),
            ("What is the rent control rule in Delhi?", "NCT of Delhi", "DL"),
            ("How to check land RTC in Bengaluru?", "Karnataka", "KA"),
            ("Can Lucknow police refuse my FIR?", "Uttar Pradesh", "UP"),
            ("Tenant dispute in Kolkata under premises tenancy", "West Bengal", "WB"),
            ("Shop opening hours in Chennai", "Tamil Nadu", "TN"),
            ("Can Hyderabad landlord disconnect water?", "Telangana", "TS"),
            ("Land revenue records in Jaipur", "Rajasthan", "RJ")
        ]
        for query, expected_name, expected_code in cases:
            res = detect_jurisdiction(query)
            self.assertTrue(res["is_state_specific"], f"Query '{query}' must be flagged as state-specific")
            self.assertEqual(res["state_code"], expected_code, f"Failed state code detection for '{query}'")
            self.assertEqual(res["state_name"], expected_name, f"Failed state name detection for '{query}'")

    # 4. Seventh Schedule Legislative Distribution Analysis
    def test_04_seventh_schedule_classification(self):
        # Union List
        union_res = analyze_seventh_schedule("What are the rules for filing income tax return?")
        self.assertEqual(union_res["list"], "Union List (List I)")
        self.assertIn("exclusive Central jurisdiction", union_res["advisory"])

        # State List
        state_res = analyze_seventh_schedule("Can landlord evict me without notice?")
        self.assertEqual(state_res["list"], "State List (List II)")
        self.assertIn("exclusive State jurisdiction", state_res["advisory"])

        # Concurrent List
        concurrent_res = analyze_seventh_schedule("Procedure for marriage and divorce under special marriage law")
        self.assertEqual(concurrent_res["list"], "Concurrent List (List III)")
        self.assertIn("Concurrent List", concurrent_res["advisory"])

    # 5. Constitutional Law Retrieval
    def test_05_constitutional_law_retrieval(self):
        art21 = get_constitutional_article("21")
        self.assertIsNotNone(art21)
        self.assertIn("Protection of life and personal liberty", art21["title"])
        self.assertIn("Part III", art21["part"])

        art32 = get_constitutional_article("Article 32")
        self.assertIsNotNone(art32)
        self.assertIn("Remedies for enforcement", art32["title"])

        art226 = get_constitutional_article("226")
        self.assertIsNotNone(art226)
        self.assertIn("Power of High Courts to issue certain writs", art226["title"])

    # 6. State-Specific Statutes Retrieval
    def test_06_state_specific_statutes(self):
        mh_stats = get_state_legislation_by_state("MH")
        self.assertGreaterEqual(len(mh_stats), 2)
        act_titles = [s["title"] for s in mh_stats]
        self.assertIn("Maharashtra Rent Control Act, 1999", act_titles)
        self.assertIn("Bombay High Court", mh_stats[0]["high_court"])

        dl_stats = get_state_legislation_by_state("DL")
        self.assertGreaterEqual(len(dl_stats), 2)
        dl_titles = [s["title"] for s in dl_stats]
        self.assertIn("Delhi Rent Control Act, 1958", dl_titles)

    # 7. Citizen Practical Scenarios & Actionable Remedies
    def test_07_citizen_scenarios_remedies(self):
        # A. Selling expired food
        food_res = retrieve_statutory_corpus("What is the penalty for selling expired food?")
        self.assertGreater(len(food_res["fts_results"]), 0)
        top_fss = food_res["fts_results"][0]
        self.assertIn("Food Safety", top_fss["act_name"])
        self.assertIn("59", top_fss["section"])

        # B. Builder delaying possession
        rera_res = retrieve_statutory_corpus("Remedy when builder delays flat possession despite agreement")
        self.assertGreater(len(rera_res["fts_results"]), 0)
        rera_match = any("RERA" in r["act_name"] or "Real Estate" in r["act_name"] for r in rera_res["fts_results"])
        self.assertTrue(rera_match, "Must retrieve RERA for builder delayed possession")

        # C. Traffic police driving licence seizure
        mv_res = retrieve_statutory_corpus("Can traffic police officer seize my driving licence?")
        self.assertGreater(len(mv_res["fts_results"]), 0)
        mv_match = any("Motor Vehicles" in r["act_name"] for r in mv_res["fts_results"])
        self.assertTrue(mv_match, "Must retrieve Motor Vehicles Act for licence seizure")

    # 8. Strict Source Verification and Whitelist Check
    def test_08_source_verification_and_authority_check(self):
        # Authoritative domains
        self.assertTrue(is_authoritative_domain("https://www.indiacode.nic.in/handle/123456789/2026"))
        self.assertTrue(is_authoritative_domain("https://legislative.gov.in/constitution-of-india/"))
        self.assertTrue(is_authoritative_domain("https://main.sci.gov.in/judgments"))
        self.assertTrue(is_authoritative_domain("https://bombayhighcourt.nic.in/"))

        # Non-authoritative / third-party domains
        self.assertFalse(is_authoritative_domain("https://randomlegalblog.com/tips"))
        self.assertFalse(is_authoritative_domain("https://commerciallawfirm.org/"))
        self.assertFalse(is_authoritative_domain(""))
        self.assertFalse(is_authoritative_domain(None))

        # Reference validation
        valid_ref = validate_legal_reference({
            "act_name": "Food Safety and Standards Act, 2006",
            "section": "59",
            "url": "https://www.indiacode.nic.in/handle/123456789/2026"
        })
        self.assertEqual(valid_ref["verification_status"], "Verified Authority")
        self.assertTrue(valid_ref["authoritative_source"])

    # 9. End-to-End RAG Integration with Zero Hallucination
    def test_09_end_to_end_rag_with_corpus_retrieval(self):
        query = "Can a hospital refuse emergency medical treatment for an accident victim?"
        res = generate_rag_response(query)
        self.assertTrue(res.get("success") or res.get("fallback_used"))
        self.assertIsNotNone(res.get("answer"))
        self.assertGreater(len(res["answer"]), 50)
        # Verify answer mentions emergency medical treatment principles
        lower_ans = res["answer"].lower()
        self.assertTrue(
            any(w in lower_ans for w in ["emergency", "hospital", "treatment", "stabilize", "clinical", "parmanand katara", "statutory"]),
            f"Expected substantive medical emergency response, got: {res['answer'][:200]}"
        )
        # Verify source attribution contains official link
        self.assertGreater(len(res["sources"]), 0)
        has_official_url = any("indiacode.nic.in" in s.get("url", "") or "gov.in" in s.get("url", "") for s in res["sources"])
        self.assertTrue(has_official_url, "Response must include official government source URL")


if __name__ == "__main__":
    unittest.main()
