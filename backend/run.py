"""
Flask Application Entry Point (WSGI).
Run with: python run.py or gunicorn -w 4 -b 0.0.0.0:5000 run:app
"""

import os
from app import create_app
from app.utils.env_validator import print_env_status_summary

app = create_app()

if __name__ == "__main__":
    print_env_status_summary()
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    print(f"[*] Starting Ghana Fintech Platform on http://127.0.0.1:{port}")
    print(f"[*] Interactive OpenAPI Docs at: http://127.0.0.1:{port}/api/docs/")
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
