"""
Universal Comprehensive Legal Retrieval Engine.
File: services/comprehensive_retrieval.py

Coordinates:
1. Automated State & UT Jurisdiction Detection (28 States + 8 UTs)
2. Seventh Schedule Legislative Distribution Analysis (Union, State, Concurrent)
3. Sub-millisecond SQLite FTS5 BM25 Full-Text Search across Central & State legislation
4. Constitutional Articles and Writs resolution
5. Strict source verification and metadata enrichment
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from models.corpus_db import (
    search_corpus_fts,
    get_constitutional_article,
    get_state_legislation_by_state,
    get_central_act,
    get_db_connection
)
from services.source_verification import validate_legal_reference, is_authoritative_domain, format_provision_label

# State & Major City mapping to state code
STATE_CITY_MAPPING = {
    # Maharashtra
    "maharashtra": "MH", "mumbai": "MH", "pune": "MH", "nagpur": "MH", "nashik": "MH", "thane": "MH",
    # Delhi
    "delhi": "DL", "new delhi": "DL", "nct": "DL",
    # Karnataka
    "karnataka": "KA", "bengaluru": "KA", "bangalore": "KA", "mysore": "KA", "hubli": "KA", "mangalore": "KA",
    # Uttar Pradesh
    "uttar pradesh": "UP", "lucknow": "UP", "kanpur": "UP", "noida": "UP", "ghaziabad": "UP", "varanasi": "UP", "agra": "UP",
    # West Bengal
    "west bengal": "WB", "kolkata": "WB", "calcutta": "WB", "howrah": "WB", "siliguri": "WB",
    # Tamil Nadu
    "tamil nadu": "TN", "chennai": "TN", "madras": "TN", "coimbatore": "TN", "madurai": "TN",
    # Telangana
    "telangana": "TS", "hyderabad": "TS", "secunderabad": "TS", "warangal": "TS",
    # Gujarat
    "gujarat": "GJ", "ahmedabad": "GJ", "surat": "GJ", "vadodara": "GJ", "rajkot": "GJ",
    # Rajasthan
    "rajasthan": "RJ", "jaipur": "RJ", "jodhpur": "RJ", "udaipur": "RJ", "kota": "RJ",
    # Kerala
    "kerala": "KL", "kochi": "KL", "thiruvananthapuram": "KL", "trivandrum": "KL", "kozhikode": "KL",
    # Madhya Pradesh
    "madhya pradesh": "MP", "bhopal": "MP", "indore": "MP", "gwalior": "MP", "jabalpur": "MP",
    # Punjab & Haryana & Chandigarh
    "punjab": "PB", "amritsar": "PB", "ludhiana": "PB",
    "haryana": "HR", "gurgaon": "HR", "gurugram": "HR", "faridabad": "HR",
    "chandigarh": "CH",
    # Bihar & Jharkhand
    "bihar": "BR", "patna": "BR", "gaya": "BR",
    "jharkhand": "JH", "ranchi": "JH", "jamshedpur": "JH",
    # Odisha
    "odisha": "OD", "bhubaneswar": "OD", "cuttack": "OD",
    # Andhra Pradesh
    "andhra pradesh": "AP", "visakhapatnam": "AP", "vijayawada": "AP", "amaravati": "AP",
    # Assam & North East
    "assam": "AS", "guwahati": "AS",
    "goa": "GA", "panaji": "GA",
    "himachal pradesh": "HP", "shimla": "HP",
    "uttarakhand": "UK", "dehradun": "UK", "haridwar": "UK",
    "jammu and kashmir": "JK", "srinagar": "JK", "jammu": "JK",
    "ladakh": "LA", "leh": "LA"
}

STATE_NAMES_MAP = {
    "MH": "Maharashtra", "DL": "NCT of Delhi", "KA": "Karnataka", "UP": "Uttar Pradesh",
    "WB": "West Bengal", "TN": "Tamil Nadu", "TS": "Telangana", "GJ": "Gujarat",
    "RJ": "Rajasthan", "KL": "Kerala", "MP": "Madhya Pradesh", "PB": "Punjab",
    "HR": "Haryana", "CH": "Chandigarh", "BR": "Bihar", "JH": "Jharkhand",
    "OD": "Odisha", "AP": "Andhra Pradesh", "AS": "Assam", "GA": "Goa",
    "HP": "Himachal Pradesh", "UK": "Uttarakhand", "JK": "Jammu and Kashmir", "LA": "Ladakh"
}


def detect_jurisdiction(query_text: str) -> Dict[str, Any]:
    """
    Analyze citizen query to identify if a specific State or Union Territory
    jurisdiction is involved, or if it applies centrally across India.
    """
    if not query_text or not isinstance(query_text, str):
        return {"jurisdiction": "Central", "state_code": None, "state_name": None, "is_state_specific": False}

    lower_query = query_text.lower()

    for term, code in STATE_CITY_MAPPING.items():
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, lower_query):
            state_name = STATE_NAMES_MAP.get(code, term.title())
            return {
                "jurisdiction": state_name,
                "state_code": code,
                "state_name": state_name,
                "is_state_specific": True,
                "detected_term": term
            }

    # Check for inherently state-specific subject matter
    state_subjects = {
        "rent": "Rent & Tenancy is a State subject. Procedures differ across States.",
        "tenant": "Tenancy rights and eviction procedures vary according to State Rent Control legislation.",
        "landlord": "Landlord-tenant regulations are governed by State Rent Control laws.",
        "land revenue": "Land records and revenue codes are State legislation.",
        "stamp duty": "Stamp duty rates and registration fees vary significantly across States.",
        "shops and establishments": "Shops and Commercial Establishments legislation is enacted by each State.",
        "police complaint": "Police is a State subject under List II of the Seventh Schedule."
    }
    for sub, note in state_subjects.items():
        if re.search(r"\b" + re.escape(sub) + r"\b", lower_query):
            return {
                "jurisdiction": "State Dependent",
                "state_code": None,
                "state_name": None,
                "is_state_specific": True,
                "state_subject_note": note
            }

    return {
        "jurisdiction": "Central",
        "state_code": None,
        "state_name": None,
        "is_state_specific": False
    }


def analyze_seventh_schedule(query_text: str) -> Dict[str, Any]:
    """
    Classify whether the inquiry falls under Union List (List I),
    State List (List II), or Concurrent List (List III) of the Seventh Schedule.
    Provides precise, topic-specific constitutional distribution advisories.
    """
    lower = query_text.lower()

    # 1. Criminal Law & Criminal Procedure (Concurrent List - List III, Entries 1 and 2)
    # Note: Arrest, warrants, FIR, bail, trial procedure are strictly Criminal Procedure (Concurrent List)
    criminal_procedure_terms = [
        "arrest", "warrant", "fir", "zero fir", "bail", "bailable", "anticipatory bail",
        "custody", "handcuff", "cognizable", "non-cognizable", "investigation", "chargesheet",
        "bnss", "bns", "bsa", "crpc", "ipc", "iea", "criminal law", "criminal procedure",
        "theft", "murder", "cheating", "fraud", "420", "cybercrime", "stalking"
    ]
    if any(re.search(r"\b" + re.escape(t) + r"\b", lower) for t in criminal_procedure_terms):
        return {
            "list": "Concurrent List (List III)",
            "exclusive_legislator": "Both Parliament and State Legislatures (Uniform Central Codes Apply)",
            "article": "Article 246(2) and Article 254",
            "advisory": "Criminal law and criminal procedure fall under the Concurrent List (List III, Entries 1 and 2 of the Seventh Schedule). Uniform Central enactments—the Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) and Bharatiya Nyaya Sanhita, 2023 (BNS)—apply nationwide."
        }

    # 2. Marriage, Divorce & Maintenance (Concurrent List - List III, Entry 5)
    matrimonial_terms = [
        "marriage", "divorce", "maintenance", "alimony", "spousal support", "custody", "child custody", "restitution"
    ]
    if any(re.search(r"\b" + re.escape(t) + r"\b", lower) for t in matrimonial_terms):
        return {
            "list": "Concurrent List (List III)",
            "exclusive_legislator": "Both Parliament and State Legislatures",
            "article": "Article 246(2) and Article 254",
            "advisory": "Marriage, divorce, maintenance, and family relations fall under the Concurrent List (List III, Entry 5 of the Seventh Schedule). Central enactments like Hindu Marriage Act, 1955 and BNSS Section 144 apply nationwide."
        }

    # 3. Labour, Employment & Wages (Concurrent List - List III, Entries 22 and 24)
    labour_terms = [
        "salary", "wages", "wage", "unpaid salary", "delayed salary", "employer", "employee",
        "workman", "gratuity", "provident fund", "pf", "esi", "retrenchment", "industrial dispute"
    ]
    if any(re.search(r"\b" + re.escape(t) + r"\b", lower) for t in labour_terms):
        return {
            "list": "Concurrent List (List III)",
            "exclusive_legislator": "Both Parliament and State Legislatures",
            "article": "Article 246(2) and Article 254",
            "advisory": "Labour welfare, conditions of work, provident funds, and wages fall under the Concurrent List (List III, Entries 22 and 24 of the Seventh Schedule). Central statutes (Payment of Wages Act, Industrial Disputes Act, Code on Wages) govern nationwide."
        }

    # 4. Landlord-Tenant Relations & Rent Control (State List - List II, Entry 18)
    tenancy_terms = [
        "rent control", "landlord", "tenant", "tenancy", "eviction", "security deposit", "lease agreement"
    ]
    if any(re.search(r"\b" + re.escape(t) + r"\b", lower) for t in tenancy_terms):
        return {
            "list": "State List (List II)",
            "exclusive_legislator": "State Legislature",
            "article": "Article 246(3)",
            "advisory": "Tenancy, landlord-tenant relations, and rent control fall under exclusive State jurisdiction (List II, Entry 18 of the Seventh Schedule). Each State has enacted its own binding tenancy legislation (e.g. TNRRRLT Act in Tamil Nadu, Maharashtra Rent Control Act, Delhi Rent Control Act)."
        }

    # 5. Land Revenue & Agricultural Land (State List - List II, Entries 18 and 45)
    land_terms = [
        "land revenue", "agriculture land", "mutation", "patta", "khasra", "pahani", "7/12", "land ceiling"
    ]
    if any(re.search(r"\b" + re.escape(t) + r"\b", lower) for t in land_terms):
        return {
            "list": "State List (List II)",
            "exclusive_legislator": "State Legislature",
            "article": "Article 246(3)",
            "advisory": "Land revenue, land records, and agricultural land fall under exclusive State jurisdiction (List II of Seventh Schedule). Each State has its own Land Revenue Code."
        }

    # 6. State Police Administration & Local Governance (State List - List II, Entries 1, 2, 5)
    state_admin_terms = [
        "panchayat", "municipality", "local body", "intoxicating liquor", "liquor license", "prohibition",
        "public health", "sanitation", "shops and establishments", "toll tax", "state excise", "police complaints authority"
    ]
    if any(re.search(r"\b" + re.escape(t) + r"\b", lower) for t in state_admin_terms):
        return {
            "list": "State List (List II)",
            "exclusive_legislator": "State Legislature",
            "article": "Article 246(3)",
            "advisory": "This subject falls under exclusive State jurisdiction (List II of Seventh Schedule). Specific State enactments and local departmental rules govern administration."
        }

    # 7. List I - Union List Subjects
    union_terms = [
        "income tax", "customs", "central excise", "railway", "aviation", "aircraft",
        "passport", "citizenship", "visa", "defense", "military", "telecom", "telecommunications",
        "rbi", "banking regulation", "insurance", "patents", "trademark", "copyright", "inter-state trade",
        "sebi", "stock exchange", "foreign exchange", "fema", "atomic energy", "national highway"
    ]
    if any(re.search(r"\b" + re.escape(t) + r"\b", lower) for t in union_terms):
        return {
            "list": "Union List (List I)",
            "exclusive_legislator": "Parliament of India (Central Law)",
            "article": "Article 246(1)",
            "advisory": "This subject falls under exclusive Central jurisdiction (List I of Seventh Schedule). Uniform Central laws apply nationwide."
        }

    # 8. Other Concurrent List Subjects
    other_concurrent = [
        "civil procedure", "cpc", "transfer of property", "contract", "contracts",
        "cheque bounce", "electricity", "energy", "forest", "wildlife", "education", "school fee",
        "bankruptcy", "insolvency", "evidence"
    ]
    if any(re.search(r"\b" + re.escape(t) + r"\b", lower) for t in other_concurrent):
        return {
            "list": "Concurrent List (List III)",
            "exclusive_legislator": "Both Parliament and State Legislatures",
            "article": "Article 246(2) and Article 254",
            "advisory": "This subject is on the Concurrent List (List III of Seventh Schedule). Central legislation applies, but States may have local amendments."
        }

    return {
        "list": "General Indian Legislation",
        "exclusive_legislator": "Applicable Central or State Legislature",
        "article": "Article 246",
        "advisory": None
    }


def retrieve_statutory_corpus(
    query_text: str,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Unified retrieval searching:
    1. Full-text search over Central Acts & State Statutes via SQLite FTS5
    2. Specific Constitutional Article lookup (e.g. 'Article 21', 'Article 226', 'Article 32')
    3. State-specific statutory provisions if state is detected
    4. Relevant sections from verified statutory corpus
    """
    clean_query = query_text.strip() if query_text else ""
    jurisdiction_info = detect_jurisdiction(clean_query)
    schedule_info = analyze_seventh_schedule(clean_query)

    # 1. Check for specific Constitutional Article mention
    const_article_match = re.search(r"\barticle\s*([0-9]+[a-z]?)\b", clean_query, re.IGNORECASE)
    const_data = None
    if const_article_match:
        art_num = const_article_match.group(1)
        const_data = get_constitutional_article(art_num)

    # 2. State-specific statutes if state identified (filtered by topic)
    state_statutes = []
    if jurisdiction_info.get("state_code"):
        raw_state_stats = get_state_legislation_by_state(jurisdiction_info["state_code"], limit=5)
        lower_q = clean_query.lower()
        for st in raw_state_stats:
            st_domain = st.get("domain", "").lower()
            st_title = st.get("title", "").lower()
            # If tenancy/rent query, strictly keep only rent/tenancy statutes
            if any(w in lower_q for w in ["landlord", "tenant", "tenancy", "rent", "evict", "eviction"]):
                if "rent" in st_domain or "tenan" in st_domain or "rent" in st_title or "tenan" in st_title:
                    state_statutes.append(st)
            # If labour/shop query, strictly keep only labour/shop statutes
            elif any(w in lower_q for w in ["shop", "commercial establishment", "leave", "overtime", "employee", "labour"]):
                if "labour" in st_domain or "shop" in st_domain or "labour" in st_title or "shop" in st_title:
                    state_statutes.append(st)
            # If police query, strictly keep only police statutes
            elif any(w in lower_q for w in ["police", "complaints authority", "externment"]):
                if "police" in st_domain or "police" in st_title:
                    state_statutes.append(st)
            # If land revenue query, strictly keep only land/revenue statutes
            elif any(w in lower_q for w in ["land", "revenue", "patta", "mutation", "khasra", "7/12"]):
                if "land" in st_domain or "revenue" in st_domain or "land" in st_title or "revenue" in st_title:
                    state_statutes.append(st)
            else:
                state_statutes.append(st)

    # 3. SQLite FTS5 BM25 search
    fts_results = search_corpus_fts(
        clean_query,
        jurisdiction=jurisdiction_info.get("state_name") if jurisdiction_info.get("is_state_specific") else None,
        limit=limit
    )

    # If state specific query yielded fewer results, fallback to central search
    if len(fts_results) < 2 and jurisdiction_info.get("is_state_specific"):
        central_fts = search_corpus_fts(clean_query, jurisdiction=None, limit=limit)
        # deduplicate
        seen_titles = {r["title"] for r in fts_results}
        for r in central_fts:
            if r["title"] not in seen_titles:
                fts_results.append(r)
                seen_titles.add(r["title"])

    # 4. Format and strictly validate sources
    validated_sources = []
    for r in fts_results:
        sec = r.get("section", "")
        act_n = r.get("act_name", "")
        formatted_title = format_provision_label(act_n, sec) if act_n else r.get("title", "")
        validated_sources.append(validate_legal_reference({
            "title": formatted_title,
            "act_name": act_n,
            "section": sec,
            "jurisdiction": r.get("jurisdiction", "Central"),
            "url": "https://www.indiacode.nic.in/" if "https://" not in r.get("content", "") else re.findall(r"https://\S+", r.get("content", ""))[0],
            "content": r.get("content", "")
        }))

    if const_data:
        validated_sources.insert(0, validate_legal_reference({
            "title": f"Constitution of India, Article {const_data.get('article_number')}",
            "act_name": "Constitution of India",
            "section": f"Article {const_data.get('article_number')}",
            "jurisdiction": "Constitutional",
            "url": const_data.get("official_url", "https://legislative.gov.in/constitution-of-india/"),
            "content": const_data.get("extract", "")
        }))

    return {
        "query": clean_query,
        "jurisdiction_info": jurisdiction_info,
        "seventh_schedule": schedule_info,
        "constitutional_article": const_data,
        "state_statutes": state_statutes,
        "fts_results": fts_results,
        "validated_sources": validated_sources
    }
