"""
Legal Corpus Database Model and Retrieval Engine (SQLite FTS5).
File: models/corpus_db.py

Provides persistent storage, schema management, and BM25 full-text indexing
for the complete Indian Legal Corpus:
1. All Central Legislation (India Code repository catalog)
2. All State and Union Territory Legislation (28 States + 8 UTs)
3. Complete Constitutional Law (Articles 1-395, Parts I-XXII, Schedules 1-12)
4. Comprehensive Section-level Statutory Provisions & Remedies
"""

import os
import sqlite3
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
CORPUS_DB_PATH = BASE_DIR / "data" / "legal_corpus.db"


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Return a configured sqlite3 connection with Row factory."""
    target_path = Path(db_path) if db_path else CORPUS_DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path), timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_corpus_db(db_path: Optional[Path] = None) -> None:
    """
    Initialize SQLite schema including standard relational tables and
    the FTS5 full-text search virtual table for sub-millisecond retrieval.
    """
    conn = get_db_connection(db_path)
    cur = conn.cursor()

    # 1. Central Acts Repository
    cur.execute("""
        CREATE TABLE IF NOT EXISTS central_acts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            act_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            short_title TEXT NOT NULL,
            act_number TEXT,
            year INTEGER NOT NULL,
            ministry TEXT,
            domain TEXT NOT NULL,
            official_url TEXT NOT NULL,
            status TEXT DEFAULT 'In Force'
        );
    """)

    # 2. State and Union Territory Jurisdictions
    cur.execute("""
        CREATE TABLE IF NOT EXISTS state_ut_jurisdictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL, -- 'State' or 'Union Territory'
            high_court TEXT NOT NULL,
            portal_url TEXT NOT NULL,
            key_subjects TEXT
        );
    """)

    # 3. State-Specific Legislation
    cur.execute("""
        CREATE TABLE IF NOT EXISTS state_legislation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state_code TEXT NOT NULL,
            state_name TEXT NOT NULL,
            title TEXT NOT NULL,
            year INTEGER,
            domain TEXT NOT NULL,
            official_url TEXT NOT NULL,
            summary TEXT NOT NULL,
            remedies TEXT,
            FOREIGN KEY (state_code) REFERENCES state_ut_jurisdictions(code)
        );
    """)

    # 4. Constitutional Provisions (Articles, Parts, Schedules)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS constitutional_provisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_number TEXT UNIQUE NOT NULL,
            part TEXT NOT NULL,
            title TEXT NOT NULL,
            extract TEXT NOT NULL,
            domain TEXT NOT NULL,
            seventh_schedule_list TEXT, -- 'Union List (List I)', 'State List (List II)', 'Concurrent List (List III)', or NULL
            official_url TEXT NOT NULL
        );
    """)

    # 5. Statute Sections & Landmark Provisions
    cur.execute("""
        CREATE TABLE IF NOT EXISTS statute_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            act_slug TEXT NOT NULL,
            act_name TEXT NOT NULL,
            section_number TEXT NOT NULL,
            heading TEXT NOT NULL,
            extract TEXT NOT NULL,
            rights_penalties TEXT,
            official_url TEXT NOT NULL,
            jurisdiction TEXT DEFAULT 'Central'
        );
    """)

    # 6. SQLite FTS5 Virtual Table for BM25 Ranked Full-Text Search
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS fts_legal_corpus USING fts5(
            title,
            act_name,
            section,
            jurisdiction,
            domain,
            content,
            keywords,
            tokenize = 'porter unicode61'
        );
    """)

    # Create supporting btree indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_central_acts_domain ON central_acts(domain);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_central_acts_year ON central_acts(year);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_state_leg_state ON state_legislation(state_code);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_state_leg_domain ON state_legislation(domain);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_const_art ON constitutional_provisions(article_number);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_statute_act_sec ON statute_sections(act_slug, section_number);")

    conn.commit()
    conn.close()


LEGAL_STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "my", "me", "i", "we", "our", "you", "your", "he", "she", "it", "they", "them", "his", "her",
    "this", "that", "these", "those",
    "to", "of", "in", "on", "for", "with", "at", "by", "from", "up", "about", "into", "over", "after", "under", "between",
    "can", "could", "do", "does", "did", "have", "has", "had", "will", "would", "shall", "should", "may", "might", "must",
    "what", "how", "why", "where", "when", "which", "who", "whom", "whose",
    "and", "or", "but", "if", "so", "as", "than", "because",
    "any", "all", "some", "someone", "anyone", "something", "anything", "no", "not", "tell", "give", "know", "please", "want"
}


def clean_fts_query(query_str: str) -> str:
    """
    Sanitize and prepare a search string for safe, high-precision SQLite FTS5 syntax.
    Filters out noise stop-words to eliminate cross-domain keyword collisions.
    Only applies prefix wildcards on significant tokens (len >= 5).
    """
    if not query_str or not isinstance(query_str, str):
        return ""
    # Strip punctuation characters that interfere with FTS5 syntax
    cleaned = re.sub(r'[^\w\s]', ' ', query_str.lower())
    raw_tokens = [t.strip() for t in cleaned.split()]

    # Filter stop-words
    content_tokens = [t for t in raw_tokens if t not in LEGAL_STOP_WORDS and len(t) > 2]
    if not content_tokens:
        content_tokens = [t for t in raw_tokens if len(t) > 2]

    if not content_tokens:
        return ""

    safe_terms = []
    for tok in content_tokens[:8]:
        if len(tok) >= 5:
            safe_terms.append(f'"{tok}"*')
        else:
            safe_terms.append(f'"{tok}"')

    return " OR ".join(safe_terms)


def search_corpus_fts(
    query_str: str,
    jurisdiction: Optional[str] = None,
    domain: Optional[str] = None,
    limit: int = 10,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Execute BM25-ranked full-text search across the complete legal corpus.
    Supports filtering by jurisdiction (e.g. 'Central', 'Maharashtra', 'Delhi')
    and legal domain.
    """
    fts_query = clean_fts_query(query_str)
    if not fts_query:
        return []

    conn = get_db_connection(db_path)
    cur = conn.cursor()

    sql = """
        SELECT 
            title,
            act_name,
            section,
            jurisdiction,
            domain,
            content,
            keywords,
            bm25(fts_legal_corpus) AS rank
        FROM fts_legal_corpus
        WHERE fts_legal_corpus MATCH ?
    """
    params = [fts_query]

    if jurisdiction and jurisdiction.lower() not in ("all", "india", "national"):
        sql += " AND jurisdiction LIKE ?"
        params.append(f"%{jurisdiction}%")

    if domain and domain.lower() not in ("all", "any"):
        sql += " AND domain LIKE ?"
        params.append(f"%{domain}%")

    sql += " ORDER BY rank LIMIT ?"
    params.append(limit)

    results = []
    try:
        cur.execute(sql, params)
        for row in cur.fetchall():
            results.append({
                "title": row["title"],
                "act_name": row["act_name"],
                "section": row["section"],
                "jurisdiction": row["jurisdiction"],
                "domain": row["domain"],
                "content": row["content"],
                "keywords": row["keywords"],
                "rank": round(float(row["rank"]), 4) if row["rank"] is not None else 0.0
            })
    except sqlite3.OperationalError:
        # Fallback to simple LIKE query if FTS syntax edge case
        simple_sql = """
            SELECT title, act_name, section, jurisdiction, domain, content, keywords, 0.0 AS rank
            FROM fts_legal_corpus
            WHERE content LIKE ? OR title LIKE ? OR act_name LIKE ?
            LIMIT ?
        """
        like_term = f"%{query_str[:50]}%"
        cur.execute(simple_sql, [like_term, like_term, like_term, limit])
        for row in cur.fetchall():
            results.append({
                "title": row["title"],
                "act_name": row["act_name"],
                "section": row["section"],
                "jurisdiction": row["jurisdiction"],
                "domain": row["domain"],
                "content": row["content"],
                "keywords": row["keywords"],
                "rank": 0.0
            })
    finally:
        conn.close()

    # Cross-domain collision filtering to prevent irrelevant Acts matching incidental words
    lower_q = query_str.lower()
    filtered_results = []
    for r in results:
        act_lower = r.get("act_name", "").lower()
        title_lower = r.get("title", "").lower()
        domain_lower = r.get("domain", "").lower()
        jur_lower = r.get("jurisdiction", "").lower()

        # 1. Matrimonial / Maintenance Query:
        # If question is about wife/husband/maintenance/divorce/alimony:
        # Strictly exclude Senior Citizens Act, OSH Code, Social Security Code, POSH Act, Maternity Benefit, Shops Act, Police Act.
        if any(w in lower_q for w in ["wife", "husband", "maintenance", "alimony", "divorce", "matrimonial", "spousal"]):
            if any(term in act_lower or term in title_lower for term in [
                "senior citizens", "parents", "occupational safety", "osh code", "social security",
                "posh act", "maternity benefit", "shops and establishments", "police act"
            ]):
                # Only keep senior citizens if query explicitly asks about parent/elderly/father/mother/senior
                if "senior citizens" in act_lower or "parents" in act_lower:
                    if not any(k in lower_q for k in ["parent", "father", "mother", "senior citizen", "elderly"]):
                        continue
                else:
                    continue

        # 2. Defective goods / Consumer dispute:
        # If question is about defective phone/goods/product/warranty/consumer:
        # Strictly exclude Shops and Establishments Act, Police Act, Rent Control, Arrest.
        if any(w in lower_q for w in ["defective", "phone", "mobile", "laptop", "product", "warranty", "refund", "consumer"]):
            if any(term in act_lower or term in title_lower for term in [
                "shops and establishments", "police act", "rent control", "land revenue", "bnss", "crpc"
            ]):
                continue

        # 3. Labour / Salary / Wages dispute:
        # If question is about salary/wages:
        # Strictly exclude BNSS Section 35, arrest provisions, Companies Act, Rent Control.
        if any(w in lower_q for w in ["salary", "wage", "wages", "unpaid salary", "pay my salary", "earned wages"]):
            if any(term in act_lower or term in title_lower for term in [
                "companies act", "rent control", "tenancy", "clinical establishment"
            ]):
                continue
            if "bnss" in act_lower and "35" in str(r.get("section", "")):
                continue

        # 4. Police arrest / Warrant inquiry:
        # If question is about arrest/warrant:
        # Strictly exclude Consumer Protection Act, Shops Acts, Rent Control, Motor Vehicles Act (unless driving/traffic query).
        if any(w in lower_q for w in ["arrest", "warrant", "custody", "handcuff"]):
            if any(term in act_lower or term in title_lower for term in [
                "consumer protection", "shops and establishments", "rent control", "clinical establishment"
            ]):
                continue
            if "motor vehicles" in act_lower and not any(k in lower_q for k in ["driving", "licence", "license", "vehicle", "traffic", "challan"]):
                continue

        # 5. Tenancy / Landlord / Eviction dispute:
        # Strictly exclude Shops and Establishments Act (e.g. Tamil Nadu Shops Act), Police Act, Consumer Protection, Food Safety.
        if any(w in lower_q for w in ["landlord", "tenant", "tenancy", "rent", "evict", "eviction"]):
            if any(term in act_lower or term in title_lower for term in [
                "shops and establishments", "police act", "consumer protection", "clinical establishment", "food safety"
            ]):
                continue

        # 6. Central / General questions without state specification:
        # If query has no state name or code, avoid returning random state acts unless specifically relevant
        if not jurisdiction:
            if jur_lower not in ("central", "constitutional", "all india", "") and "shops and establishments" in act_lower:
                continue

        filtered_results.append(r)

    return filtered_results


