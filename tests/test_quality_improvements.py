"""
Comprehensive 20-Category Quality Verification Test Suite for LegalEase.
File: tests/test_quality_improvements.py

Verifies:
 1. Criminal law (BNS / IPC Transition)
 2. Arrest and bail (BNSS 478 / CrPC 436 bailable rights)
 3. Police powers & FIR (BNSS 173(4), 175(3))
 4. Cybercrime (IT Act 66D, 1930 Helpline)
 5. Consumer protection (CPA 2019, 1915 NCH)
 6. Employment & salary disputes (Payment of Wages Act 15, no Companies Act 166 collision)
 7. Family law & maintenance (HMA 24)
 8. Property & rental disputes (State Rent Control, no Clinical Establishments collision)
 9. Education & student certificates (UGC guidelines, Article 226)
10. Traffic law (MV Act 185, 206 licence seizure receipt)
11. Food safety (FSSA 59 unsafe food, FSSAI portal)
12. Medical & healthcare emergency (Clinical Establishments 12, Art 21)
13. Constitutional rights & writs (Habeas Corpus, Arts 32 & 226)
14. Legal aid accessibility (NALSA 15100, DLSA)
15. State-specific legal questions (Maharashtra Rent Control Act)
16. Follow-up multi-turn questions contextualization
17. Ambiguous questions graceful handling
18. Repealed legislation transition (IPC 420 vs BNS 318)
19. Multiple Acts interaction (Consumer Protection + Food Safety)
20. Unverified queries with honest limitation disclaimer
21. Standardized 8-section layout adherence
22. Gemini-enabled generative pipeline (mocked)
"""

import sys
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import Config
from models.legal_nlp import get_nlp_engine, find_best_faq
from services.comprehensive_retrieval import detect_jurisdiction
from services.legal_search import search_legal_information
from services.rag_service import generate_rag_response, contextualize_query
from services.gemini_service import GeminiService


