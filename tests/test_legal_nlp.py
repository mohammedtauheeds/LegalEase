"""
Unit tests for LegalEase NLP & FAQ Matching Engine (models/legal_nlp.py).
Tests:
- Dataset loading
- TF-IDF vectorization
- Correct FAQ matching
- Similarity score calculation
- Threshold behavior
- Empty input handling
- Unknown or unrelated questions
- Intent recognition
- Legal section extraction
- Duplicate question handling
"""

import sys
import unittest
from pathlib import Path

# Set up path resolution to import LegalEase modules
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config import Config
from models.legal_nlp import LegalNLP, find_best_faq, get_nlp_engine


class TestLegalNLP(unittest.TestCase):
    """Test suite for LegalNLP class and matching functions."""

    @classmethod
    def setUpClass(cls):
        """Initialize the NLP engine once for the test suite."""
        cls.nlp = LegalNLP(threshold=0.70)

    def test_dataset_loading(self):
        """1. Verify that the FAQ dataset is loaded and has >= 100 records."""
        self.assertFalse(self.nlp.df.empty, "Dataset should not be empty")
        self.assertGreaterEqual(len(self.nlp.df), 100, "Dataset must have at least 100 records")
        expected_cols = ["id", "question", "answer", "topic", "act_name", "section", "source_title", "source_url"]
        for col in expected_cols:
            self.assertIn(col, self.nlp.df.columns, f"Expected column {col} missing in dataset")

    def test_tfidf_vectorization(self):
        """2. Verify that TF-IDF vectorizer and feature matrices are properly created."""
        self.assertIsNotNone(self.nlp.vectorizer, "Vectorizer must not be None")
        self.assertIsNotNone(self.nlp.faq_vectors, "FAQ vectors must not be None")
        self.assertEqual(self.nlp.faq_vectors.shape[0], len(self.nlp.df), "Vector rows must equal record count")
        self.assertGreater(self.nlp.faq_vectors.shape[1], 100, "TF-IDF vocabulary should have substantial features")

    def test_correct_faq_matching(self):
        """3. Verify that exact or near-exact questions match the correct FAQ with high score."""
        query = "What is the Preamble of the Indian Constitution and what does it declare?"
        result = self.nlp.find_best_faq(query)
        self.assertTrue(result["matched"], "Exact question should match")
        self.assertGreaterEqual(result["similarity_score"], 0.95, "Exact match should have score >= 0.95")
        self.assertEqual(result["topic"], "Indian Constitution")
        self.assertEqual(result["section"], "Preamble")
        self.assertIn("Sovereign", result["answer"])

    def test_similarity_score_calculation(self):
        """4. Verify that paraphrased queries produce logical similarity scores between 0.0 and 1.0."""
        query = "How to report online cyber fraud and financial scam?"
        result = self.nlp.find_best_faq(query, threshold=0.40)
        self.assertGreater(result["similarity_score"], 0.40, "Paraphrased cybercrime question should have good score")
        self.assertLessEqual(result["similarity_score"], 1.0, "Score cannot exceed 1.0")
        self.assertEqual(result["topic"], "Cybercrime and Online Fraud")

    def test_threshold_behavior(self):
        """5. Verify that queries below threshold are marked matched=False and require AI generation."""
        query = "Can a school punish a student for bringing a mobile phone?"
        # High threshold test: this specific question isn't in FAQ
        result = self.nlp.find_best_faq(query, threshold=0.85)
        self.assertFalse(result["matched"], "Unindexed question should not match with high threshold")
        self.assertTrue(result["requires_ai_generation"], "Should trigger AI generation")
        self.assertEqual(result["answer"], "", "Unmatched query must not return an unrelated FAQ answer")

    def test_empty_input_handling(self):
        """6. Verify safe handling of empty strings and whitespace."""
        for empty_query in ["", "   ", "\t\n", None]:
            result = self.nlp.find_best_faq(empty_query)
            self.assertFalse(result["matched"], "Empty query must not match")
            self.assertEqual(result["similarity_score"], 0.0)
            self.assertFalse(result["requires_ai_generation"])

    def test_unrelated_or_unknown_questions(self):
        """7. Verify handling of off-topic and greeting queries."""
        # Greeting test
        greet_result = self.nlp.find_best_faq("Hello there!")
        self.assertFalse(greet_result["matched"])
        self.assertEqual(greet_result["intent"], "greeting")
        self.assertIn("Namaste", greet_result["answer"])

        # Off-topic non-legal test
        off_topic_result = self.nlp.find_best_faq("How to cook delicious chicken biryani recipe?")
        self.assertFalse(off_topic_result["matched"])
        self.assertEqual(off_topic_result["intent"], "non_legal")
        self.assertIn("dedicated to providing awareness", off_topic_result["answer"])

    def test_intent_recognition(self):
        """8. Verify intent classification across different legal categories."""
        test_cases = [
            ("Someone stole 50000 rupees in online fraud 1930", "report_cybercrime"),
            ("The seller sent a defective phone and refused refund", "consumer_grievance"),
            ("How do I register a Zero FIR at a police station?", "police_complaint_fir"),
            ("Where can poor people get a free lawyer from NALSA?", "find_legal_aid"),
            ("What are my fundamental rights under Article 21?", "understand_rights"),
            ("Can landlord disconnect my electricity to evict me?", "tenant_rental"),
            ("What is the time limit procedure to file an appeal?", "understand_procedure"),
            ("What does Section 318 BNS say?", "statutory_inquiry"),
        ]
        for text, expected_intent in test_cases:
            detected_intent = self.nlp.classify_intent(text)
            self.assertEqual(
                detected_intent, expected_intent,
                f"Failed intent detection for query: '{text}' (Got: {detected_intent}, Expected: {expected_intent})"
            )

    def test_legal_section_extraction(self):
        """9. Verify extraction of sections, articles, and Act slugs."""
        # Test BNS extraction
        refs_bns = self.nlp.extract_legal_references("Punishment under Section 318 of the BNS")
        self.assertTrue(len(refs_bns) > 0)
        self.assertEqual(refs_bns[0]["number"], "318")
        self.assertEqual(refs_bns[0]["slug"], "bns")

        # Test Constitution Article extraction
        refs_art = self.nlp.extract_legal_references("Protection of life under Article 21 and Article 32")
        self.assertEqual(len(refs_art), 2)
        self.assertEqual(refs_art[0]["number"], "21")
        self.assertEqual(refs_art[1]["number"], "32")
        self.assertEqual(refs_art[0]["slug"], "constitution")

        # Test BNSS extraction
        refs_bnss = self.nlp.extract_legal_references("Arrest procedure under Section 35 BNSS")
        self.assertTrue(len(refs_bnss) > 0)
        self.assertEqual(refs_bnss[0]["number"], "35")
        self.assertEqual(refs_bnss[0]["slug"], "bnss")

    def test_duplicate_question_handling(self):
        """10. Verify that dataset has zero duplicate questions."""
        questions_normalized = self.nlp.df["question"].apply(self.nlp.preprocess_text)
        duplicates = questions_normalized[questions_normalized.duplicated()]
        self.assertEqual(len(duplicates), 0, f"Found duplicate questions in dataset: {duplicates.tolist()}")

    def test_module_convenience_function(self):
        """Verify the module-level find_best_faq function returns expected interface structure."""
        res = find_best_faq("What is the Right to Education under the Indian Constitution?")
        self.assertIsInstance(res, dict)
        expected_keys = [
            "matched", "similarity_score", "question", "answer", "topic",
            "act_name", "section", "source_title", "source_url",
            "intent", "extracted_legal_references", "requires_ai_generation"
        ]
        for key in expected_keys:
            self.assertIn(key, res, f"Expected key {key} missing from result dictionary")
        self.assertTrue(res["matched"])
        self.assertEqual(res["section"], "Article 21A")


if __name__ == "__main__":
    unittest.main()
