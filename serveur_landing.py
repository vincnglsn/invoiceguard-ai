"""
InvoiceGuard AI — Serveur Landing Page avec API Lead Capture
Lance un serveur HTTP local qui sert la landing page ET capture les leads
en temps réel dans la base SQLite.

Usage:
    python serveur_landing.py          # port 8000 par défaut
    python serveur_landing.py --port 80
"""

import http.server
import json
import os
import sys
import argparse
import urllib.parse
from http import HTTPStatus
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

LANDING_DIR = os.path.join(os.path.dirname(__file__), "invoiceguard_landing")


class InvoiceGuardHandler(http.server.SimpleHTTPRequestHandler):
    """Handler HTTP avec endpoint /api/lead pour la capture."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=LANDING_DIR, **kwargs)

    def log_message(self, format, *args):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [{ts}] {args[0]} {args[1]}")

    def do_POST(self):
        if self.path == "/api/lead":
            self._handle_lead()
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def _handle_lead(self):
        """Capture un lead depuis le formulaire landing page."""
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")

        # Accepte JSON et form-urlencoded
        try:
            if self.headers.get("Content-Type", "").startswith("application/json"):
                data = json.loads(body)
            else:
                data = dict(urllib.parse.parse_qsl(body))
        except Exception:
            data = {}

        email   = data.get("email", "").strip()
        nom     = data.get("nom", "").strip()
        societe = data.get("societe", "").strip()
        ca      = float(data.get("ca", 0) or 0)
        source  = data.get("source", "landing")

        if email and "@" in email:
            try:
                from modules import database as db
                saved = db.save_lead(email, nom, societe, "", ca, source)
                ts = datetime.now().strftime("%d/%m %H:%M")
                if saved:
                    print(f"\n  🎯 NOUVEAU LEAD [{ts}] : {email} — {nom} ({societe})")
                    response = {"success": True, "message": "Lead enregistré"}
                else:
                    response = {"success": True, "message": "Déjà enregistré"}
            except Exception as e:
                response = {"success": False, "error": str(e)}
        else:
            response = {"success": False, "error": "Email invalide"}

        # CORS headers pour la landing page
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        # Route /leads pour voir les leads en JSON (debug)
        if self.path == "/leads":
            try:
                from modules import database as db
                leads = db.get_leads()
                data = leads.to_dict(orient="records") if not leads.empty else []
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data, ensure_ascii=False, default=str).encode())
            except Exception as e:
                self.send_error(500, str(e))
            return
        super().do_GET()


def run(port: int = 8000):
    os.chdir(LANDING_DIR)
    server = http.server.HTTPServer(("", port), InvoiceGuardHandler)

    sep = "=" * 60
    print(sep)
    print("  InvoiceGuard AI -- Serveur Landing Page")
    print(sep)
    print(f"  Landing page : http://localhost:{port}")
    print(f"  API leads    : http://localhost:{port}/api/lead")
    print(f"  Voir leads   : http://localhost:{port}/leads")
    print("  Ctrl+C pour arreter")
    print(sep + "\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Serveur arrêté.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    run(args.port)
