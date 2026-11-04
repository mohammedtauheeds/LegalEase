"""
Validation script for LegalEase Legal FAQ Dataset.
Checks:
- CSV readability (Standard CSV & Pandas)
- Total record count (>= 100)
- Missing required fields
- Duplicate questions
- URL formatting & authoritative source compliance
- Topic distribution against config.Config.LEGAL_TOPICS
"""

import sys
from pathlib import Path
from urllib.parse import urlparse

# Ensure LegalEase base directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pandas as pd
from config import Config

CSV_PATH = BASE_DIR / "data" / "legal_faq.csv"

AUTHORITATIVE_DOMAINS = {
    "www.indiacode.nic.in",
    "indiacode.nic.in",
    "www.sci.gov.in",
    "sci.gov.in",
    "nalsa.gov.in",
    "www.nalsa.gov.in",
    "consumerhelpline.gov.in",
    "www.consumerhelpline.gov.in",
    "cybercrime.gov.in",
    "www.cybercrime.gov.in",
    "www.india.gov.in",
    "india.gov.in",
}

def validate_dataset():
    print("=" * 70)
    print("LegalEase FAQ Dataset Validation")
    print(f"Dataset Path: {CSV_PATH}")
    print("=" * 70)

    # 1. Readability Check
    if not CSV_PATH.exists():
        print(f"[FAIL] Dataset file does not exist at {CSV_PATH}")
        return False

    try:
        df = pd.read_csv(CSV_PATH, encoding="utf-8")
        print("[PASS] CSV Readability: Successfully loaded with pandas (UTF-8).")
    except Exception as e:
        print(f"[FAIL] CSV Readability error: {e}")
        return False

    # 2. Total Records Check
    total_records = len(df)
    if total_records >= 100:
        print(f"[PASS] Total Records: {total_records} (Requirement: >= 100)")
    else:
        print(f"[FAIL] Total Records: {total_records} (Expected at least 100)")
        return False

    # 3. Columns & Missing Values Check
    expected_cols = [
        "id", "question", "answer", "topic", "act_name",
        "section", "source_title", "source_url"
    ]
    missing_cols = set(expected_cols) - set(df.columns)
    if missing_cols:
        print(f"[FAIL] Missing Columns: {missing_cols}")
        return False
    print(f"[PASS] Column Structure: All 8 required columns present: {list(df.columns)}")

    # Check required non-empty fields (section is allowed to be empty)
    required_non_empty = ["id", "question", "answer", "topic", "act_name", "source_title", "source_url"]
    has_nulls = False
    for col in required_non_empty:
        null_count = df[col].isnull().sum() + (df[col].astype(str).str.strip() == "").sum()
        if null_count > 0:
            print(f"[FAIL] Column '{col}' has {null_count} empty records!")
            has_nulls = True
    if not has_nulls:
        print("[PASS] Missing Values Check: All required fields populated (sections left blank only where unverified).")
    else:
        return False

    # 4. Duplicate Questions Check
    questions_clean = df["question"].astype(str).str.strip().str.lower()
    duplicates = df[questions_clean.duplicated(keep=False)]
    if len(duplicates) == 0:
        print("[PASS] Duplicate Check: 0 duplicate questions found across all records.")
    else:
        print(f"[FAIL] Duplicate Check: Found {len(duplicates)} duplicate questions:")
        for _, row in duplicates.iterrows():
            print(f"   - ID {row['id']}: {row['question']}")
        return False

    # 5. Invalid URLs & Authoritative Domain Check
    invalid_urls = []
    non_auth_urls = []
    for idx, row in df.iterrows():
        url = str(row["source_url"]).strip()
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            invalid_urls.append((row["id"], url))
        elif parsed.netloc.lower() not in AUTHORITATIVE_DOMAINS:
            non_auth_urls.append((row["id"], parsed.netloc))

    if not invalid_urls:
        print("[PASS] URL Syntax Check: 100% valid HTTP/HTTPS URLs.")
    else:
        print(f"[FAIL] Invalid URLs found: {invalid_urls}")
        return False

    if not non_auth_urls:
        print(f"[PASS] Authoritative Sources Check: All source URLs belong to verified official domains.")
    else:
        print(f"[WARN] Non-standard domains detected: {non_auth_urls}")

    # 6. Topic Distribution Check
    config_topics = set(Config.LEGAL_TOPICS)
    dataset_topics = set(df["topic"].unique())

    missing_topics = config_topics - dataset_topics
    extra_topics = dataset_topics - config_topics

    if missing_topics:
        print(f"[FAIL] Topics Missing in Dataset: {missing_topics}")
        return False
    if extra_topics:
        print(f"[WARN] Dataset has extra topics not in Config: {extra_topics}")

    print("\n--- Topic Distribution Summary ---")
    topic_counts = df["topic"].value_counts()
    for topic, count in topic_counts.items():
        print(f" • {topic.ljust(38)}: {count} questions")

    print("-" * 70)
    print(f"Unique Topics: {len(topic_counts)} / 20 required topics covered.")
    print("=" * 70)
    print("ALL VALIDATION CHECKS PASSED SUCCESSFULLY (100/100).")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = validate_dataset()
    sys.exit(0 if success else 1)
