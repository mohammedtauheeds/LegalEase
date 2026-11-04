"""
LegalEase - Unified Legal Search & Retrieval Service.
File: services/legal_search.py

Coordinates retrieval across:
1. NLP-based FAQ matching (data/legal_faq.csv via models/legal_nlp.py)
2. Verified statutory provisions (services/legal_api_service.py & local store)
3. Court judgments (Courts & Cases API via services/legal_api_service.py)
4. Authoritative Indian Government and judicial portals (India Code, SCI, NALSA)

Performs source deduplication, relevance ranking, context trimming, and status tracking.
"""

import logging
from typing import Any, Dict, List, Optional

from config import Config
from models.legal_nlp import find_best_faq
from services.legal_api_service import (
    get_statute,
    retrieve_legal_context,
    search_judgments,
    SUPPORTED_ACTS,
)
from services.comprehensive_retrieval import retrieve_statutory_corpus
from services.source_verification import format_provision_label

logger = logging.getLogger("legalease.legal_search")


def normalize_source_entry(
    title: str,
    source_type: str,
    url: str,
    act_name: Optional[str] = None,
    section: Optional[str] = None,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """Create a standardized, clean source attribution entry."""
    return {
        "title": title.strip() if title else "Official Indian Legal Portal",
        "type": source_type.strip() if source_type else "Government Resource",
        "url": url.strip() if url else "https://www.indiacode.nic.in/",
        "act_name": act_name.strip() if act_name else None,
        "section": section.strip() if section else None,
        "status": status.strip() if status else None
    }


def deduplicate_sources(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate source references based on normalized Title and URL."""
    unique_sources = []
    seen_urls = set()
    seen_titles = set()

    for s in sources:
        raw_url = (s.get("url") or s.get("source_url") or "").strip()
        raw_title = (s.get("title") or "").strip().lower()
        if not raw_url and not raw_title:
            continue
        norm_url = raw_url.lower().rstrip("/")
        if (norm_url and norm_url in seen_urls) or (raw_title and raw_title in seen_titles):
            continue
        if norm_url:
            seen_urls.add(norm_url)
        if raw_title:
            seen_titles.add(raw_title)
        s_copy = dict(s)
        s_copy["url"] = raw_url or "https://www.indiacode.nic.in/"
        unique_sources.append(s_copy)

    return unique_sources


def search_legal_information(user_question: str, limit: int = 5) -> Dict[str, Any]:
    """
    Unified legal retrieval function.
    Coordinates FAQ similarity matching, statutory provision lookup,
    and court judgment searches into a normalized payload.

    Returns:
    {
        "success": bool,
        "query": str,
        "faq_results": list,
        "statutes": list,
        "judgments": list,
        "sources": list,
        "retrieval_status": {
            "faq_available": bool,
            "statutes_available": bool,
            "judgments_available": bool,
            "external_api_used": bool
        },
        "errors": list
    }
    """
    errors = []

    # 1. Input Validation
    if not user_question or not isinstance(user_question, str) or not user_question.strip():
        return {
            "success": False,
            "query": "",
            "faq_results": [],
            "statutes": [],
            "judgments": [],
            "sources": [],
            "retrieval_status": {
                "faq_available": False,
                "statutes_available": False,
                "judgments_available": False,
                "external_api_used": False
            },
            "errors": ["User question must be a non-empty string."]
        }

    clean_query = user_question.strip()
    if len(clean_query) > 500:
        clean_query = clean_query[:500]

    raw_sources: List[Dict[str, Any]] = []

    # 2. Phase 4: NLP FAQ Matching
    faq_results = []
    faq_available = False
    try:
        faq_match = find_best_faq(clean_query)
        faq_results.append(faq_match)
        if faq_match.get("similarity_score", 0.0) > 0.0 or faq_match.get("matched"):
            faq_available = True

        if faq_match.get("source_url"):
            raw_sources.append(normalize_source_entry(
                title=faq_match.get("source_title") or f"{faq_match.get('act_name')} Resource",
                source_type="FAQ / Government Resource",
                url=faq_match.get("source_url"),
                act_name=faq_match.get("act_name"),
                section=faq_match.get("section")
            ))
    except Exception as e:
        logger.error(f"FAQ retrieval error: {e}")
        errors.append(f"FAQ retrieval error: {str(e)}")

    # 3. Phase 5: High-Level Legal Context & Statutory Retrieval
    statutes = []
    statutes_available = False
    judgments = []
    judgments_available = False
    external_api_used = False

    try:
        context_payload = retrieve_legal_context(clean_query)
        retrieved_stats = context_payload.get("retrieved_statutes", [])

        # Limit statutes to top 3 to keep token budget optimal
        for st in retrieved_stats[:3]:
            statutes.append({
                "act_slug": st.get("act_slug", ""),
                "act_name": st.get("act_name", ""),
                "section": st.get("section", ""),
                "heading": st.get("heading", ""),
                "text": st.get("text", "")[:600],  # Trim long provisions
                "status": st.get("status", ""),
                "corresponding_provision": st.get("corresponding_provision"),
                "source_title": st.get("source_title", "India Code"),
                "source_url": st.get("source_url", "https://www.indiacode.nic.in/")
            })
            st_title = format_provision_label(st.get("act_name", ""), st.get("section", ""))
            raw_sources.append(normalize_source_entry(
                title=st_title,
                source_type="Official Legislation",
                url=st.get("source_url", "https://www.indiacode.nic.in/"),
                act_name=st.get("act_name"),
                section=st.get("section"),
                status=st.get("status")
            ))

        if statutes:
            statutes_available = True

        # Process retrieved judgments (only if genuinely returned from external API)
        retrieved_judgs = context_payload.get("retrieved_judgments", [])
        for jg in retrieved_judgs[:limit]:
            if jg.get("title") and jg.get("title") != "Untitled Judgment":
                judgments.append({
                    "case_id": jg.get("case_id", ""),
                    "title": jg.get("title", ""),
                    "court": jg.get("court", "Indian Court"),
                    "decision_date": jg.get("decision_date", ""),
                    "citation": jg.get("citation", ""),
                    "url": jg.get("url", "https://www.sci.gov.in/"),
                    "summary": jg.get("summary", "")[:400]
                })
                raw_sources.append(normalize_source_entry(
                    title=f"{jg.get('title')} ({jg.get('court')})",
                    source_type="Court Judgment",
                    url=jg.get("url", "https://www.sci.gov.in/")
                ))

        if judgments:
            judgments_available = True
            external_api_used = True

    except Exception as e:
        logger.error(f"Statutory and judgment context retrieval error: {e}")
        errors.append(f"Legal API retrieval error: {str(e)}")

    # 4. Universal Statutory Corpus Retrieval (FTS5 across Central, State & Constitutional Corpus)
    jurisdiction_info = {"jurisdiction": "Central", "is_state_specific": False}
    seventh_schedule = None
    constitutional_article = None
    state_statutes = []
    corpus_results = []

    try:
        corpus_data = retrieve_statutory_corpus(clean_query, limit=5)
        jurisdiction_info = corpus_data.get("jurisdiction_info", jurisdiction_info)
        seventh_schedule = corpus_data.get("seventh_schedule")
        constitutional_article = corpus_data.get("constitutional_article")
        state_statutes = corpus_data.get("state_statutes", [])
        corpus_results = corpus_data.get("fts_results", [])

        # Add official source attributions for corpus results with domain relevance filtering
        lower_q = clean_query.lower()
        for fts_item in corpus_results:
            act_n = fts_item.get('act_name', '')
            sec_n = fts_item.get('section', '')
            formatted_title = format_provision_label(act_n, sec_n) if act_n else fts_item.get('title', '')

            raw_sources.append(normalize_source_entry(
                title=formatted_title,
                source_type="Official Legislation",
                url="https://www.indiacode.nic.in/",
                act_name=act_n,
                section=sec_n,
                status="In Force"
            ))

        if constitutional_article:
            raw_sources.insert(0, normalize_source_entry(
                title=f"Constitution of India, Article {constitutional_article.get('article_number')}",
                source_type="Constitutional Authority",
                url=constitutional_article.get("official_url", "https://legislative.gov.in/constitution-of-india/"),
                act_name="Constitution of India",
                section=f"Article {constitutional_article.get('article_number')}",
                status="In Force"
            ))

    except Exception as e:
        logger.error(f"Comprehensive corpus retrieval error: {e}")
        errors.append(f"Comprehensive corpus retrieval error: {str(e)}")

    # 5. Fallback baseline sources if no sources collected
    if not raw_sources:
        raw_sources.append(normalize_source_entry(
            title="India Code - Digital Repository of All Central and State Acts",
            source_type="Official Portal",
            url="https://www.indiacode.nic.in/"
        ))

    # 6. Deduplicate sources
    clean_sources = deduplicate_sources(raw_sources)

    return {
        "success": True,
        "query": clean_query,
        "faq_results": faq_results,
        "statutes": statutes,
        "judgments": judgments,
        "sources": clean_sources,
        "corpus_results": corpus_results,
        "jurisdiction_info": jurisdiction_info,
        "seventh_schedule": seventh_schedule,
        "constitutional_article": constitutional_article,
        "state_statutes": state_statutes,
        "retrieval_status": {
            "faq_available": faq_available,
            "statutes_available": statutes_available,
            "judgments_available": judgments_available,
            "external_api_used": external_api_used
        },
        "errors": errors
    }
