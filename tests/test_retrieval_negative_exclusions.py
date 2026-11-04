"""
LegalEase - Negative Exclusion & Precision Retrieval Verification Suite.
File: tests/test_retrieval_negative_exclusions.py

Strictly tests real-world query precision and negative exclusions:
Ensures that for each query, forbidden cross-domain provisions, malformed section labels,
and irrelevant state/central statutes are strictly ABSENT from both retrieval and generated answers.
"""

import sys
import unittest
import json
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from services.rag_service import generate_rag_response, contextualize_query
from services.comprehensive_retrieval import analyze_seventh_schedule, retrieve_statutory_corpus
from services.source_verification import format_provision_label
from models.corpus_db import search_corpus_fts


class TestRetrievalNegativeExclusions(unittest.TestCase):
    """Rigorous tests asserting expected laws present AND forbidden laws strictly excluded."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

    def test_format_provision_label_safeguards(self):
        """Verify format_provision_label prevents erroneous section prefixing."""
        # Act years should NEVER be formatted as 'Section 2017' or 'Section 1947'
        self.assertEqual(
            format_provision_label("Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017", "2017"),
            "Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act, 2017"
        )
        self.assertEqual(
            format_provision_label("Tamil Nadu Shops and Establishments Act, 1947", "1947"),
            "Tamil Nadu Shops and Establishments Act, 1947"
        )
        self.assertEqual(
            format_provision_label("Karnataka Shops and Commercial Establishments Act, 1961", "1961"),
            "Karnataka Shops and Commercial Establishments Act, 1961"
        )
        # Act numbers should NEVER be formatted as 'Section Act 56 of 2007'
        self.assertEqual(
            format_provision_label("Senior Citizens Act", "Act 56 of 2007"),
            "Senior Citizens Act"
        )
        # Constitution should be formatted as Article, NOT Section
        self.assertEqual(
            format_provision_label("Constitution of India", "22"),
            "Constitution of India, Article 22"
        )
        self.assertEqual(
            format_provision_label("Constitution of India", "Article 22"),
            "Constitution of India, Article 22"
        )
        # Standard statute sections
        self.assertEqual(
            format_provision_label("Bharatiya Nagarik Suraksha Sanhita, 2023", "35"),
            "Bharatiya Nagarik Suraksha Sanhita, 2023, Section 35"
        )
        self.assertEqual(
            format_provision_label("Hindu Marriage Act, 1955", "24"),
            "Hindu Marriage Act, 1955, Section 24"
        )

    def test_1_police_arrest_without_warrant(self):
        """Test 1: Police arrest without warrant precision and negative exclusions."""
        query = "Can police arrest me without a warrant?"
        res = generate_rag_response(query)
        self.assertTrue(res.get("success") or res.get("fallback_used"))
        answer = res.get("answer", "")
        sources_text = " ".join([s.get("title", "") for s in res.get("sources", [])])

        # Positive assertions
        self.assertIn("35", answer)
        self.assertTrue("Bharatiya Nagarik Suraksha Sanhita" in answer or "BNSS" in answer or "22" in answer)
        self.assertIn("cognizable", answer.lower())

        # Negative exclusions: Forbidden laws and erroneous sections
        self.assertNotIn("Consumer Protection Act", answer, "CPA must not appear in police arrest query")
        self.assertNotIn("Shops and Establishments", answer, "Shops Act must not appear in police arrest query")
        self.assertNotIn("Section 1961", answer, "Section 1961 must not appear")
        self.assertNotIn("Section 1947", answer, "Section 1947 must not appear")
        self.assertNotIn("Rent Control", answer, "Rent Control advisory must not appear in police arrest query")
        self.assertNotIn("Land Revenue Code", answer, "Land Revenue must not appear in police arrest query")
        self.assertNotIn("Section 22", answer, "Constitution Article 22 must not be called Section 22")
        self.assertNotIn("Citation: .", answer, "Empty citation placeholder must not appear")

        # Seventh schedule classification must be Concurrent List (Criminal Procedure)
        sched = analyze_seventh_schedule(query)
        self.assertEqual(sched["list"], "Concurrent List (List III)")
        self.assertIn("Criminal", sched["advisory"])

    def test_2_unpaid_salary_multi_turn_independence(self):
        """Test 2: Salary inquiry following arrest query must remain independent."""
        # Multi-turn scenario: Turn 1 is arrest, Turn 2 is salary
        history = [
            {"role": "user", "content": "Can police arrest me without a warrant?"},
            {"role": "assistant", "content": "Police can arrest without warrant only in cognizable offences..."}
        ]
        q2 = "My employer has not paid my salary for two months"
        contextualized = contextualize_query(q2, history)
        # Contextualizer must preserve independence and NOT merge turn 1 arrest into turn 2
        self.assertEqual(contextualized, q2, "Independent salary query must not be polluted with preceding arrest query")

        res = generate_rag_response(q2, conversation_history=history)
        self.assertTrue(res.get("success") or res.get("fallback_used"))
        answer = res.get("answer", "")
        sources_text = " ".join([s.get("title", "") for s in res.get("sources", [])])

        # Positive assertions
        self.assertTrue("Payment of Wages Act" in answer or "Industrial Disputes Act" in answer or "Code on Wages" in answer)
        self.assertIn("15", answer)

        # Negative exclusions
        self.assertNotIn("Bharatiya Nagarik Suraksha Sanhita", answer, "BNSS must not appear in salary dispute")
        self.assertNotIn("arrest without warrant", answer.lower(), "Arrest text must not appear in salary dispute")
        self.assertNotIn("Section 35", answer, "BNSS 35 must not appear in salary dispute")
        self.assertNotIn("Section 1961", answer, "Section 1961 must not appear")
        self.assertNotIn("Section 1954", answer, "Section 1954 must not appear")
        self.assertNotIn("Karnataka Shops", sources_text, "Karnataka Shops Act must not appear when no state is specified")
        self.assertNotIn("Delhi Shops", sources_text, "Delhi Shops Act must not appear when no state is specified")

    def test_3_working_wife_claim_maintenance(self):
        """Test 3: Working wife maintenance precision and negative exclusions."""
        query = "Can a working wife claim maintenance?"
        res = generate_rag_response(query)
        self.assertTrue(res.get("success") or res.get("fallback_used"))
        answer = res.get("answer", "")
        sources_text = " ".join([s.get("title", "") for s in res.get("sources", [])])

        # Positive assertions
        self.assertTrue("Hindu Marriage Act" in answer or "HMA" in answer or "BNSS" in answer)
        self.assertTrue("24" in answer or "144" in answer or "125" in answer)
        # Must clearly answer affirmatively
        self.assertTrue("yes" in answer.lower() or "can legally claim" in answer.lower() or "not disentitled" in answer.lower())

        # Negative exclusions: Forbidden cross-domain collision Acts
        self.assertNotIn("Senior Citizens Act", answer, "Senior Citizens Act must not appear in matrimonial maintenance")
        self.assertNotIn("Parents and Senior Citizens", answer, "Parents Act must not appear in working wife maintenance")
        self.assertNotIn("Section Act 56 of 2007", answer, "Malformed section Act 56 of 2007 must not appear")
        self.assertNotIn("Occupational Safety", answer, "OSH Code must not appear in matrimonial maintenance")
        self.assertNotIn("OSH Code", answer, "OSH Code must not appear in matrimonial maintenance")
        self.assertNotIn("Social Security Code", answer, "Social Security Code must not appear in maintenance")
        self.assertNotIn("POSH Act", answer, "POSH Act must not appear in maintenance")
        self.assertNotIn("Maternity Benefit", answer, "Maternity Benefit Act must not appear in maintenance")

    def test_4_defective_mobile_phone(self):
        """Test 4: Defective mobile phone consumer dispute and negative exclusions."""
        query = "Defective mobile phone"
        res = generate_rag_response(query)
        self.assertTrue(res.get("success") or res.get("fallback_used"))
        answer = res.get("answer", "")
        sources_text = " ".join([s.get("title", "") for s in res.get("sources", [])])

        # Positive assertions
        self.assertIn("Consumer Protection Act, 2019", answer)
        self.assertTrue("35" in answer or "2" in answer)
        self.assertTrue("1915" in answer or "consumerhelpline" in answer or "e-daakhil" in answer.lower())

        # Negative exclusions: State shops acts must not appear in central consumer dispute
        self.assertNotIn("Delhi Shops", answer, "Delhi Shops Act must not appear in consumer defect dispute")
        self.assertNotIn("Karnataka Shops", answer, "Karnataka Shops Act must not appear in consumer defect dispute")
        self.assertNotIn("Section 1961", answer, "Section 1961 must not appear")
        self.assertNotIn("Section 1954", answer, "Section 1954 must not appear")
        self.assertNotIn("Police Act", answer, "Police Act must not appear")

    def test_5_tamil_nadu_landlord_eviction(self):
        """Test 5: Landlord eviction in Tamil Nadu precision and negative exclusions."""
        query = "Landlord eviction without notice in Tamil Nadu"
        res = generate_rag_response(query)
        self.assertTrue(res.get("success") or res.get("fallback_used"))
        answer = res.get("answer", "")
        sources_text = " ".join([s.get("title", "") for s in res.get("sources", [])])

        # Positive assertions
        self.assertTrue(
            "Tamil Nadu Regulation of Rights and Responsibilities of Landlords and Tenants Act" in answer
            or "TNRRRLT" in answer
        )
        self.assertIn("21", answer)
        self.assertIn("Tamil Nadu", answer)

        # Negative exclusions: TN Shops Act and malformed section years
        self.assertNotIn("Tamil Nadu Shops and Establishments Act", answer, "TN Shops Act must not appear in tenancy dispute")
        self.assertNotIn("Section 1947", answer, "Section 1947 must not appear")
        self.assertNotIn("Section 2017", answer, "Section 2017 must not appear")
        self.assertNotIn("Tamil Nadu Shops", sources_text, "TN Shops Act must not appear in sources")

    def test_6_live_flask_api_endpoint(self):
        """Test 6: Verify all 5 queries over live Flask /api/chat endpoint."""
        test_queries = [
            ("Can police arrest me without a warrant?", ["Bharatiya Nagarik Suraksha Sanhita", "BNSS", "22"], ["Shops", "Consumer Protection", "Section 1961"]),
            ("My employer has not paid my salary for two months", ["Payment of Wages Act", "15"], ["BNSS", "Arrest", "Shops and Establishments"]),
            ("Can a working wife claim maintenance?", ["Hindu Marriage Act", "24"], ["Senior Citizens", "OSH Code", "Section Act 56 of 2007"]),
            ("Defective mobile phone", ["Consumer Protection Act", "35"], ["Shops and Establishments", "Police Act"]),
            ("Landlord eviction without notice in Tamil Nadu", ["Tamil Nadu Regulation of Rights and Responsibilities", "21"], ["Tamil Nadu Shops", "Section 2017", "Section 1947"])
        ]

        for query_text, expected_present, forbidden_absent in test_queries:
            resp = self.client.post(
                "/api/chat",
                data=json.dumps({"message": query_text}),
                content_type="application/json"
            )
            self.assertEqual(resp.status_code, 200, f"Failed for query: {query_text}")
            data = resp.get_json()
            self.assertTrue(data.get("success"), f"API success False for {query_text}")
            ans = data.get("answer", "")

            # Verify standard 8 sections exist
            self.assertIn("### Direct Answer", ans)
            self.assertIn("### Relevant Law", ans)
            self.assertIn("### Explanation in Simple English", ans)
            self.assertIn("### Conditions and Exceptions", ans)
            self.assertIn("### Rights of the Person", ans)
            self.assertIn("### Available Remedies", ans)
            self.assertIn("### Practical Next Steps", ans)
            self.assertIn("### Sources", ans)

            # Assert positives
            has_expected = any(exp.lower() in ans.lower() for exp in expected_present)
            self.assertTrue(has_expected, f"Expected {expected_present} not found in response for '{query_text}'")

            # Assert negative exclusions
            for forbidden in forbidden_absent:
                self.assertNotIn(forbidden.lower(), ans.lower(), f"Forbidden '{forbidden}' was found in response for '{query_text}'")


if __name__ == "__main__":
    unittest.main()
