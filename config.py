"""
LegalEase - Centralized Configuration Module
Manages application settings, AI model selection, database URIs,
external API endpoints, official legal resources, and security parameters.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

# Load environment variables from .env if present
load_dotenv(dotenv_path=ENV_PATH)


class Config:
    """Base application configuration with secure defaults."""

    # Application Info
    APP_NAME = "LegalEase"
    APP_VERSION = "1.0.0"
    SECRET_KEY = os.environ.get("SECRET_KEY", "legalease-insecure-dev-key-change-in-production")

    # Server Settings
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", 5000))
    DEBUG = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")

    # Database Configuration (SQLite stored locally in instance/ folder)
    INSTANCE_DIR = BASE_DIR / "instance"
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_DB_PATH = INSTANCE_DIR / "legalease.db"

    _env_db_url = os.environ.get("DATABASE_URL")
    if _env_db_url and _env_db_url.startswith("sqlite:///") and ":memory:" not in _env_db_url:
        _rel_path = _env_db_url.replace("sqlite:///", "")
        if not Path(_rel_path).is_absolute():
            _abs_path = (BASE_DIR / _rel_path).resolve()
            _abs_path.parent.mkdir(parents=True, exist_ok=True)
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{_abs_path.as_posix()}"
        else:
            SQLALCHEMY_DATABASE_URI = _env_db_url
    elif _env_db_url:
        SQLALCHEMY_DATABASE_URI = _env_db_url
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AI Configuration (Official Google GenAI SDK)
    # Centrally configurable supported Gemini Flash model
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    GEMINI_TEMPERATURE = 0.2  # Low temperature for factual precision
    GEMINI_MAX_OUTPUT_TOKENS = 1200

    # Courts & Cases API Configuration
    COURTS_CASES_BASE_URL = os.environ.get(
        "COURTS_CASES_BASE_URL", "https://courtsandcases.com"
    ).rstrip("/")
    COURTS_CASES_API_KEY = os.environ.get("COURTS_CASES_API_KEY", "")
    EXTERNAL_API_TIMEOUT = int(os.environ.get("EXTERNAL_API_TIMEOUT", 5))

    # NLP & Machine Learning Settings
    DATA_DIR = BASE_DIR / "data"
    FAQ_DATASET_PATH = DATA_DIR / "legal_faq.csv"
    NLP_SIMILARITY_THRESHOLD = float(os.environ.get("NLP_SIMILARITY_THRESHOLD", 0.75))

    # Supported Legal Topics (20 distinct Indian Legal Awareness domains)
    LEGAL_TOPICS = [
        "Indian Constitution",
        "Fundamental Rights",
        "Fundamental Duties",
        "Consumer Protection",
        "Cybercrime and Online Fraud",
        "Women's Rights and Legal Protection",
        "Family Law",
        "Marriage and Divorce",
        "Property and Inheritance",
        "Employment and Labour Rights",
        "Criminal Law",
        "Civil Law",
        "Traffic Rules and Road Safety",
        "Right to Information (RTI)",
        "Digital Privacy and Data Protection",
        "Banking and Financial Fraud",
        "Tenant and Rental Rights",
        "Legal Complaint Procedures",
        "Police Complaint and FIR Procedures",
        "Legal Aid and Access to Justice",
    ]

    # Official Indian Legal Resources & Portals
    OFFICIAL_LEGAL_SOURCES = {
        "india_code": {
            "title": "India Code - Digital Repository of All Central and State Acts",
            "url": "https://www.indiacode.nic.in/",
            "type": "Official Legislation",
        },
        "supreme_court": {
            "title": "Supreme Court of India (Official Portal)",
            "url": "https://www.sci.gov.in/",
            "type": "Court Judgment",
        },
        "ecourts": {
            "title": "eCourts Services - Integrated Mission Mode Project",
            "url": "https://ecourts.gov.in/",
            "type": "Court Judgment",
        },
        "cybercrime": {
            "title": "National Cyber Crime Reporting Portal",
            "url": "https://cybercrime.gov.in/",
            "type": "Government Resource",
            "helpline": "1930",
        },
        "consumer": {
            "title": "National Consumer Helpline (NCH - INGRAM)",
            "url": "https://consumerhelpline.gov.in/",
            "type": "Government Resource",
            "helpline": "1915",
        },
        "nalsa": {
            "title": "National Legal Services Authority (NALSA) - Free Legal Aid",
            "url": "https://nalsa.gov.in/",
            "type": "Legal Aid Resource",
            "helpline": "15100",
        },
        "national_portal": {
            "title": "National Portal of India",
            "url": "https://www.india.gov.in/",
            "type": "Government Resource",
        },
    }

    # Emergency Helplines Directory
    EMERGENCY_HELPLINES = {
        "all_emergency": {
            "service": "Emergency Response Support System (ERSS)",
            "number": "112",
            "scope": "Police, Fire, Ambulance pan-India",
        },
        "cybercrime": {
            "service": "National Cyber Crime Helpline",
            "number": "1930",
            "scope": "Financial cyber frauds and digital crime reporting",
        },
        "consumer": {
            "service": "National Consumer Helpline",
            "number": "1915",
            "scope": "Consumer grievances and unfair trade practices",
        },
        "women_safety": {
            "service": "Women Helpline",
            "number": "1091 / 181",
            "scope": "Women in distress and domestic violence assistance",
        },
        "legal_aid": {
            "service": "NALSA Legal Aid Helpline",
            "number": "15100",
            "scope": "Free legal aid for eligible citizens under Legal Services Authorities Act",
        },
    }

    # Mandatory Legal Disclaimer
    LEGAL_DISCLAIMER = (
        "LegalEase provides general legal awareness and educational information about Indian laws. "
        "It does not provide professional legal advice and is not a substitute for consulting a qualified advocate. "
        "Laws and procedures may change. Please verify important legal matters using official sources "
        "or seek professional legal assistance."
    )


class DevelopmentConfig(Config):
    """Configuration for local development."""
    DEBUG = True


class TestingConfig(Config):
    """Configuration for automated test execution."""
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    NLP_SIMILARITY_THRESHOLD = 0.60


class ProductionConfig(Config):
    """Configuration for production deployment."""
    DEBUG = False


# Map environment names to configuration classes
CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env_name=None):
    """Retrieve configuration based on environment name or FLASK_ENV."""
    if not env_name:
        env_name = os.environ.get("FLASK_ENV", "development").lower()
    return CONFIG_MAP.get(env_name, DevelopmentConfig)
