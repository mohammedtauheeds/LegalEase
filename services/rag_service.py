"""
LegalEase - Retrieval-Augmented Generation (RAG) Orchestration Service.
File: services/rag_service.py

Orchestrates the complete hybrid legal awareness answering pipeline:
1. Input sanitization & prompt injection guardrails
2. Intent & conversational routing (greetings / off-topic deflection)
3. Verified FAQ similarity matching (Phase 4)
4. Context-grounded statutory & case law retrieval (Phase 5 via services/legal_search.py)
5. Gemini Flash context generation with strict legal safeguards (Phase 6)
6. Zero-downtime offline fallback using verified local statutory data
7. Authoritative source normalization & deduplication
"""

import logging
import re
from typing import Any, Dict, List, Optional

from config import Config
from services.gemini_service import (
    generate_legal_answer,
    get_gemini_service,
)
from services.legal_search import (
    deduplicate_sources,
    normalize_source_entry,
    search_legal_information,
)
from services.source_verification import format_provision_label

logger = logging.getLogger("legalease.rag_service")


def generate_rag_response(
    user_question: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Main RAG pipeline entry point.
    Coordinates question evaluation, FAQ confidence routing, statutory retrieval,
    and Gemini generation to produce grounded, legally responsible answers.

    Returns:
    {
        "success": bool,
        "answer": str,
        "sources": list,
        "retrieval": dict,
        "model": str | None,
        "fallback_used": bool,
        "error": str | None
    }
    """
INDEPENDENT_DOMAIN_KEYWORDS = {
    # Labour & Employment
    "salary", "wages", "wage", "employer", "employee", "unpaid", "bonus", "gratuity", "overtime", "pf", "esi",
    # Tenancy & Property
    "landlord", "tenant", "tenancy", "eviction", "evict", "rent", "lease", "rent agreement",
    # Family & Matrimonial
    "wife", "husband", "marriage", "divorce", "maintenance", "alimony", "child custody", "custody",
    # Consumer & Goods
    "defective", "phone", "mobile", "laptop", "product", "warranty", "refund", "consumer",
    # Criminal & Police
    "arrest", "police", "fir", "warrant",
    # Traffic
    "challan", "licence", "license", "helmet", "traffic police",
    # Cyber
    "cyber", "otp", "phishing", "scam", "upi fraud",
    # Cheque
    "cheque bounce", "bounced cheque",
    # Education
    "marksheet", "degree certificate", "ragging", "school fee",
    # Healthcare
    "hospital", "treatment deposit", "clinical"
}

GENUINE_FOLLOW_UP_PATTERNS = [
    r"^(what\s+if|what\s+about|and\s+if|what\s+then|what\s+next)\b",
    r"^(can\s+(they|he|she|police|court)\s+(do\s+that|refuse|arrest))\b",
    r"\b(refuse\s+to\s+register\s+(it|this)|file\s+(it|this)|appeal\s+against\s+(this|it)|penalty\s+for\s+(that|this))\b",
    r"\b(in\s+that\s+case|after\s+that|how\s+to\s+do\s+that|if\s+so|if\s+not)\b",
    r"\b(what\s+if\s+(the\s+offence\s+is\s+)?(bailable|non-bailable))\b",
    r"\b(how\s+long\s+does\s+it\s+take|where\s+should\s+i\s+go)\b"
]


def contextualize_query(user_question: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Expand conversational follow-up questions with the core legal topic from previous turns.
    Strictly ensures independent new questions are NEVER polluted with previous turn queries.
    """
    if not conversation_history or not user_question:
        return user_question

    clean_q = user_question.strip()
    lower_q = clean_q.lower()

    # If user query introduces its own distinct substantive legal subject, it is NOT a follow-up
    has_own_legal_subject = any(
        re.search(r"\b" + re.escape(kw) + r"\b", lower_q) for kw in INDEPENDENT_DOMAIN_KEYWORDS
    )

    is_followup_pattern = any(re.search(pat, lower_q) for pat in GENUINE_FOLLOW_UP_PATTERNS)

    # A query is a follow-up ONLY if it matches a genuine follow-up pattern and lacks an independent subject
    # (Exception: phrases like "refuse to register it" can have "police" but clearly refer to prior turn's "FIR")
    is_genuine_followup = is_followup_pattern and (
        not has_own_legal_subject or any(p in lower_q for p in ["register it", "refuse it", "do that", "for that", "is that", "in that case", "if it is bailable"])
    )

    if not is_genuine_followup:
        return user_question

    prev_user_queries = [
        m.get("content", "").strip()
        for m in conversation_history
        if m.get("role") in ("user", "citizen") and m.get("content", "").strip()
    ]
    if not prev_user_queries:
        return user_question

    last_query = prev_user_queries[-1]
    last_cleaned = re.sub(r'[^\w\s]', ' ', last_query).strip()

    # Extract primary noun/subject from previous query rather than full raw sentence
    prev_keywords = [
        kw for kw in INDEPENDENT_DOMAIN_KEYWORDS
        if re.search(r"\b" + re.escape(kw) + r"\b", last_query.lower())
    ]
    if prev_keywords:
        subject_anchor = prev_keywords[0].upper() if prev_keywords[0] in ("fir", "otp", "bns", "bnss", "cpc", "crpc", "ipc") else prev_keywords[0].title()
        return f"{subject_anchor} {clean_q}"

    return f"{last_cleaned} {clean_q}"


def generate_rag_response(
    user_question: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Primary interface for RAG-based legal question answering.
    Orchestrates FAQ similarity, statutory search, judgment lookup,
    and grounded generation via Gemini API.

    Returns:
    {
        "success": bool,
        "answer": str,
        "sources": list,
        "retrieval": dict,
        "model": str | None,
        "fallback_used": bool,
        "error": str | None
    }
    """
    gemini_svc = get_gemini_service()

    # 1. Input Validation & Prompt Injection Defense
    is_valid, validation_err = gemini_svc.validate_user_input(user_question)
    if not is_valid:
        return {
            "success": False,
            "answer": validation_err,
            "sources": [normalize_source_entry(
                title="India Code - Digital Repository of All Central and State Acts",
                source_type="Official Portal",
                url="https://www.indiacode.nic.in/"
            )],
            "retrieval": {
                "faq_available": False,
                "statutes_available": False,
                "judgments_available": False,
                "external_api_used": False
            },
            "model": None,
            "fallback_used": False,
            "error": validation_err
        }

    clean_question = user_question.strip()
    search_query = contextualize_query(clean_question, conversation_history)

    # 2. Execute Unified Legal Search (Phase 4 FAQ + Phase 5 Statutes & Cases)
    search_res = search_legal_information(search_query)
    retrieval_status = search_res.get("retrieval_status", {})
    faq_matches = search_res.get("faq_results", [])
    top_faq = faq_matches[0] if faq_matches else {}

    intent = top_faq.get("intent", "general_legal_inquiry")

    # 3. Conversational / Intent Short-Circuiting
    # A. Greeting Intent
    if intent == "greeting":
        return {
            "success": True,
            "answer": top_faq.get("answer", (
                "Namaste! I am LegalEase, your Indian Legal Awareness Assistant. "
                "How can I help you understand your legal rights or Indian laws today?"
            )),
            "sources": search_res.get("sources", []),
            "retrieval": retrieval_status,
            "model": "rule_based_intent_handler",
            "fallback_used": False,
            "error": None
        }

    # B. Non-Legal Off-Topic Intent
    if intent == "non_legal":
        return {
            "success": True,
            "answer": top_faq.get("answer", (
                "LegalEase is dedicated to providing awareness regarding Indian laws, fundamental rights, "
                "and legal procedures. I do not answer general non-legal questions. Please ask an Indian law-related question."
            )),
            "sources": [normalize_source_entry(
                title="LegalEase Indian Legal Awareness Platform",
                source_type="Informational Resource",
                url="https://www.indiacode.nic.in/"
            )],
            "retrieval": retrieval_status,
            "model": "rule_based_intent_handler",
            "fallback_used": False,
            "error": None
        }

    # 4. FAQ Confidence Routing
    # If high similarity FAQ match exists (score >= threshold) and does not require AI generation
    if top_faq.get("matched") and not top_faq.get("requires_ai_generation"):
        logger.info(f"FAQ confidence match ({top_faq.get('similarity_score')}). Serving verified FAQ directly.")
        
        faq_ans = top_faq.get("answer", "").strip()
        act_name = top_faq.get("act_name", "Indian Legal Framework")
        section = top_faq.get("section", "")
        source_title = top_faq.get("source_title", "Official Legal Portal")
        source_url = top_faq.get("source_url", "https://www.indiacode.nic.in/")
        topic = top_faq.get("topic", "General Legal Inquiry")

        sec_label = format_provision_label(act_name, section)

        # Tailor specific remedies and conditions based on detected intent
        if "fir" in clean_question.lower() or "police" in clean_question.lower():
            remedy_text = (
                "• Send the complaint in writing by post to the Superintendent of Police under Section 173(4) BNSS.\n"
                "• File an application before the Judicial Magistrate under Section 175(3) BNSS.\n"
                "• Approach the High Court under Section 528 BNSS (former 482 CrPC) or Article 226 for appropriate directions."
            )
            rights_text = (
                "• Right to have an FIR registered for any cognizable offence without unlawful refusal.\n"
                "• Statutory right to obtain a free signed copy of the FIR under Section 173(2) BNSS.\n"
                "• Right to register a Zero FIR at any police station regardless of jurisdiction."
            )
        elif intent == "report_cybercrime" or "cyber" in clean_question.lower():
            remedy_text = (
                "• Call 1930 immediately to alert Indian Cyber Crime Coordination Centre (I4C).\n"
                "• File a complaint on the National Cyber Crime Reporting Portal at cybercrime.gov.in.\n"
                "• File an FIR at the jurisdictional Cyber Crime Police Station."
            )
            rights_text = (
                "• Right to emergency banking freeze assistance via 1930 within the 'golden hour'.\n"
                "• Limited liability for unauthorized electronic transactions reported within 3 days as per RBI directives."
            )
        elif intent == "consumer_grievance" or "consumer" in clean_question.lower():
            remedy_text = (
                "• Dial 1915 for National Consumer Helpline or submit grievance on consumerhelpline.gov.in.\n"
                "• File an online consumer complaint via e-Daakhil (edaakhil.nic.in) before the District Consumer Commission."
            )
            rights_text = (
                "• Right to be protected against unfair trade practices and substandard goods.\n"
                "• Right to claim full refund, replacement, damages, and litigation costs."
            )
        else:
            remedy_text = (
                f"• Approach the competent statutory authority, commissioner, or court under {act_name}.\n"
                "• Issue a formal Legal Notice demanding compliance or dispute resolution.\n"
                "• Contact the District Legal Services Authority (DLSA) or dial 15100 for free legal assistance."
            )
            rights_text = (
                "• Right to fair procedure, natural justice, and equal protection of the laws.\n"
                f"• Right to claim statutory protections and remedies under {act_name}.\n"
                "• Right to free legal aid under Section 12 of the Legal Services Authorities Act, 1987 for eligible persons."
            )

        # Assemble Standardized 8 Sections
        sections = [
            f"### Direct Answer\n{faq_ans}\n",
            f"### Relevant Law\n• {sec_label} [Current / Verified Law | Source: {source_url}]\n",
            f"### Explanation in Simple English\n{faq_ans}\n\nThis provision sets out the statutory procedure, standards, and legal protections under Indian law.\n",
            f"### Conditions and Exceptions\nStatutory requirements, jurisdictional criteria, and limitation periods under Indian law must be satisfied before instituting formal legal proceedings.\n",
            f"### Rights of the Person\n{rights_text}\n",
            f"### Available Remedies\n{remedy_text}\n",
            f"### Practical Next Steps\n1. Collate all written agreements, receipts, communications, or police complaints.\n2. Verify the applicable forum, territorial jurisdiction, and limitation period.\n3. Contact the National Legal Aid Helpline at 15100 or consult an advocate in your jurisdiction.\n",
            f"### Relevant Judicial Decisions\nNo verified judicial decisions were found for this query.\n",
            f"### Sources\n• {source_title}: {source_url}"
        ]

        # Add emergency helpline notice if applicable
        if intent == "report_cybercrime" or "cyber" in clean_question.lower():
            sections.append("\n**Emergency Helpline:** Dial **1930** (National Cyber Crime Helpline) or report online at [cybercrime.gov.in](https://cybercrime.gov.in/).")
        elif intent == "consumer_grievance" or "consumer" in clean_question.lower():
            sections.append("\n**Consumer Grievance:** Dial **1915** (National Consumer Helpline) or visit [consumerhelpline.gov.in](https://consumerhelpline.gov.in/).")
        elif intent == "find_legal_aid":
            sections.append("\n**Free Legal Aid:** Call NALSA helpline **15100** or visit [nalsa.gov.in](https://nalsa.gov.in/).")
        elif intent == "women_protection":
            sections.append("\n**Women's Helplines:** Dial **1091** (Women in Distress), **181** (Domestic Abuse), or **112** (Pan-India Emergency).")
        elif intent == "child_protection_pocso":
            sections.append("\n**Child Protection:** Dial **1098** (Childline) or **112** (Pan-India Emergency).")
        elif intent == "senior_citizen_welfare":
            sections.append("\n**Senior Citizen Helpline:** Dial **14567** (Elderline) for welfare assistance.")
        elif intent == "education_student_rights" and "ragging" in clean_question.lower():
            sections.append("\n**Anti-Ragging Helpline:** Call **1800-180-5522** or report online at [antiragging.in](https://www.antiragging.in/).")

        sections.append("\n*(Notice: Public legal awareness response synthesized from verified Indian statutory provisions and authoritative government records.)*")
        sections.append(f"\n*Note: {Config.LEGAL_DISCLAIMER}*")

        answer_text = "\n".join(sections)

        return {
            "success": True,
            "answer": answer_text,
            "sources": search_res.get("sources", []),
            "retrieval": retrieval_status,
            "model": "local_faq_dataset",
            "fallback_used": False,
            "error": None
        }

    # 5. Low FAQ Confidence: Forward to RAG + Gemini AI Generation
    logger.info("FAQ confidence insufficient or novel legal question. Invoking Gemini AI.")
    
    # Combine standard statutes with FTS corpus provisions & constitutional article (with strict deduplication)
    combined_statutes = list(search_res.get("statutes", []))
    existing_headings = {s.get("heading", "").lower().strip() for s in combined_statutes}
    existing_keys = {
        (s.get("act_name", "").lower().strip(), str(s.get("section", "")).lower().strip())
        for s in combined_statutes
        if s.get("act_name")
    }

    if search_res.get("constitutional_article"):
        ca = search_res["constitutional_article"]
        ca_heading = ca.get("title", "").lower().strip()
        ca_sec = f"Article {ca.get('article_number')}".lower().strip()
        if ca_heading not in existing_headings and ("constitution of india", ca_sec) not in existing_keys:
            combined_statutes.insert(0, {
                "act_slug": "constitution",
                "act_name": "Constitution of India",
                "section": f"Article {ca.get('article_number')}",
                "heading": ca.get("title", ""),
                "text": ca.get("extract", "")[:600],
                "status": "In Force",
                "corresponding_provision": ca.get("seventh_schedule_list"),
                "source_title": "Constitution of India",
                "source_url": ca.get("official_url", "https://legislative.gov.in/constitution-of-india/")
            })
            existing_headings.add(ca_heading)
            existing_keys.add(("constitution of india", ca_sec))

    lower_sq = search_query.lower()
    for fts_item in search_res.get("corpus_results", []):
        act_n = fts_item.get("act_name", "")
        sec_n = fts_item.get("section", "")
        h = fts_item.get("title", "")
        h_lower = h.lower().strip()
        item_key = (act_n.lower().strip(), str(sec_n).lower().strip())

        # If already present, enrich missing text if needed
        if item_key in existing_keys or h_lower in existing_headings:
            for s in combined_statutes:
                if (s.get("act_name", "").lower().strip() == act_n.lower().strip() and str(s.get("section", "")).lower().strip() == str(sec_n).lower().strip()):
                    if not s.get("text") or str(s.get("text")).lower() in ("none", "null"):
                        s["text"] = fts_item.get("content", "")[:600]
            continue

        item_text = fts_item.get("content", "")
        if not item_text or item_text.strip().lower() in ("none", "null"):
            item_text = h

        combined_statutes.append({
            "act_slug": fts_item.get("domain", "central_act"),
            "act_name": act_n,
            "section": sec_n,
            "heading": h,
            "text": item_text[:600],
            "status": "In Force",
            "corresponding_provision": f"Jurisdiction: {fts_item.get('jurisdiction', 'Central')}",
            "source_title": act_n if act_n else "India Code",
            "source_url": "https://www.indiacode.nic.in/"
        })
        existing_headings.add(h_lower)
        if sec_n:
            existing_keys.add(item_key)

    # Construct normalized legal context payload for Gemini
    legal_context = {
        "retrieved_statutes": combined_statutes,
        "retrieved_judgments": search_res.get("judgments", []),
        "nlp_analysis": top_faq,
        "jurisdiction_info": search_res.get("jurisdiction_info"),
        "seventh_schedule": search_res.get("seventh_schedule"),
        "state_statutes": search_res.get("state_statutes", []),
        "authoritative_sources": Config.OFFICIAL_LEGAL_SOURCES
    }

    # Call Gemini service (Phase 6)
    gemini_res = generate_legal_answer(
        user_question=clean_question,
        legal_context=legal_context,
        conversation_history=conversation_history
    )

    # Merge and deduplicate sources
    all_sources = search_res.get("sources", []) + gemini_res.get("sources", [])
    deduped_sources = deduplicate_sources(all_sources)

    # Return standard response
    return {
        "success": gemini_res.get("success", False),
        "answer": gemini_res.get("answer", "No answer could be generated."),
        "sources": deduped_sources,
        "retrieval": retrieval_status,
        "model": gemini_res.get("model", Config.GEMINI_MODEL),
        "fallback_used": gemini_res.get("fallback_used", False),
        "error": gemini_res.get("error")
    }