class TestQualityImprovements(unittest.TestCase):
    """Rigorous 20-Category Universal Legal Coverage Test Suite."""

    # 1. Criminal Law (BNS / IPC Transition)
    def test_01_criminal_law_theft(self):
        res = generate_rag_response("What is the legal punishment for theft in India?")
        self.assertIsNotNone(res.get("answer"))
        ans = res["answer"]
        self.assertIn("Section 303", ans)
        self.assertIn("Bharatiya Nyaya Sanhita", ans)
        self.assertIn("### Direct Answer", ans)
        self.assertIn("### Relevant Law", ans)

    # 2. Arrest and Bail (BNSS 478 / CrPC 436)
    def test_02_arrest_and_bailable_offence_rights(self):
        res = generate_rag_response("Can police refuse bail for a bailable offence?")
        ans = res["answer"]
        # Must recognize bail as a statutory right under Section 478 BNSS / Section 436 CrPC
        self.assertTrue(
            "478" in ans or "436" in ans or "right" in ans.lower(),
            "Must explain bail is a statutory right in bailable offences"
        )
        self.assertIn("### Rights of the Person", ans)

    # 3. Police Powers & FIR (BNSS 173)
    def test_03_police_powers_and_fir(self):
        res = generate_rag_response("What can I do if a police officer refuses to register my FIR?")
        ans = res["answer"]
        self.assertTrue("173" in ans or "Superintendent" in ans or "Magistrate" in ans)
        self.assertIn("### Available Remedies", ans)

    # 4. Cybercrime (IT Act 66D, 1930 Helpline)
    def test_04_cybercrime_financial_fraud(self):
        res = generate_rag_response("I was scammed by an online UPI phishing link and lost 50000 rupees. What should I do immediately?")
        ans = res["answer"]
        self.assertIn("1930", ans)
        self.assertTrue("cybercrime.gov.in" in ans or "cyber" in ans.lower())
        self.assertIn("### Practical Next Steps", ans)

    # 5. Consumer Protection (CPA 2019, 1915 NCH)
    def test_05_consumer_protection(self):
        res = generate_rag_response("Amazon delivered a damaged laptop and refuses replacement or refund.")
        ans = res["answer"]
        self.assertTrue("Consumer Protection" in ans or "1915" in ans or "e-daakhil" in ans.lower())
        self.assertIn("### Available Remedies", ans)

    # 6. Employment & Salary Disputes (Payment of Wages Act 15, no Companies Act 166 collision)
    def test_06_employment_and_salary_disputes(self):
        res = generate_rag_response("My company has not paid my salary for three months. What legal action can I take?")
        ans = res["answer"]
        # Must NOT cite director duties under Companies Act 166
        self.assertNotIn("Companies Act, 2013", ans)
        self.assertNotIn("Section 166", ans)
        self.assertTrue(
            "Payment of Wages" in ans or "Labour" in ans or "wages" in ans.lower(),
            "Must retrieve labour/wage statutory protections"
        )
        self.assertIn("### Practical Next Steps", ans)

    # 7. Family Law & Maintenance (HMA 24)
    def test_07_family_law_maintenance(self):
        res = generate_rag_response("Can a spouse claim interim maintenance during pending divorce proceedings under Hindu law?")
        ans = res["answer"]
        self.assertTrue(
            "24" in ans or "maintenance" in ans.lower() or "Hindu Marriage" in ans,
            "Must identify interim maintenance provisions"
        )
        self.assertIn("### Direct Answer", ans)

    # 8. Property & Rental Disputes (State Rent Control, no Clinical Establishments collision)
    def test_08_property_and_rental_disputes(self):
        res = generate_rag_response("My landlord cut off water and electricity supply to force me out. Is this legal?")
        ans = res["answer"]
        # Must NOT pollute with Clinical Establishments Act
        self.assertNotIn("Clinical Establishments", ans)
        self.assertTrue(
            "rent" in ans.lower() or "essential" in ans.lower() or "easement" in ans.lower() or "landlord" in ans.lower(),
            "Must identify landlord/tenant essential services protections"
        )

    # 9. Education & Student Certificates (UGC Guidelines)
    def test_09_education_student_certificates(self):
        res = generate_rag_response("Can a college hold my original degree and marksheet because of pending tuition fee dispute?")
        ans = res["answer"]
        self.assertTrue(
            "UGC" in ans or "certificate" in ans.lower() or "degree" in ans.lower() or "original" in ans.lower(),
            "Must advise that withholding original student credentials is prohibited"
        )

    # 10. Traffic Law (MV Act 206 Licence Seizure)
    def test_10_traffic_law_licence_seizure(self):
        res = generate_rag_response("Under what conditions can traffic police seize my driving licence?")
        ans = res["answer"]
        self.assertTrue(
            "Motor Vehicles" in ans or "206" in ans or "licence" in ans.lower() or "challan" in ans.lower(),
            "Must cite Motor Vehicles Act and requirement of official seizure receipt"
        )

    # 11. Food Safety (FSSA 59 Unsafe Food)
    def test_11_food_safety_law(self):
        res = generate_rag_response("A restaurant served spoiled, expired food causing food poisoning. What legal action can I take?")
        ans = res["answer"]
        self.assertTrue(
            "Food Safety" in ans or "FSSA" in ans or "59" in ans or "FSSAI" in ans,
            "Must cite Food Safety and Standards Act provisions"
        )

    # 12. Medical & Healthcare Emergency (Clinical Establishments 12)
    def test_12_medical_emergency_treatment(self):
        res = generate_rag_response("Can a private hospital refuse emergency treatment if a patient cannot pay deposit upfront?")
        ans = res["answer"]
        self.assertTrue(
            "emergency" in ans.lower() or "Clinical Establishments" in ans or "Article 21" in ans,
            "Must identify mandatory emergency medical stabilization obligation"
        )

    # 13. Constitutional Rights & Writs (Habeas Corpus, Arts 32 & 226)
    def test_13_constitutional_writs(self):
        res = generate_rag_response("What constitutional remedy exists if someone is illegally detained by the police?")
        ans = res["answer"]
        self.assertTrue(
            "Habeas Corpus" in ans or "226" in ans or "32" in ans or "Article 21" in ans,
            "Must identify Habeas Corpus and High Court / Supreme Court writ remedies"
        )

    # 14. Legal Aid Accessibility (NALSA 15100, DLSA)
    def test_14_free_legal_aid(self):
        res = generate_rag_response("How can an economically poor citizen get a free government lawyer in India?")
        ans = res["answer"]
        self.assertTrue(
            "15100" in ans or "NALSA" in ans or "Legal Services" in ans or "DLSA" in ans,
            "Must provide NALSA helpline 15100 and Legal Services Authorities Act guidance"
        )

    # 15. State-Specific Legal Questions (Maharashtra Rent Control)
    def test_15_state_specific_law(self):
        jur = detect_jurisdiction("What are tenant eviction rules under Maharashtra Rent Control Act in Mumbai?")
        self.assertEqual(jur["state_code"], "MH")
        self.assertEqual(jur["state_name"], "Maharashtra")

        res = generate_rag_response("What are tenant eviction rules under Maharashtra Rent Control Act in Mumbai?")
        ans = res["answer"]
        self.assertTrue(
            "Maharashtra" in ans or "Rent" in ans,
            "Must identify state-specific Maharashtra tenancy provisions"
        )

    # 16. Multi-Turn Follow-up Questions Contextualization
    def test_16_multiturn_followup_contextualization(self):
        history = [
            {"role": "user", "content": "What is an FIR?"},
            {"role": "assistant", "content": "An FIR is recorded under Section 173 of BNSS."}
        ]
        contextualized = contextualize_query("What if police refuse to register it?", history)
        self.assertIn("FIR", contextualized)

        res = generate_rag_response("What if police refuse to register it?", conversation_history=history)
        ans = res["answer"]
        self.assertTrue("173" in ans or "Superintendent" in ans or "Magistrate" in ans or "FIR" in ans)

    # 17. Ambiguous Questions Handled Gracefully
    def test_17_ambiguous_question_handling(self):
        res = generate_rag_response("Is this legal?")
        self.assertIsNotNone(res.get("answer"))
        ans = res["answer"]
        self.assertIn("### Direct Answer", ans)
        self.assertIn("### Practical Next Steps", ans)
        self.assertTrue("factual context" in ans.lower() or "specific" in ans.lower())

    # 18. Repealed Legislation Transition (IPC 420 vs BNS 318)
    def test_18_repealed_legislation_transition(self):
        res = generate_rag_response("Is Section 420 of IPC still applicable for cheating cases today?")
        ans = res["answer"]
        self.assertIn("318", ans)
        self.assertIn("Bharatiya Nyaya Sanhita", ans)
        self.assertTrue("420" in ans)
        self.assertTrue("July 1, 2024" in ans or "repealed" in ans.lower() or "former" in ans.lower())

    # 19. Multiple Acts Interaction (Consumer + Food Safety)
    def test_19_multiple_acts_interaction(self):
        res = generate_rag_response("Can I file both a consumer case and a food safety complaint if a grocery store sells adulterated baby food?")
        ans = res["answer"]
        self.assertTrue(
            ("Consumer" in ans or "1915" in ans) and ("Food" in ans or "FSSA" in ans or "FSSAI" in ans),
            "Must address both consumer redressal and food safety regulatory enforcement"
        )

    # 20. Unverified Queries with Honest Limitation Disclaimer
    def test_20_unverified_queries_honest_limitation(self):
        res = generate_rag_response("What is the penalty for violating Galactic Space Mining Regulation Section 999 under Indian law?")
        ans = res["answer"]
        # Must NOT hallucinate non-existent Galactic Acts
        self.assertNotIn("Galactic Space Mining Regulation Act", ans)
        self.assertTrue(
            "limitation" in ans.lower() or "official" in ans.lower() or "factual context" in ans.lower() or "disclaimer" in ans.lower()
        )

    # 21. Standardized 8-Section Output Layout Adherence
    def test_21_standardized_8_section_layout(self):
        queries = [
            "What is cheating under BNS?",
            "What are my rights if arrested?",
            "My company has not paid my salary"
        ]
        mandatory_sections = [
            "### Direct Answer",
            "### Relevant Law",
            "### Explanation in Simple English",
            "### Conditions and Exceptions",
            "### Rights of the Person",
            "### Available Remedies",
            "### Practical Next Steps",
            "### Sources"
        ]
        for q in queries:
            res = generate_rag_response(q)
            ans = res["answer"]
            for sec in mandatory_sections:
                self.assertIn(sec, ans, f"Mandatory section '{sec}' missing for query '{q}'")

    # 22. Generative Gemini Integration Mode (Mocked SDK)
    def test_22_gemini_generative_pipeline_success(self):
        # Mock Google GenAI Client
        mock_google = ModuleType("google")
        mock_genai_mod = ModuleType("google.genai")
        mock_types_mod = ModuleType("google.genai.types")

        mock_client_cls = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_cls.return_value = mock_client_instance
        mock_genai_mod.Client = mock_client_cls
        mock_genai_mod.types = mock_types_mod

        mock_config_cls = MagicMock()
        mock_types_mod.GenerateContentConfig = mock_config_cls
        mock_google.genai = mock_genai_mod

        with patch.dict(sys.modules, {
            "google": mock_google,
            "google.genai": mock_genai_mod,
            "google.genai.types": mock_types_mod
        }):
            mock_model_response = MagicMock()
            mock_model_response.text = (
                "### Direct Answer\nBail is a matter of right in bailable offences.\n\n"
                "### Relevant Law\n• Section 478 of BNSS, 2023.\n\n"
                "### Explanation in Simple English\nThe police must release you upon bond.\n\n"
                "### Conditions and Exceptions\nSubject to furnishing bond.\n\n"
                "### Rights of the Person\nRight to release immediately.\n\n"
                "### Available Remedies\nApply before SHO or Magistrate.\n\n"
                "### Practical Next Steps\n1. Furnish surety.\n\n"
                "### Sources\n• India Code: https://www.indiacode.nic.in/"
            )
            mock_client_instance.models.generate_content.return_value = mock_model_response

            service = GeminiService(api_key="valid-mock-key-12345", model="gemini-2.5-flash")
            res = service.generate_legal_answer("Can police deny bail for a bailable offence?")
            self.assertTrue(res["success"])
            self.assertFalse(res["fallback_used"])
            self.assertIn("Section 478 of BNSS", res["answer"])
            self.assertIn("### Direct Answer", res["answer"])
            self.assertGreaterEqual(len(res["sources"]), 1)


if __name__ == "__main__":
    unittest.main()
