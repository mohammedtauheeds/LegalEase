"""
LegalEase - Courts & Cases External API Service & Resilient Legal Retrieval Client.
Integrates with https://courtsandcases.com for:
1. Indian Court Judgment Search (/api/v1/search)
2. Case Details Retrieval (/api/v1/cases/{case_id})
3. Legal Citation Resolution (/api/v1/citations/resolve)
4. Statutory Section Retrieval (/api/v1/statutes/{act}/{section})

Features exponential backoff retry for transient errors, strict input validation,
statutory transition awareness (IPC/BNS, CrPC/BNSS, IEA/BSA), and an authoritative
fallback store referencing verified provisions and India Code.
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests

from config import Config
from models.legal_nlp import find_best_faq

logger = logging.getLogger("legalease.legal_api")

# Expanded central Act definitions and authoritative local statutory store (52 Central Acts, 100+ provisions)
from models.statutory_provisions import (
    SUPPORTED_ACTS,
    VERIFIED_STATUTE_FALLBACK,
    VERIFIED_LANDMARK_JUDGMENTS,
)


class CourtsAndCasesClient:
    """Client for the Courts & Cases API with resilience and statutory fallback."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, timeout: Optional[int] = None):
        self.base_url = (base_url or Config.COURTS_CASES_BASE_URL).rstrip("/")
        self.api_key = api_key if api_key is not None else Config.COURTS_CASES_API_KEY
        self.timeout = timeout if timeout is not None else Config.EXTERNAL_API_TIMEOUT
        self.session = requests.Session()
        
        # Default headers
        self.session.headers.update({
            "User-Agent": "LegalEase-Indian-Legal-Awareness-Bot/1.0",
            "Accept": "application/json",
        })
        # If API key is provided, attach Bearer auth
        if self.api_key and self.api_key.strip():
            self.session.headers["Authorization"] = f"Bearer {self.api_key.strip()}"

    def _execute_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None, retries: int = 2) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str], int]:
        """
        Execute an HTTP GET request with exponential backoff on transient errors.
        Returns: (success: bool, response_json: dict|None, error_message: str|None, status_code: int)
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Enforce HTTPS unless running on localhost for testing
        if not url.startswith("https://") and not ("127.0.0.1" in url or "localhost" in url):
            return False, None, "Security Violation: External API requests must use HTTPS.", 400

        attempt = 0
        last_error = None
        status_code = 0

        while attempt <= retries:
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                status_code = response.status_code

                # Success
                if status_code == 200:
                    try:
                        data = response.json()
                        return True, data, None, status_code
                    except Exception as e:
                        return False, None, f"Invalid JSON response from API: {str(e)}", status_code

                # Client errors (Do not retry 400, 401, 403, 404)
                if status_code in (400, 401, 403, 404):
                    msg = f"API returned HTTP {status_code}: {response.text[:200]}"
                    if status_code == 401:
                        msg = "Authentication failure: Invalid or missing API key."
                    elif status_code == 404:
                        msg = f"Requested resource not found at endpoint {endpoint}."
                    return False, None, msg, status_code

                # Transient server errors / rate limits (Retry 429, 500, 502, 503, 504)
                if status_code in (429, 500, 502, 503, 504):
                    last_error = f"HTTP {status_code} transient error"
                    if attempt < retries:
                        sleep_time = 0.5 * (2 ** attempt)
                        time.sleep(sleep_time)
                        attempt += 1
                        continue
                    else:
                        return False, None, f"API error after {retries} retries: {last_error}", status_code

                return False, None, f"Unexpected HTTP status {status_code}: {response.text[:200]}", status_code

            except requests.exceptions.Timeout as e:
                last_error = f"Request timed out after {self.timeout}s"
                if attempt < retries:
                    time.sleep(0.5 * (2 ** attempt))
                    attempt += 1
                    continue
                return False, None, f"Connection timeout: {last_error}", 408

            except requests.exceptions.ConnectionError as e:
                last_error = "Network connection failed or host unreachable"
                if attempt < retries:
                    time.sleep(0.5 * (2 ** attempt))
                    attempt += 1
                    continue
                return False, None, f"Connection error: {last_error}", 503

            except Exception as e:
                return False, None, f"Unexpected request exception: {str(e)}", 500

        return False, None, f"Request failed: {last_error}", status_code

    def search_judgments(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Endpoint A: Search Indian court judgments using natural-language queries.
        GET /api/v1/search?q={query}&limit=10
        """
        if not query or not isinstance(query, str) or not query.strip():
            return {
                "success": False,
                "data": None,
                "source": None,
                "fallback_used": False,
                "error": "Query parameter must be a non-empty string."
            }

        clean_query = query.strip()
        if len(clean_query) > 300:
            clean_query = clean_query[:300]

        clamped_limit = min(max(1, int(limit)), 10)
        params = {"q": clean_query, "limit": clamped_limit}

        success, data, error, status_code = self._execute_request("api/v1/search", params=params)

        if success and data:
            results = data.get("results") or data.get("data") or data.get("cases") or []
            formatted_judgments = []
            for item in results:
                formatted_judgments.append({
                    "case_id": item.get("case_id") or item.get("id", ""),
                    "title": item.get("title") or item.get("case_title", "Untitled Judgment"),
                    "court": item.get("court") or item.get("court_name", "Indian Court"),
                    "decision_date": item.get("decision_date") or item.get("date", ""),
                    "citation": item.get("citation") or item.get("neutral_citation", ""),
                    "url": item.get("url") or item.get("judgment_url", "https://www.sci.gov.in/"),
                    "summary": item.get("summary") or item.get("snippet", "")
                })

            return {
                "success": True,
                "data": {
                    "query": clean_query,
                    "count": len(formatted_judgments),
                    "judgments": formatted_judgments
                },
                "source": "courts_and_cases_api",
                "fallback_used": False,
                "error": None
            }

        # Fallback to local verified FAQ context if external API is unreachable
        return self._fallback_judgment_search(clean_query, error_reason=error)

    def _fallback_judgment_search(self, query: str, error_reason: Optional[str] = None) -> Dict[str, Any]:
        """Fallback when API is unavailable: matches verified landmark Supreme Court precedents."""
        faq_result = find_best_faq(query)
        lower_q = query.lower()

        matched_judgments = []
        if any(w in lower_q for w in ["arrest", "warrant", "custody", "handcuff"]):
            matched_judgments = list(VERIFIED_LANDMARK_JUDGMENTS.get("arrest_safeguards", []))
        elif any(w in lower_q for w in ["wife", "maintenance", "alimony", "spousal"]):
            matched_judgments = list(VERIFIED_LANDMARK_JUDGMENTS.get("maintenance_working_wife", []))
        elif any(w in lower_q for w in ["salary", "wage", "wages", "unpaid salary"]):
            matched_judgments = list(VERIFIED_LANDMARK_JUDGMENTS.get("unpaid_salary_wages", []))
        elif any(w in lower_q for w in ["defective", "warranty", "refund"]) and any(w in lower_q for w in ["phone", "mobile", "goods", "product", "laptop"]):
            matched_judgments = list(VERIFIED_LANDMARK_JUDGMENTS.get("defective_goods_consumer", []))
        elif any(w in lower_q for w in ["landlord", "tenant", "tenancy", "eviction"]):
            matched_judgments = list(VERIFIED_LANDMARK_JUDGMENTS.get("tenancy_eviction_safeguards", []))

        fallback_data = {
            "query": query,
            "count": len(matched_judgments),
            "judgments": matched_judgments,
            "fallback_context": {
                "matched_faq_topic": faq_result.get("topic", "General Legal Inquiry"),
                "faq_summary": faq_result.get("answer", ""),
                "official_portal_title": "Supreme Court of India (Official Portal)",
                "official_portal_url": "https://www.sci.gov.in/",
                "ecourts_portal_url": "https://ecourts.gov.in/"
            },
            "note": "Verified landmark Supreme Court precedents retrieved from authoritative legal records." if matched_judgments else "External judgment search is offline; no unverified judgments generated."
        }

        return {
            "success": True,
            "data": fallback_data,
            "source": "verified_landmark_store" if matched_judgments else "local_faq_fallback",
            "fallback_used": True,
            "error": error_reason
        }

    def get_case_details(self, case_id: str) -> Dict[str, Any]:
        """
        Endpoint B: Retrieve detailed information about a specific judgment.
        GET /api/v1/cases/{case_id}
        """
        if not case_id or not isinstance(case_id, str) or not case_id.strip():
            return {
                "success": False,
                "data": None,
                "source": None,
                "fallback_used": False,
                "error": "Case ID must be a valid, non-empty identifier."
            }

        clean_id = case_id.strip()
        # Input validation: case IDs are typically alphanumeric, hyphens, colons, or underscores
        if not re.match(r"^[A-Za-z0-9_\-\.:/]+$", clean_id) or len(clean_id) > 100:
            return {
                "success": False,
                "data": None,
                "source": None,
                "fallback_used": False,
                "error": "Invalid Case ID format. Must contain only alphanumeric characters, hyphens, colons, or underscores."
            }

        safe_endpoint = f"api/v1/cases/{quote(clean_id, safe='')}"
        success, data, error, status_code = self._execute_request(safe_endpoint)

        if success and data:
            c = data.get("case") or data.get("data") or data
            formatted = {
                "case_id": clean_id,
                "title": c.get("title") or c.get("case_title", "Unknown Title"),
                "court": c.get("court") or c.get("court_name", "Indian Judiciary"),
                "decision_date": c.get("decision_date") or c.get("date", ""),
                "case_number": c.get("case_number", ""),
                "judges": c.get("judges", []),
                "neutral_citation": c.get("neutral_citation", ""),
                "reported_citations": c.get("reported_citations", []),
                "outcome": c.get("outcome", ""),
                "outcome_sentence": c.get("outcome_sentence") or c.get("relevant_sentence", ""),
                "legal_provisions": c.get("legal_provisions", []),
                "citation_line": c.get("citation_line", ""),
                "url": c.get("url") or c.get("judgment_url", "https://www.sci.gov.in/")
            }
            return {
                "success": True,
                "data": formatted,
                "source": "courts_and_cases_api",
                "fallback_used": False,
                "error": None
            }

        return {
            "success": False,
            "data": None,
            "source": None,
            "fallback_used": False,
            "error": error or f"Failed to retrieve case details for ID: {clean_id}"
        }

    def resolve_citations(self, text: str) -> Dict[str, Any]:
        """
        Endpoint C: Identify and resolve legal citations mentioned in legal text.
        GET /api/v1/citations/resolve?text={text}
        """
        if not text or not isinstance(text, str) or not text.strip():
            return {
                "success": False,
                "data": None,
                "source": None,
                "fallback_used": False,
                "error": "Text parameter must be a non-empty string."
            }

        clean_text = text.strip()
        if len(clean_text) > 500:
            clean_text = clean_text[:500]

        params = {"text": clean_text}
        success, data, error, status_code = self._execute_request("api/v1/citations/resolve", params=params)

        if success and data:
            citations = data.get("citations") or data.get("results") or []
            resolved_list = []
            for item in citations:
                resolved_list.append({
                    "citation": item.get("citation", ""),
                    "normalized_citation": item.get("normalized_citation", ""),
                    "matched": item.get("matched", True),
                    "case_id": item.get("case_id", ""),
                    "title": item.get("title", ""),
                    "court": item.get("court", ""),
                    "year": item.get("year", ""),
                    "url": item.get("url", "https://www.sci.gov.in/")
                })

            return {
                "success": True,
                "data": {
                    "input_text": clean_text,
                    "count": len(resolved_list),
                    "citations": resolved_list
                },
                "source": "courts_and_cases_api",
                "fallback_used": False,
                "error": None
            }

        # Safe fallback for citation resolution: report unmatched cleanly without fabrication
        return {
            "success": True,
            "data": {
                "input_text": clean_text,
                "count": 0,
                "citations": [],
                "note": "Citations could not be resolved through external API. Never fabricating legal citations."
            },
            "source": "local_fallback",
            "fallback_used": True,
            "error": error
        }

    def get_statute(self, act: str, section: str) -> Dict[str, Any]:
        """
        Endpoint D: Statutory Section Retrieval.
        GET /api/v1/statutes/{act}/{section}
        Supported Act slugs: ipc, bns, crpc, bnss, iea, bsa, cpc.
        """
        if not act or not isinstance(act, str) or not act.strip():
            return {
                "success": False,
                "data": None,
                "source": None,
                "fallback_used": False,
                "error": f"Act identifier is required. Supported acts: {list(SUPPORTED_ACTS.keys())}"
            }

        clean_act = act.strip().lower()
        if clean_act not in SUPPORTED_ACTS:
            return {
                "success": False,
                "data": None,
                "source": None,
                "fallback_used": False,
                "error": f"Unsupported Act slug '{clean_act}'. Allowed: {list(SUPPORTED_ACTS.keys())}"
            }

        if not section or not isinstance(section, str) or not section.strip():
            return {
                "success": False,
                "data": None,
                "source": None,
                "fallback_used": False,
                "error": "Section identifier must be a non-empty string."
            }

        clean_section = section.strip()
        # Section validation (e.g. 318, 420, 173(1), 46(4), 51A)
        if not re.match(r"^[0-9A-Za-z\(\)\-_]+$", clean_section) or len(clean_section) > 30:
            return {
                "success": False,
                "data": None,
                "source": None,
                "fallback_used": False,
                "error": f"Invalid section format '{clean_section}'. Must be alphanumeric with optional parentheses/hyphens."
            }

        safe_endpoint = f"api/v1/statutes/{quote(clean_act, safe='')}/{quote(clean_section, safe='')}"
        success, data, error, status_code = self._execute_request(safe_endpoint)

        if success and data:
            act_info = SUPPORTED_ACTS[clean_act]
            res_data = {
                "act_slug": clean_act,
                "act_name": data.get("act_name") or act_info["name"],
                "section": data.get("section") or clean_section,
                "heading": data.get("heading") or data.get("title", ""),
                "text": data.get("text") or data.get("provision", ""),
                "status": act_info["status"],
                "corresponding_provision": data.get("corresponding_provision") or data.get("related_section", None),
                "source_title": "Courts & Cases Statutory Database",
                "source_url": data.get("url") or act_info["source_url"]
            }
            return {
                "success": True,
                "data": res_data,
                "source": "courts_and_cases_api",
                "fallback_used": False,
                "error": None
            }

        # Resilient fallback from verified statutory repository
        return self._fallback_statute_lookup(clean_act, clean_section, error_reason=error)

    def _fallback_statute_lookup(self, act: str, section: str, error_reason: Optional[str] = None) -> Dict[str, Any]:
        """Provides verified statutory provision from the local repository when external API is unreachable."""
        act_info = SUPPORTED_ACTS.get(act, {
            "name": act.upper(),
            "status": "Unknown",
            "source_url": "https://www.indiacode.nic.in/"
        })

        # Normalize section lookup key (strip non-digits for fallback match if needed)
        norm_sec = re.sub(r"[^\w]", "", section.lower())
        matched_entry = None

        # Check exact (act, section) in verified dictionary
        for (k_act, k_sec), val in VERIFIED_STATUTE_FALLBACK.items():
            if k_act == act and (k_sec.lower() == section.lower() or k_sec.lower() == norm_sec):
                matched_entry = val
                break

        if matched_entry:
            return {
                "success": True,
                "data": {
                    "act_slug": act,
                    "act_name": matched_entry["act_name"],
                    "section": matched_entry["section"],
                    "heading": matched_entry["heading"],
                    "text": matched_entry["text"],
                    "status": matched_entry["status"],
                    "corresponding_provision": matched_entry.get("former_provision"),
                    "source_title": "India Code - Digital Repository of All Central and State Acts",
                    "source_url": act_info["source_url"]
                },
                "source": "local_statutory_store",
                "fallback_used": True,
                "error": error_reason
            }

        # If not present in pre-cached provisions, provide an authoritative India Code reference
        return {
            "success": True,
            "data": {
                "act_slug": act,
                "act_name": act_info["name"],
                "section": section,
                "heading": f"Section {section} of {act_info['name']}",
                "text": (
                    f"Official statutory text for Section {section} of {act_info['name']} should be verified "
                    f"directly from India Code (the official digital repository of Central and State Acts)."
                ),
                "status": act_info["status"],
                "corresponding_provision": None,
                "source_title": "India Code - Digital Repository of All Central and State Acts",
                "source_url": act_info["source_url"]
            },
            "source": "local_statutory_store",
            "fallback_used": True,
            "error": error_reason
        }


