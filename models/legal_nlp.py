"""
LegalEase - Natural Language Processing & FAQ Matching Engine
Implements text normalization, TF-IDF vectorization, cosine similarity,
legal reference extraction, and intent classification against verified legal FAQs.
"""

import re
import string
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import Config

# Module-level singleton instance
_NLP_ENGINE_INSTANCE = None


class LegalNLP:
    """Intelligent NLP processor for Indian Legal Awareness queries."""

    def __init__(self, dataset_path: Optional[Path] = None, threshold: Optional[float] = None):
        """
        Initialize the NLP engine, load dataset, and build the TF-IDF index once.
        """
        self.dataset_path = dataset_path or Config.FAQ_DATASET_PATH
        self.threshold = threshold if threshold is not None else Config.NLP_SIMILARITY_THRESHOLD
        
        self.df: pd.DataFrame = pd.DataFrame()
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.faq_vectors: Optional[np.ndarray] = None
        
        # Load dataset and train vectorizer immediately
        self._load_dataset()
        self._build_vectorizer()

    def _load_dataset(self) -> None:
        """Load and sanitize the FAQ dataset."""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Legal FAQ dataset not found at: {self.dataset_path}")

        df = pd.read_csv(self.dataset_path, encoding="utf-8")
        
        # Safe column defaults and fillna
        expected_cols = [
            "id", "question", "answer", "topic", "act_name",
            "section", "source_title", "source_url"
        ]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""
            df[col] = df[col].fillna("").astype(str)

        self.df = df

    def preprocess_text(self, text: str) -> str:
        """
        Normalize input text: lowercase, remove special characters while
        preserving essential alphanumeric and legal symbols.
        """
        if not text or not isinstance(text, str):
            return ""

        text = text.lower().strip()
        # Normalize punctuation except hyphens and parentheses inside section numbers
        text = re.sub(r"[^\w\s\(\)\-]", " ", text)
        # Collapse multiple whitespaces
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _build_vectorizer(self) -> None:
        """Fit the TF-IDF vectorizer on the preprocessed FAQ questions."""
        if self.df.empty:
            raise ValueError("Cannot initialize TF-IDF vectorizer on an empty dataset.")

        preprocessed_questions = [
            self.preprocess_text(q) for q in self.df["question"].tolist()
        ]

        # Use unigrams and bigrams with sublinear TF scaling
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True
        )
        self.faq_vectors = self.vectorizer.fit_transform(preprocessed_questions)

    def extract_legal_references(self, text: str) -> List[Dict[str, str]]:
        """
        Extract statutory sections, constitutional articles, and Act names from text.
        Identifies IPC, BNS, CrPC, BNSS, IEA, BSA, CPC, RTI, and Constitution.
        """
        references = []
        if not text or not isinstance(text, str):
            return references

        lower_text = text.lower()

        # 1. Constitutional Articles and Parts (e.g. Article 21, Article 32, Art 51A, Fundamental Rights)
        article_matches = re.findall(
            r"\b(?:article|art\.?)\s*(\d+[a-z]?)\b", text, re.IGNORECASE
        )
        for art in article_matches:
            references.append({
                "act": "Constitution of India",
                "provision_type": "Article",
                "number": art.upper(),
                "slug": "constitution"
            })

        if "fundamental right" in lower_text:
            if not any("part3" in r.get("number", "").lower() for r in references):
                references.append({
                    "act": "Constitution of India",
                    "provision_type": "Part",
                    "number": "part3",
                    "slug": "constitution"
                })

        if "common law" in lower_text or "stare decisis" in lower_text:
            if not any(r.get("number") == "141" for r in references):
                references.append({
                    "act": "Constitution of India",
                    "provision_type": "Article",
                    "number": "141",
                    "slug": "constitution"
                })

        # 2. Sections with specific Act designations across all major Indian laws
        act_patterns = [
            (r"\b(?:(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?bns|bns\s*(?:section\s*)?(\d+[a-z]?))\b", "Bharatiya Nyaya Sanhita, 2023", "bns"),
            (r"\b(?:(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?ipc|ipc\s*(?:section\s*)?(\d+[a-z]?))\b", "Indian Penal Code, 1860 (superseded by BNS)", "ipc"),
            (r"\b(?:(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?bnss|bnss\s*(?:section\s*)?(\d+[a-z]?))\b", "Bharatiya Nagarik Suraksha Sanhita, 2023", "bnss"),
            (r"\b(?:(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?crpc|crpc\s*(?:section\s*)?(\d+[a-z]?))\b", "Code of Criminal Procedure, 1973 (superseded by BNSS)", "crpc"),
            (r"\b(?:(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?bsa|bsa\s*(?:section\s*)?(\d+[a-z]?))\b", "Bharatiya Sakshya Adhiniyam, 2023", "bsa"),
            (r"\b(?:(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?iea|iea\s*(?:section\s*)?(\d+[a-z]?))\b", "Indian Evidence Act, 1872 (superseded by BSA)", "iea"),
            (r"\b(?:(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?cpc|cpc\s*(?:section\s*)?(\d+[a-z]?))\b", "Code of Civil Procedure, 1908", "cpc"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?rti(?:\s+act)?\b", "Right to Information Act, 2005", "rti_act"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?(?:ni|negotiable\s+instruments)\s+act\b", "Negotiable Instruments Act, 1881", "ni_act"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?it\s+act\b", "Information Technology Act, 2000", "it_act"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?(?:cpa|consumer\s+protection\s+act)\b", "Consumer Protection Act, 2019", "cpa"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?(?:dv|pwdva|domestic\s+violence)\s+act\b", "Protection of Women from Domestic Violence Act, 2005", "dv_act"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?posh(?:\s+act)?\b", "Sexual Harassment of Women at Workplace Act, 2013", "posh"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?pocso(?:\s+act)?\b", "Protection of Children from Sexual Offences Act, 2012", "pocso"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?(?:sc\s*[\/-]?\s*st|atrocities)\s+act\b", "Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act, 1989", "sc_st_act"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?(?:poca|prevention\s+of\s+corruption\s+act)\b", "Prevention of Corruption Act, 1988", "poca"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?rera(?:\s+act)?\b", "Real Estate (Regulation and Development) Act, 2016", "rera"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?ibc\b", "Insolvency and Bankruptcy Code, 2016", "ibc"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?sarfaesi(?:\s+act)?\b", "SARFAESI Act, 2002", "sarfaesi"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?pmla(?:\s+act)?\b", "Prevention of Money Laundering Act, 2002", "pmla"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?(?:mv|motor\s+vehicles)\s+act\b", "Motor Vehicles Act, 1988", "mv_act"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?(?:contract\s+act|indian\s+contract\s+act)\b", "Indian Contract Act, 1872", "contract_act"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?hma\b", "Hindu Marriage Act, 1955", "hma"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?hsa\b", "Hindu Succession Act, 1956", "hsa"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?companies\s+act\b", "Companies Act, 2013", "companies_act"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?arbitration\s+act\b", "Arbitration and Conciliation Act, 1996", "arbitration_act"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?mediation\s+act\b", "Mediation Act, 2023", "mediation_act"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?dpdp(?:\s+act)?\b", "Digital Personal Data Protection Act, 2023", "dpdp"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?senior\s+citizens\s+act\b", "Maintenance and Welfare of Parents and Senior Citizens Act, 2007", "senior_citizens"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?maternity\s+benefit\s+act\b", "Maternity Benefit Act, 1961", "maternity_benefit"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?epa\b", "Environment (Protection) Act, 1986", "epa"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?ngt\s+act\b", "National Green Tribunal Act, 2010", "ngt_act"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?income\s+tax\s+act\b", "Income-tax Act, 1961", "it_tax_act"),
            (r"\b(?:section\s*)?(\d+[a-z]?)\s*(?:of\s+(?:the\s+)?)?(?:cgst|gst)\s+act\b", "Central Goods and Services Tax Act, 2017", "cgst_act"),
        ]

        for pattern, act_name, slug in act_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                sec = m if isinstance(m, str) else (m[0] or m[1] if len(m) > 1 else m[0])
                if sec and not any(r.get("number") == sec and r.get("slug") == slug for r in references):
                    references.append({
                        "act": act_name,
                        "provision_type": "Section",
                        "number": sec,
                        "slug": slug
                    })

        # 3. Famous Landmark Section Numbers & Colloquial References
        # Colloquial 420 case -> IPC 420 / BNS 318
        if re.search(r"\b420\b", lower_text) and not any(r.get("number") == "420" for r in references):
            references.append({
                "act": "Indian Penal Code, 1860 (superseded by BNS)",
                "provision_type": "Section",
                "number": "420",
                "slug": "ipc"
            })
            if not any(r.get("number") == "318" for r in references):
                references.append({
                    "act": "Bharatiya Nyaya Sanhita, 2023",
                    "provision_type": "Section",
                    "number": "318",
                    "slug": "bns"
                })

        # Cheque Bounce -> Section 138 NI Act
        if (re.search(r"\b138\b", lower_text) or any(w in lower_text for w in ["cheque bounce", "bounced cheque", "dishonour of cheque", "dishonor of cheque"])) and not any(r.get("number") == "138" for r in references):
            references.append({
                "act": "Negotiable Instruments Act, 1881",
                "provision_type": "Section",
                "number": "138",
                "slug": "ni_act"
            })

        # Murder -> BNS 103 / IPC 302
        if (re.search(r"\b302\b", lower_text) or "murder" in lower_text) and not any(r.get("number") in ("103", "302") for r in references):
            references.append({
                "act": "Bharatiya Nyaya Sanhita, 2023",
                "provision_type": "Section",
                "number": "103",
                "slug": "bns"
            })
            references.append({
                "act": "Indian Penal Code, 1860 (superseded by BNS)",
                "provision_type": "Section",
                "number": "302",
                "slug": "ipc"
            })

        # Anticipatory Bail -> BNSS 482 / CrPC 438
        if (re.search(r"\b438\b", lower_text) or "anticipatory bail" in lower_text) and not any(r.get("number") in ("482", "438") for r in references):
            references.append({
                "act": "Bharatiya Nagarik Suraksha Sanhita, 2023",
                "provision_type": "Section",
                "number": "482",
                "slug": "bnss"
            })

        # Maintenance -> BNSS 144 / CrPC 125
        if re.search(r"\b125\b", lower_text) and not any(r.get("number") in ("144", "125") for r in references):
            references.append({
                "act": "Bharatiya Nagarik Suraksha Sanhita, 2023",
                "provision_type": "Section",
                "number": "144",
                "slug": "bnss"
            })

        # General Theft -> BNS 303 / IPC 378
        if any(w in lower_text for w in ["theft", "stolen", "stealing"]) and "identity theft" not in lower_text:
            if not any(r.get("number") == "303" for r in references):
                references.append({
                    "act": "Bharatiya Nyaya Sanhita, 2023",
                    "provision_type": "Section",
                    "number": "303",
                    "slug": "bns"
                })
            if not any(r.get("number") == "378" for r in references):
                references.append({
                    "act": "Indian Penal Code, 1860 (superseded by BNS)",
                    "provision_type": "Section",
                    "number": "378",
                    "slug": "ipc"
                })

        # FIR -> BNSS 173 / CrPC 154
        if any(w in lower_text for w in ["fir", "zero fir", "e-fir"]) and not any(r.get("number") in ("173", "154") for r in references):
            references.append({
                "act": "Bharatiya Nagarik Suraksha Sanhita, 2023",
                "provision_type": "Section",
                "number": "173",
                "slug": "bnss"
            })

        # 4. Generic Section mentions (e.g. "section 138", "section 318")
        if not references:
            generic_sections = re.findall(r"\bsection\s*(\d+[a-z]?)\b", text, re.IGNORECASE)
            for sec in generic_sections:
                references.append({
                    "act": "Unspecified Statutory Provision",
                    "provision_type": "Section",
                    "number": sec,
                    "slug": "unknown"
                })

        return references

    def classify_intent(self, text: str) -> str:
        """
        Determine user intent from linguistic patterns and keywords.
        """
        if not text or not isinstance(text, str):
            return "empty_input"
        clean = self.preprocess_text(text)
        if not clean:
            return "empty_input"

        # Remove assistant self-reference name so "legalease" does not match "lease" or "legal"
        clean_no_name = re.sub(r"\blegalease\b", "", clean).strip()
        test_clean = clean_no_name if clean_no_name else clean

        # Check for non-legal greetings or common conversational phrases
        greetings = ["hello", "hi", "hey", "good morning", "good evening", "good afternoon", "who are you", "what can you do"]
        if test_clean in greetings or any(test_clean.startswith(g) for g in ["hello", "hi ", "hey "]):
            if not any(k in test_clean for k in ["law", "right", "crime", "court", "act", "section", "fir"]):
                return "greeting"

        # Check for non-legal domain questions
        off_topic_indicators = [
            "how to cook", "recipe", "weather today", "python code", "write a code",
            "stock price", "cricket score", "movie review", "what is the capital of",
            "bake a", "chocolate cake"
        ]
        if any(term in clean for term in off_topic_indicators):
            return "non_legal"

        # Specific legal intents across 35 Indian legal domains
        if any(term in test_clean for term in ["cyber", "online fraud", "phishing", "scam", "hacked", "1930", "financial fraud", "atm debit"]):
            return "report_cybercrime"

        if any(term in test_clean for term in ["cheque bounce", "bounced cheque", "138", "dishonour of cheque", "dishonor of cheque"]):
            return "cheque_bounce_inquiry"

        if any(term in test_clean for term in ["pocso", "child abuse", "minor child", "childline", "1098"]):
            return "child_protection_pocso"

        if any(term in test_clean for term in ["senior citizen", "elderly parent", "old age home", "14567", "elderline"]):
            return "senior_citizen_welfare"

        if any(term in test_clean for term in ["bribe", "corruption", "poca", "lokpal", "lokayukta", "vigilance", "trap case"]):
            return "anti_corruption_inquiry"

        if any(term in test_clean for term in ["sc/st", "atrocity", "caste abuse", "caste discrimination", "untouchability", "14566"]):
            return "sc_st_protection"

        if any(term in test_clean for term in ["medical negligence", "patient right", "medical bill", "hospital bill", "hospital", "dead body", "informed consent", "post-mortem", "clinical establishment"]):
            return "medical_patient_rights"

        if any(term in test_clean for term in ["traffic fine", "drunk driving", "challan", "mact", "accident claim", "hit and run"]):
            return "motor_accident_traffic"

        if any(term in test_clean for term in ["environment", "ngt", "pollution", "air quality", "tree cutting", "waste management"]):
            return "environmental_inquiry"

        if any(term in test_clean for term in ["bailable offence", "bailable", "right to bail"]):
            return "bailable_offence_rights"

        if any(term in test_clean for term in ["anticipatory bail", "pre-arrest bail"]):
            return "anticipatory_bail_inquiry"

        if any(term in test_clean for term in ["expired food", "unsafe food", "food adulteration", "adulterated", "fssai", "food safety", "food poisoning"]):
            return "food_safety_inquiry"

        if any(term in test_clean for term in ["blocking access", "easement", "right of way", "light and air", "neighbour construction", "blocking road"]):
            return "easement_property_dispute"

        if any(term in test_clean for term in ["salary", "unpaid salary", "withheld salary", "wages", "wage", "delayed wages", "pay cut", "stipend", "bonus", "gratuity", "provident fund", "epf", "retrenchment", "layoff", "minimum wage", "workman", "workplace compensation", "employee compensation"]):
            return "labour_employment_inquiry"

        if any(term in test_clean for term in ["anti-ragging", "ragging", "rte", "school fee", "student rights", "1800-180-5522", "original certificate", "original certificates", "marksheet", "degree certificate", "school refuse", "college refuse"]):
            return "education_student_rights"

        if any(term in test_clean for term in ["arbitration", "mediation", "arbitrator", "adr", "lok adalat"]):
            return "adr_mediation_inquiry"

        if any(term in test_clean for term in ["income tax", "itr", "gst", "advance tax", "tds", "input tax credit"]):
            return "taxation_citizens_rights"

        if any(term in test_clean for term in ["passport", "citizenship", "visa", "frro", "deportation", "oci"]):
            return "immigration_citizenship"

        if any(term in test_clean for term in ["fundamental right", "fundamental duties", "constitutional right", "right to equality", "right to life"]):
            return "understand_rights"

        if any(term in test_clean for term in ["fir", "zero fir", "e-fir", "police", "arrest", "bail", "investigation", "magistrate"]):
            return "police_complaint_fir"

        if any(term in test_clean for term in ["legal aid", "free lawyer", "nalsa", "dlsa", "tele-law", "lok adalat", "15100"]):
            return "find_legal_aid"

        if any(term in test_clean for term in ["women", "domestic violence", "posh", "sexual harassment", "matrimonial", "creche", "maternity", "1091", "181"]):
            return "women_protection"

        if any(term in test_clean for term in ["consumer", "defective", "seller", "refund", "e-daakhil", "forum", "1915", "warranty"]):
            return "consumer_grievance"

        if any(term in test_clean for term in ["tenant", "rent", "landlord", "evict", "security deposit", "repairs"]) or re.search(r"\blease\b", test_clean):
            return "tenant_rental"

        if any(term in test_clean for term in ["ancestral property", "will", "probate", "gift deed", "partition", "coparcener"]):
            return "property_inheritance_inquiry"

        if any(term in test_clean for term in ["incorporation", "board of directors", "director duties", "din", "nclt", "corporate social responsibility", "csr", "merger", "shareholder", "agm", "mca filing", "companies act"]) or ("company" in test_clean and any(k in test_clean for k in ["register", "incorporate", "shares", "board", "resolution", "winding up", "liquidation", "llp", "directors"])):
            return "corporate_business_law"

        if any(term in test_clean for term in ["common law", "stare decisis", "doctrine of precedent", "precedent"]):
            return "statutory_inquiry"

        if any(term in test_clean for term in ["theft", "stolen", "stealing", "robbery", "pickpocket"]):
            return "statutory_inquiry"

        if any(term in test_clean for term in ["cheating", "420", "defraud", "dishonestly inducing"]):
            return "statutory_inquiry"

        if any(term in test_clean for term in ["how to file", "procedure", "process", "time limit", "limitation", "notice", "appeal"]):
            return "understand_procedure"

        if any(term in test_clean for term in ["section ", "article ", "bns", "ipc", "bnss", "crpc", "bsa", "iea", "cpc"]):
            return "statutory_inquiry"

        return "general_legal_inquiry"

    def find_best_faq(self, user_question: str, threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Match a user query against the FAQ dataset using TF-IDF and Cosine Similarity.
        
        Returns a structured dictionary with match status, top FAQ details,
        similarity score, detected intent, and extracted legal references.
        """
        active_threshold = threshold if threshold is not None else self.threshold
        if user_question is None or not isinstance(user_question, str):
            user_question = ""
        clean_question = self.preprocess_text(user_question)

        intent = self.classify_intent(user_question)
        extracted_refs = self.extract_legal_references(user_question)

        # Handle empty or invalid input
        if not clean_question:
            return {
                "matched": False,
                "similarity_score": 0.0,
                "question": "",
                "answer": "Please ask a specific legal question to receive legal awareness information.",
                "topic": "None",
                "act_name": "",
                "section": "",
                "source_title": "",
                "source_url": "",
                "intent": intent,
                "extracted_legal_references": extracted_refs,
                "requires_ai_generation": False,
                "message": "Input is empty or whitespace only."
            }

        # Handle purely conversational greetings
        if intent == "greeting":
            return {
                "matched": False,
                "similarity_score": 0.0,
                "question": user_question,
                "answer": (
                    "Namaste! I am LegalEase, your AI-powered Indian Legal Awareness Assistant. "
                    "I can help you understand your fundamental rights, Indian criminal and civil laws, "
                    "cybercrime reporting, consumer protection, women's legal safeguards, and common legal procedures. "
                    "How can I assist you today?"
                ),
                "topic": "Indian Constitution",
                "act_name": "Constitution of India",
                "section": "",
                "source_title": "National Portal of India",
                "source_url": "https://www.india.gov.in/",
                "intent": intent,
                "extracted_legal_references": extracted_refs,
                "requires_ai_generation": False,
                "message": "Greeting handled directly."
            }

        # Handle non-legal off-topic questions
        if intent == "non_legal":
            return {
                "matched": False,
                "similarity_score": 0.0,
                "question": user_question,
                "answer": (
                    "LegalEase is dedicated to providing awareness and educational information regarding "
                    "Indian laws, fundamental rights, and legal procedures. I do not answer general or off-topic queries. "
                    "Please ask a question related to Indian legal topics."
                ),
                "topic": "None",
                "act_name": "",
                "section": "",
                "source_title": "LegalEase Legal Awareness System",
                "source_url": "https://www.indiacode.nic.in/",
                "intent": intent,
                "extracted_legal_references": extracted_refs,
                "requires_ai_generation": False,
                "message": "Non-legal query identified."
            }

        # Vectorize user input
        user_vector = self.vectorizer.transform([clean_question])

        # Compute cosine similarity against all FAQ questions + topics
        similarities = cosine_similarity(user_vector, self.faq_vectors).flatten().copy()

        # Guards against cross-topic misleading matches:
        # 1. FIR queries must only match FIR questions
        if re.search(r"\bfir\b", clean_question):
            for i, row in self.df.iterrows():
                if "fir" not in row["question"].lower():
                    similarities[i] *= 0.1

        # 2. General theft queries must not match identity theft
        if "theft" in clean_question and "identity" not in clean_question:
            for i, row in self.df.iterrows():
                if "identity theft" in row["question"].lower():
                    similarities[i] *= 0.1

        # 3. Common law is a doctrine outside the 100 FAQs
        if "common law" in clean_question:
            for i in range(len(similarities)):
                similarities[i] *= 0.1

        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])

        top_row = self.df.iloc[best_idx]

        # Determine if similarity qualifies as an authoritative FAQ match
        if best_score >= active_threshold:
            return {
                "matched": True,
                "similarity_score": round(best_score, 4),
                "question": top_row["question"],
                "answer": top_row["answer"],
                "topic": top_row["topic"],
                "act_name": top_row["act_name"],
                "section": top_row["section"],
                "source_title": top_row["source_title"],
                "source_url": top_row["source_url"],
                "intent": intent,
                "extracted_legal_references": extracted_refs,
                "requires_ai_generation": False,
                "message": f"Exact FAQ match found with confidence score {round(best_score, 4)}."
            }
        else:
            # Below threshold: do not return an unrelated FAQ answer to the user
            return {
                "matched": False,
                "similarity_score": round(best_score, 4),
                "question": user_question,
                "candidate_faq_question": top_row["question"],
                "answer": "",
                "topic": top_row["topic"] if best_score > 0.3 else "General Legal Inquiry",
                "act_name": top_row["act_name"] if best_score > 0.3 else "",
                "section": top_row["section"] if best_score > 0.3 else "",
                "source_title": top_row["source_title"],
                "source_url": top_row["source_url"],
                "intent": intent,
                "extracted_legal_references": extracted_refs,
                "requires_ai_generation": True,
                "message": f"No sufficiently high similarity match (score: {round(best_score, 4)} < threshold {active_threshold}). Forwarding to RAG/AI pipeline."
            }


def get_nlp_engine() -> LegalNLP:
    """Return or initialize the singleton LegalNLP instance."""
    global _NLP_ENGINE_INSTANCE
    if _NLP_ENGINE_INSTANCE is None:
        _NLP_ENGINE_INSTANCE = LegalNLP()
    return _NLP_ENGINE_INSTANCE


def find_best_faq(user_question: str, threshold: Optional[float] = None) -> Dict[str, Any]:
    """Convenience module function for easy RAG pipeline integration."""
    engine = get_nlp_engine()
    return engine.find_best_faq(user_question, threshold=threshold)
