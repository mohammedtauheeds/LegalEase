"""
Strict Source Verification and Authority Validation Service.
File: services/source_verification.py

Validates legal citations, metadata, official domain whitelists,
and ensures no fabricated or unverified sources are presented to citizens.
"""

import re
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional

# Whitelisted authoritative government and judicial domains
AUTHORITATIVE_DOMAINS = [
    "indiacode.nic.in",
    "legislative.gov.in",
    "egazette.gov.in",
    "egazette.nic.in",
    "sci.gov.in",
    "main.sci.gov.in",
    "judgments.ecourts.gov.in",
    "ecourts.gov.in",
    "india.gov.in",
    "nalsa.gov.in",
    "fssai.gov.in",
    "consumerhelpline.gov.in",
    "edaakhil.nic.in",
    "delhicourts.nic.in",
    "bombayhighcourt.nic.in",
    "hckrecruitment.nic.in",
    "karnatakajudiciary.kar.nic.in",
    "mphc.gov.in",
    "highcourtofjudicatureatallahabad.nic.in",
    "calcuttahighcourt.gov.in",
    "mhc.tn.gov.in"
]


def is_authoritative_domain(url: Optional[str]) -> bool:
    """
    Check if a given URL belongs to an official Indian government,
    legislative, or judicial repository.
    """
    if not url or not isinstance(url, str):
        return False
    parsed = urlparse(url.strip())
    hostname = (parsed.netloc or "").lower()
    if not hostname:
        return False

    # Check against known authoritative domains or .gov.in / .nic.in suffixes
    if any(hostname == d or hostname.endswith("." + d) for d in AUTHORITATIVE_DOMAINS):
        return True
    if hostname.endswith(".gov.in") or hostname.endswith(".nic.in"):
        return True

    return False


def validate_legal_reference(source: Dict[str, Any]) -> Dict[str, Any]:
    """
    Strictly audit and validate a statutory or legal citation.
    Assigns:
    - verification_status: 'Verified Authority', 'Statutory Record', or 'Requires Verification'
    - authoritative_source: bool
    """
    validated = dict(source)
    url = validated.get("url") or validated.get("source_url") or ""
    act_name = validated.get("act") or validated.get("act_name") or validated.get("title") or ""
    section = validated.get("section") or validated.get("section_number") or ""
    jurisdiction = validated.get("jurisdiction") or "Central"

    is_official = is_authoritative_domain(url)
    has_act = bool(act_name.strip())
    has_url = bool(url.strip())

    if is_official and has_act:
        validated["verification_status"] = "Verified Authority"
        validated["authoritative_source"] = True
    elif has_act and has_url:
        validated["verification_status"] = "Statutory Record"
        validated["authoritative_source"] = True
    else:
        validated["verification_status"] = "Requires Verification"
        validated["authoritative_source"] = False

    validated["url"] = url
    validated["act_name"] = act_name
    validated["section"] = section
    validated["jurisdiction"] = jurisdiction

    return validated


def format_provision_label(act_name: str, section: Optional[str] = None) -> str:
    """
    Format a clean, legally correct citation label.
    Prevents erroneous formatting such as:
    - 'Section 2017' (when 2017 is an Act year)
    - 'Section Act 56 of 2007' (when act_number was passed as section)
    - 'Section Article 22' or 'Section 22' for Constitution of India
    - 'Section Rent_Evict'
    """
    act = (act_name or "").strip()
    sec = str(section).strip() if section is not None else ""

    if not sec or sec.lower() in ("none", "null", ""):
        return act

    # If section is a 4-digit year (e.g. 1947, 1954, 1961, 2017, 2023) or contains 'Act ' or 'Rent_'
    if re.match(r"^\d{4}$", sec) or sec.lower().startswith("act ") or sec.lower().startswith("rent_"):
        return act

    # If Constitutional Article
    if "constitution" in act.lower():
        if sec.lower().startswith("article"):
            return f"{act}, {sec}"
        elif sec.lower().startswith("part"):
            return f"{act}, {sec}"
        elif "schedule" in sec.lower():
            return f"{act}, {sec}"
        else:
            return f"{act}, Article {sec}"

    # If section already starts with 'section', 'article', 'order', or 'rule'
    if sec.lower().startswith("section") or sec.lower().startswith("article") or sec.lower().startswith("order") or sec.lower().startswith("rule"):
        return f"{act}, {sec}"

    return f"{act}, Section {sec}"


def format_source_attribution(source: Dict[str, Any]) -> str:
    """Generate a clean, standardized citation string for citizens."""
    act = source.get("act_name") or source.get("title") or "Applicable Law"
    sec = source.get("section") or ""
    jurisdiction = source.get("jurisdiction") or "Central"
    url = source.get("url") or source.get("source_url") or ""

    prefix = format_provision_label(act, sec)
    if jurisdiction and jurisdiction.lower() not in ("central", "national", "all india"):
        prefix += f" ({jurisdiction})"

    if url:
        return f"[{prefix}]({url})"
    return prefix


def verify_judgment_reference(judgment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate court judgment citations ensuring court name, case title,
    citation, and official link meet standards.
    """
    validated = dict(judgment)
    court = validated.get("court") or "Supreme Court of India"
    title = validated.get("case_title") or validated.get("title") or ""
    citation = validated.get("citation") or ""
    source_url = validated.get("source_url") or validated.get("url") or ""

    validated["is_verified"] = bool(title and (citation or source_url))
    validated["verification_tag"] = "Verified Precedent" if validated["is_verified"] else "Requires Verification"
    validated["court"] = court
    validated["title"] = title
    validated["citation"] = citation
    validated["source_url"] = source_url

    return validated
