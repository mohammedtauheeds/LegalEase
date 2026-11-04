"""
LegalEase - Comprehensive Multi-Domain Verification Suite
File: tests/test_expanded_knowledge.py

Verifies:
1. Complete 1,050 Legal FAQ records across all 35 distinct domains (30 questions each).
2. Expanded statutory repository with 50+ Central Acts and 100+ verified provisions.
3. High-precision NLP legal reference extraction across diverse domains.
4. Expanded multi-domain intent classification.
5. Grounded RAG responses with zero generic fallback across distinct Indian legal domains.
6. Automated emergency helpline triggers for high-risk domains (1930, 1915, 15100, 1091, 1098, 14567).
7. Modern vs legacy criminal law transition cross-referencing (BNS/IPC, BNSS/CrPC, BSA/IEA).
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pandas as pd
from config import Config
from models.legal_nlp import LegalNLP, find_best_faq, get_nlp_engine
from models.statutory_provisions import SUPPORTED_ACTS, VERIFIED_STATUTE_FALLBACK
from services.legal_api_service import get_statute, retrieve_legal_context
from services.legal_search import search_legal_information
from services.rag_service import generate_rag_response


@patch("time.sleep", return_value=None)
class TestExpandedKnowledge(unittest.TestCase):
    """Test suite verifying full-scale expansion across all 35 areas of Indian law."""

    def test_01_faq_dataset_35_domains_1050_records(self, mock_sleep):
        """Verify FAQ dataset exists, has 1,050 records, exactly 35 topics, and 30 questions each."""
        faq_path = Config.FAQ_DATASET_PATH
        self.assertTrue(faq_path.exists(), f"FAQ dataset missing at {faq_path}")

        df = pd.read_csv(faq_path, encoding="utf-8")
        self.assertEqual(df.shape[0], 1050, f"Expected 1050 rows, got {df.shape[0]}")
        self.assertEqual(df.shape[1], 8, f"Expected 8 columns, got {df.shape[1]}")

        # Ensure no null values anywhere
        self.assertFalse(df.isnull().any().any(), "Dataset contains null or NaN values")

        # Verify distinct topics
        topics = df["topic"].value_counts()
        self.assertEqual(len(topics), 35, f"Expected 35 distinct legal topics, got {len(topics)}")

        for topic_name, count in topics.items():
            self.assertEqual(count, 30, f"Topic '{topic_name}' must have 30 records, got {count}")

        # Verify all questions are non-empty and unique
        questions = df["question"].str.strip().str.lower()
        self.assertEqual(len(questions.unique()), 1050, "All 1,050 questions must be unique")

    def test_02_supported_acts_expanded_coverage(self, mock_sleep):
        """Verify SUPPORTED_ACTS contains at least 50 Central Acts spanning all major legal areas."""
        self.assertGreaterEqual(len(SUPPORTED_ACTS), 50, f"Expected 50+ acts, got {len(SUPPORTED_ACTS)}")

        essential_acts = [
            "constitution", "bns", "ipc", "bnss", "crpc", "bsa", "iea", "cpc",
            "contract_act", "cpa", "it_act", "dpdp", "dv_act", "posh", "pocso",
            "maternity_benefit", "hma", "hsa", "tpa", "model_tenancy", "rera",
            "code_on_wages", "sarfaesi", "ni_act", "companies_act", "ibc",
            "pmla", "mv_act", "copyright_act", "patents_act", "trademark_act",
            "rti_act", "epa", "ngt_act", "rte_act", "senior_citizens", "sc_st_act",
            "poca", "arbitration_act", "mediation_act", "lsaa", "it_tax_act",
            "cgst_act", "citizenship_act", "passports_act"
        ]
        for act in essential_acts:
            self.assertIn(act, SUPPORTED_ACTS, f"Missing essential Act slug '{act}' in SUPPORTED_ACTS")
            self.assertIn("name", SUPPORTED_ACTS[act])
            self.assertIn("source_url", SUPPORTED_ACTS[act])

    def test_03_verified_statute_fallback_coverage(self, mock_sleep):
        """Verify VERIFIED_STATUTE_FALLBACK has 100+ verified provisions across diverse legal fields."""
        self.assertGreaterEqual(len(VERIFIED_STATUTE_FALLBACK), 100, f"Expected 100+ provisions, got {len(VERIFIED_STATUTE_FALLBACK)}")

        sample_provisions = [
            ("constitution", "14"),
            ("constitution", "21"),
            ("constitution", "32"),
            ("constitution", "141"),
            ("bns", "103"),
            ("bns", "303"),
            ("bns", "318"),
            ("bnss", "173"),
            ("bnss", "482"),
            ("bsa", "61"),
            ("cpc", "80"),
            ("cpa", "35"),
            ("it_act", "66D"),
            ("ni_act", "138"),
            ("dv_act", "12"),
            ("posh", "9"),
            ("pocso", "19"),
            ("sc_st_act", "3"),
            ("poca", "7"),
            ("rera", "18"),
            ("mv_act", "185"),
            ("senior_citizens", "4"),
            ("senior_citizens", "23"),
            ("rti_act", "6"),
            ("arbitration_act", "9"),
            ("lsaa", "21"),
        ]
        for act_slug, sec in sample_provisions:
            stat = get_statute(act_slug, sec)
            self.assertTrue(stat["success"], f"Failed to retrieve statutory fallback for ({act_slug}, {sec})")
            self.assertIsNotNone(stat["data"]["heading"])
            self.assertIsNotNone(stat["data"]["text"])

    def test_04_nlp_entity_extraction_multidomain(self, mock_sleep):
        """Verify that NLP extracts statutory sections across modern and legacy laws."""
        nlp = get_nlp_engine()

        test_cases = [
            ("What is the penalty under Section 138 of NI Act?", "138", "ni_act"),
            ("How to file application under Section 12 of DV Act?", "12", "dv_act"),
            ("Procedure under Section 9 of POSH Act for complaint?", "9", "posh"),
            ("Builder delay under Section 18 of RERA?", "18", "rera"),
            ("Drunk driving under Section 185 of MV Act?", "185", "mv_act"),
            ("RTI application timeline under Section 6 of RTI Act?", "6", "rti_act"),
            ("Section 318 of BNS for fraud", "318", "bns"),
            ("Cheating case under Section 420 IPC", "420", "ipc"),
            ("Anticipatory bail under Section 482 of BNSS", "482", "bnss"),
            ("Notice requirement under Section 80 of CPC", "80", "cpc"),
        ]

        for query, expected_sec, expected_slug in test_cases:
            refs = nlp.extract_legal_references(query)
            matches = [r for r in refs if r.get("number") == expected_sec and r.get("slug") == expected_slug]
            self.assertTrue(len(matches) > 0, f"Query '{query}' failed to extract ({expected_slug}, {expected_sec}). Got: {refs}")

    def test_05_nlp_intent_classification_multidomain(self, mock_sleep):
        """Verify that intent classification handles multi-domain queries accurately."""
        nlp = get_nlp_engine()

        intent_tests = [
            ("How to report an online credit card phishing scam?", "report_cybercrime"),
            ("What should I do if my cheque bounced for insufficient funds?", "cheque_bounce_inquiry"),
            ("Where can I report child sexual abuse and what is childline?", "child_protection_pocso"),
            ("Can elderly parents evict abusive adult son from their home?", "senior_citizen_welfare"),
            ("Government official demanding bribe for issuing certificate", "anti_corruption_inquiry"),
            ("Casteist abuse and atrocity against scheduled caste person", "sc_st_protection"),
            ("Hospital detained dead body for unpaid medical bill", "medical_patient_rights"),
            ("What is the fine for drunk driving on highways?", "motor_accident_traffic"),
            ("How to file consumer complaint on e-Daakhil for defective phone?", "consumer_grievance"),
            ("Free lawyer for woman through NALSA or DLSA", "find_legal_aid"),
            ("Landlord disconnected electricity without notice", "tenant_rental"),
            ("What is the gratuity eligibility after 5 years service?", "labour_employment_inquiry"),
        ]

        for query, expected_intent in intent_tests:
            intent = nlp.classify_intent(query)
            self.assertEqual(intent, expected_intent, f"Query '{query}' classified as '{intent}' instead of '{expected_intent}'")

    def test_06_rag_diverse_domain_answers(self, mock_sleep):
        """Verify that RAG generates distinct, informative answers across completely different domains."""
        domain_queries = [
            "How can a senior citizen claim maintenance from children?",
            "What is the procedure for cheque bounce notice under Section 138?",
            "What is the 25% EWS quota in private schools under RTE?",
            "Can hospital refuse emergency treatment without advance deposit?",
            "What are the rights of a woman in domestic violence shared household?"
        ]

        answers = {}
        for q in domain_queries:
            res = generate_rag_response(q)
            self.assertIsNotNone(res.get("answer"), f"RAG returned None answer for query: {q}")
            ans = res.get("answer", "")
            self.assertGreater(len(ans), 80, f"Answer too short for query: {q}")
            answers[q] = ans

        # All answers must be distinct and specific
        self.assertEqual(len(set(answers.values())), len(domain_queries), "All domain answers must be unique!")

    def test_07_emergency_helplines_appended(self, mock_sleep):
        """Verify emergency helplines are appended for high-risk domains."""
        # 1. Cybercrime -> 1930
        res_cyber = generate_rag_response("Someone stole money from my bank account online fraud")
        self.assertIn("1930", res_cyber["answer"])

        # 2. Consumer -> 1915
        res_consumer = generate_rag_response("Defective refrigerator seller refusing refund consumer complaint")
        self.assertIn("1915", res_consumer["answer"])

        # 3. Free Legal Aid -> 15100
        res_legalaid = generate_rag_response("I need a free government lawyer from NALSA")
        self.assertIn("15100", res_legalaid["answer"])

        # 4. Women in Distress -> 1091 or 181
        res_women = generate_rag_response("Where can a woman get help for domestic violence?")
        self.assertTrue(any(num in res_women["answer"] for num in ["1091", "181", "112"]))

        # 5. Childline -> 1098
        res_pocso = generate_rag_response("How to report child abuse under POCSO Act?")
        self.assertIn("1098", res_pocso["answer"])

        # 6. Senior Citizens -> 14567
        res_senior = generate_rag_response("Helpline for senior citizen abandoned by children")
        self.assertIn("14567", res_senior["answer"])

    def test_08_statutory_transition_cross_referencing(self, mock_sleep):
        """Verify modern BNS/BNSS/BSA provisions include historical cross-references."""
        # Section 318 BNS should cross-reference IPC 420
        stat_bns = get_statute("bns", "318")
        self.assertTrue(stat_bns["success"])
        self.assertIn("420", stat_bns["data"].get("corresponding_provision", ""))

        # Section 103 BNS should cross-reference IPC 302
        stat_murder = get_statute("bns", "103")
        self.assertTrue(stat_murder["success"])
        self.assertIn("302", stat_murder["data"].get("corresponding_provision", ""))

        # Section 173 BNSS should cross-reference CrPC 154
        stat_fir = get_statute("bnss", "173")
        self.assertTrue(stat_fir["success"])
        self.assertIn("154", stat_fir["data"].get("corresponding_provision", ""))


if __name__ == "__main__":
    unittest.main()