# Module-level client instance and public functions
_CLIENT_INSTANCE: Optional[CourtsAndCasesClient] = None

def get_legal_api_client() -> CourtsAndCasesClient:
    """Retrieve or initialize the global CourtsAndCasesClient instance."""
    global _CLIENT_INSTANCE
    if _CLIENT_INSTANCE is None:
        _CLIENT_INSTANCE = CourtsAndCasesClient()
    return _CLIENT_INSTANCE

def search_judgments(query: str, limit: int = 10) -> Dict[str, Any]:
    """Search court judgments via Courts & Cases API with fallback."""
    return get_legal_api_client().search_judgments(query, limit)

def get_case_details(case_id: str) -> Dict[str, Any]:
    """Retrieve details for a specific judgment by case ID."""
    return get_legal_api_client().get_case_details(case_id)

def resolve_citations(text: str) -> Dict[str, Any]:
    """Resolve legal citations from text with fallback."""
    return get_legal_api_client().resolve_citations(text)

def get_statute(act: str, section: str) -> Dict[str, Any]:
    """Retrieve statutory section provision with fallback."""
    return get_legal_api_client().get_statute(act, section)

def retrieve_legal_context(user_question: str) -> Dict[str, Any]:
    """
    High-level integration bridging NLP intent, statutory extraction, and API retrieval.
    Prepares a unified context payload for the downstream RAG pipeline.
    """
    client = get_legal_api_client()
    nlp_result = find_best_faq(user_question)

    retrieved_statutes = []
    retrieved_judgments = []

    # 1. If explicit statutes/sections were extracted by NLP, retrieve statutory details
    for ref in nlp_result.get("extracted_legal_references", []):
        slug = ref.get("slug")
        number = ref.get("number")
        if slug in SUPPORTED_ACTS and number:
            statute_res = client.get_statute(slug, number)
            if statute_res.get("success") and statute_res.get("data"):
                # Avoid duplicates
                if not any(s.get("act_slug") == slug and s.get("section") == statute_res["data"].get("section") for s in retrieved_statutes):
                    retrieved_statutes.append(statute_res["data"])

    # Semantic keyword fallback for statutory context across 35 Indian legal domains
    if not retrieved_statutes:
        lower_q = user_question.lower()

        # A. State-specific Tenancy Eviction
        if any(w in lower_q for w in ["eviction", "evict", "tenant", "landlord", "rent"]):
            if "tamil nadu" in lower_q or "chennai" in lower_q:
                stat = client.get_statute("tn_tenancy", "21")
                if stat.get("success") and stat.get("data"):
                    retrieved_statutes.append(stat["data"])
            elif "delhi" in lower_q:
                stat = client.get_statute("delhi_rent", "14")
                if stat.get("success") and stat.get("data"):
                    retrieved_statutes.append(stat["data"])
            elif "maharashtra" in lower_q or "mumbai" in lower_q or "pune" in lower_q:
                stat = client.get_statute("mh_rent", "15")
                if stat.get("success") and stat.get("data"):
                    retrieved_statutes.append(stat["data"])

        # B. Matrimonial Maintenance / Working Wife
        if any(w in lower_q for w in ["wife", "maintenance", "alimony", "spousal"]):
            s1 = client.get_statute("hma", "24")
            if s1.get("success") and s1.get("data") and not any(s.get("act_slug") == "hma" for s in retrieved_statutes):
                retrieved_statutes.append(s1["data"])
            s2 = client.get_statute("bnss", "144")
            if s2.get("success") and s2.get("data") and not any(s.get("act_slug") == "bnss" and s.get("section") == "144" for s in retrieved_statutes):
                retrieved_statutes.append(s2["data"])

        # C. Police Arrest / Warrant Safegaurds
        elif any(w in lower_q for w in ["arrest", "warrant", "custody"]):
            s1 = client.get_statute("bnss", "35")
            if s1.get("success") and s1.get("data") and not any(s.get("act_slug") == "bnss" for s in retrieved_statutes):
                retrieved_statutes.append(s1["data"])
            s2 = client.get_statute("constitution", "22")
            if s2.get("success") and s2.get("data") and not any(s.get("act_slug") == "constitution" for s in retrieved_statutes):
                retrieved_statutes.append(s2["data"])

        # D. Defective Product / Consumer Grievance
        elif any(w in lower_q for w in ["defective", "phone", "mobile", "laptop"]) and any(w in lower_q for w in ["product", "warranty", "refund", "defective", "goods", "service", "phone", "mobile"]):
            s1 = client.get_statute("cpa", "35")
            if s1.get("success") and s1.get("data") and not any(s.get("act_slug") == "cpa" for s in retrieved_statutes):
                retrieved_statutes.append(s1["data"])
            s2 = client.get_statute("cpa", "84")
            if s2.get("success") and s2.get("data") and not any(s.get("act_slug") == "cpa" and s.get("section") == "84" for s in retrieved_statutes):
                retrieved_statutes.append(s2["data"])

        # E. Unpaid Salary / Wage Deductions
        elif any(w in lower_q for w in ["salary", "wage", "wages", "unpaid salary"]):
            s1 = client.get_statute("payment_wages", "15")
            if s1.get("success") and s1.get("data") and not any(s.get("act_slug") == "payment_wages" for s in retrieved_statutes):
                retrieved_statutes.append(s1["data"])
            s2 = client.get_statute("ida", "33c")
            if s2.get("success") and s2.get("data") and not any(s.get("act_slug") == "ida" for s in retrieved_statutes):
                retrieved_statutes.append(s2["data"])

        statute_lookups = [
            # Criminal & Procedural Laws
            (["theft", "stolen", "stole", "pickpocket"], ("bns", "303")),
            (["cheating", "fraud", "scam", "420"], ("bns", "318")),
            (["murder", "homicide", "kill", "302"], ("bns", "103")),
            (["defamation", "slander", "libel", "reputation"], ("bns", "356")),
            (["stalking", "stalk", "following woman"], ("bns", "78")),
            (["fir", "zero fir", "e-fir", "police station complaint"], ("bnss", "173")),
            (["bailable", "bailable offence", "bail as matter of right"], ("bnss", "478")),
            (["anticipatory bail", "pre-arrest bail"], ("bnss", "482")),
            (["regular bail", "bail in non-bailable", "bail"], ("bnss", "480")),
            (["arrest", "detain", "handcuff"], ("bnss", "35")),
            (["electronic evidence", "whatsapp evidence", "65b"], ("bsa", "61")),
            # Labour, Wages & Employment
            (["salary", "unpaid salary", "delayed salary", "unpaid wages", "withheld salary", "wages not paid", "deduction from wages"], ("payment_wages", "15")),
            # Food Safety
            (["expired food", "unsafe food", "food adulteration", "adulterated food", "fssai"], ("fssa", "59")),
            # Motor Vehicles & Traffic Enforcement
            (["seize driving licence", "seize driving license", "licence seized", "license seized", "impound driving licence", "confiscate license"], ("mv_act", "206")),
            # Property & Easement Rights
            (["blocking access", "easement", "right of way", "light and air", "neighbour construction"], ("easements", "15")),
            # Constitutional & Administrative
            (["common law", "precedent", "stare decisis"], ("constitution", "141")),
            (["fundamental right", "fundamental rights", "equality"], ("constitution", "part3")),
            (["writ", "habeas corpus", "mandamus", "article 32"], ("constitution", "32")),
            (["high court writ", "article 226"], ("constitution", "226")),
            (["fundamental duty", "article 51a"], ("constitution", "51a")),
            # Commercial & Financial
            (["cheque bounce", "bounced cheque", "dishonour", "138", "dishonor"], ("ni_act", "138")),
            (["contract", "breach of contract", "agreement", "offer", "acceptance"], ("contract_act", "10")),
            (["insolvency", "bankruptcy", "ibc", "nclt"], ("ibc", "7")),
            (["sarfaesi", "bank loan default", "possession notice"], ("sarfaesi", "13")),
            (["money laundering", "pmla", "ed arrest"], ("pmla", "3")),
            (["board of directors", "director duties", "incorporation of company", "mca filing", "shareholder rights"], ("companies_act", "166")),
            # Consumer & Real Estate
            (["consumer", "defective goods", "deficiency in service", "consumer court"], ("cpa", "35")),
            (["rera", "builder delay", "flat possession", "builder refund"], ("rera", "18")),
            (["rent", "eviction", "tenant", "landlord", "security deposit"], ("model_tenancy", "21")),
            (["gift deed", "transfer of property", "lease"], ("tpa", "122")),
            # Family & Succession
            (["divorce", "mutual consent divorce", "alimony"], ("hma", "13B")),
            (["maintenance", "interim maintenance", "spousal support"], ("hma", "24")),
            (["daughter inheritance", "ancestral property", "coparcenary"], ("hsa", "6")),
            # Women & Child Rights
            (["domestic violence", "dv act", "protection order", "shared household"], ("dv_act", "12")),
            (["sexual harassment", "posh", "icc", "workplace harassment"], ("posh", "9")),
            (["maternity", "maternity benefit", "pregnancy leave"], ("maternity_benefit", "5")),
            (["pocso", "child abuse", "minor protection"], ("pocso", "19")),
            # Special & Welfare Laws
            (["sc/st", "atrocity", "caste abuse", "caste discrimination"], ("sc_st_act", "3")),
            (["corruption", "bribe", "public servant bribe", "vigilance"], ("poca", "7")),
            (["rti", "right to information", "pio", "first appeal"], ("rti_act", "6")),
            (["environment", "ngt", "pollution", "tree cutting"], ("epa", "15")),
            (["rte", "right to education", "free admission 25%"], ("rte_act", "12")),
            (["senior citizen", "elderly parent", "parent maintenance"], ("senior_citizens", "4")),
            (["arbitration", "arbitrator", "commercial dispute adr"], ("arbitration_act", "9")),
            (["lok adalat", "free legal aid", "nalsa", "dlsa"], ("lsaa", "21")),
            (["drunk driving", "traffic fine", "hit and run", "challan"], ("mv_act", "185")),
            (["patient right", "medical negligence", "hospital overcharging"], ("clinical_est", "11")),
            (["cyber", "phishing", "online fraud", "identity theft", "hacked"], ("it_act", "66D")),
            (["data privacy", "dpdp", "personal data breach"], ("dpdp", "6")),
            (["trademark", "patent", "copyright", "infringement"], ("trademark_act", "29")),
            (["income tax", "itr", "tax audit"], ("it_tax_act", "139")),
            (["gst", "input tax credit", "eway bill"], ("cgst_act", "16")),
            (["citizenship", "caa", "passport impounded"], ("citizenship_act", "5")),
        ]
        for keywords, (act_slug, sec_slug) in statute_lookups:
            if any(kw in lower_q for kw in keywords):
                stat = client.get_statute(act_slug, sec_slug)
                if stat.get("success") and stat.get("data"):
                    retrieved_statutes.append(stat["data"])
                    break

    # 2. If the user question requires case law or broader legal context, search judgments
    intent = nlp_result.get("intent", "")
    if intent in ("understand_procedure", "statutory_inquiry", "general_legal_inquiry", "police_complaint_fir"):
        search_res = client.search_judgments(user_question, limit=3)
        if search_res.get("success"):
            retrieved_judgments = search_res.get("data", {}).get("judgments", [])

    return {
        "user_question": user_question,
        "nlp_analysis": nlp_result,
        "retrieved_statutes": retrieved_statutes,
        "retrieved_judgments": retrieved_judgments,
        "authoritative_sources": Config.OFFICIAL_LEGAL_SOURCES
    }