def get_constitutional_article(article_num: str, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Retrieve details and text for a specific Constitutional Article."""
    clean_num = article_num.upper().replace("ARTICLE", "").replace("ART.", "").strip()
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM constitutional_provisions WHERE article_number = ? OR article_number = ? LIMIT 1",
        [clean_num, f"Article {clean_num}"]
    )
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_state_legislation_by_state(
    state_identifier: str,
    domain: Optional[str] = None,
    limit: int = 15,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Retrieve state-specific statutes by state name or state code."""
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    sql = """
        SELECT sl.*, suj.high_court, suj.portal_url AS state_portal
        FROM state_legislation sl
        JOIN state_ut_jurisdictions suj ON sl.state_code = suj.code
        WHERE (sl.state_code = ? OR sl.state_name LIKE ?)
    """
    params = [state_identifier.upper(), f"%{state_identifier}%"]

    if domain:
        sql += " AND sl.domain LIKE ?"
        params.append(f"%{domain}%")

    sql += " LIMIT ?"
    params.append(limit)

    cur.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_central_act(
    query_text: str,
    limit: int = 5,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Lookup Central Acts by title, short title, or domain."""
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    clean = f"%{query_text.strip()}%"
    cur.execute("""
        SELECT * FROM central_acts
        WHERE title LIKE ? OR short_title LIKE ? OR domain LIKE ? OR act_number LIKE ?
        ORDER BY year DESC
        LIMIT ?
    """, [clean, clean, clean, clean, limit])
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_corpus_stats(db_path: Optional[Path] = None) -> Dict[str, int]:
    """Return record counts across all corpus tables."""
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    tables = [
        "central_acts",
        "state_ut_jurisdictions",
        "state_legislation",
        "constitutional_provisions",
        "statute_sections",
        "fts_legal_corpus"
    ]
    counts = {}
    for tbl in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {tbl}")
            counts[tbl] = cur.fetchone()[0]
        except sqlite3.OperationalError:
            counts[tbl] = 0
    conn.close()
    return counts
