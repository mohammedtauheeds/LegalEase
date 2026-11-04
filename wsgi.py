"""
LegalEase - Production WSGI Entry Point.
File: wsgi.py

Exposes the WSGI application object for production WSGI servers:
- Windows: Waitress (waitress-serve --host=127.0.0.1 --port=5000 wsgi:app)
- Linux: Gunicorn (gunicorn --workers=4 --bind 0.0.0.0:5000 wsgi:app)
- Containers: Docker / Kubernetes / Cloud Run / App Service

Loads the environment configuration ('production' by default) without enabling
debug mode or running developmental local servers upon module import.
"""

import logging
import os
import sys
from pathlib import Path

# Ensure application root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app
from config import Config

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("legalease.wsgi")

# 1. Determine environment ('production' by default for WSGI servers)
env_name = os.environ.get("WSGI_ENV", "production").lower()
logger.info(f"Initializing LegalEase WSGI application with environment: '{env_name}'")

# 2. Instantiate application factory
app = create_app(config_name=env_name)

# 3. WSGI Standard alias (supported by Gunicorn, Waitress, uWSGI, and PaaS providers)
application = app


if __name__ == "__main__":
    # Local fallback entry point if run directly with `python wsgi.py`
    host = os.environ.get("HOST", Config.HOST)
    port = int(os.environ.get("PORT", Config.PORT))

    try:
        import waitress
        logger.info(f"Serving LegalEase with Waitress WSGI on http://{host}:{port}")
        waitress.serve(app, host=host, port=port)
    except ImportError:
        logger.warning(
            "Waitress is not installed. Serving with standard WSGI development server. "
            "For production on Windows, install waitress: pip install waitress"
        )
        app.run(host=host, port=port, debug=False)
