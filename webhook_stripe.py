"""
InvoiceGuard AI -- Stripe Webhook Handler
Serveur Flask qui ecoute les evenements Stripe et met a jour
automatiquement la base de donnees (plan utilisateur, acces).

Port : 5000
Evenements traites :
  - checkout.session.completed    -> nouveau client
  - customer.subscription.created -> abonnement actif
  - customer.subscription.updated -> changement de plan
  - customer.subscription.deleted -> resiliation
  - invoice.payment_failed        -> echec paiement

Usage:
  python webhook_stripe.py

Configuration .env :
  STRIPE_SECRET_KEY=sk_live_...
  STRIPE_WEBHOOK_SECRET=whsec_...   (depuis le dashboard Stripe)
  TELEGRAM_TOKEN=...                (optionnel, pour les alertes)
  TELEGRAM_CHAT_ID=...              (optionnel)
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("webhook")

app = Flask(__name__)

STRIPE_SECRET_KEY    = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Mapping prix Stripe -> plan InvoiceGuard
PRICE_TO_PLAN = {}  # rempli dynamiquement depuis stripe_config.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "stripe_config.json")
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = json.load(f)
    for plan_name, info in cfg.items():
        PRICE_TO_PLAN[info.get("price_id", "")] = plan_name
    log.info("Stripe config chargee : %s plans", len(PRICE_TO_PLAN))


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_plan_from_price(price_id: str) -> str:
    return PRICE_TO_PLAN.get(price_id, "pro")


def notifier_telegram(message: str):
    """Envoie une notification Telegram au fondateur."""
    token   = os.environ.get("TELEGRAM_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return
    try:
        import urllib.request as ureq
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = json.dumps({"chat_id": chat_id, "text": message, "parse_mode": "HTML"}).encode()
        req = ureq.Request(url, data=data, headers={"Content-Type": "application/json"})
        ureq.urlopen(req, timeout=5)
    except Exception as e:
        log.warning("Telegram notification failed: %s", e)


def envoyer_email_bienvenue(email: str, nom: str, plan: str):
    """Envoie l'email de bienvenue au nouveau client."""
    try:
        from modules.email_bienvenue import envoyer_bienvenue
        envoyer_bienvenue(email, nom, plan)
        log.info("Email bienvenue envoye a %s (%s)", email, plan)
    except Exception as e:
        log.warning("Email bienvenue echoue: %s", e)


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload   = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")

    # Verification signature Stripe
    if STRIPE_WEBHOOK_SECRET:
        try:
            import stripe
            stripe.api_key = STRIPE_SECRET_KEY
            event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        except Exception as e:
            log.warning("Signature Stripe invalide: %s", e)
            return jsonify({"error": "Invalid signature"}), 400
    else:
        # Mode dev sans verification
        try:
            event = json.loads(payload)
        except Exception:
            return jsonify({"error": "Invalid JSON"}), 400

    event_type = event.get("type", "")
    data       = event.get("data", {}).get("object", {})
    log.info("Evenement Stripe recu: %s", event_type)

    try:
        from modules import database as db

        # ── Nouveau paiement checkout ──────────────────────────────────────────
        if event_type == "checkout.session.completed":
            email  = data.get("customer_details", {}).get("email", "")
            nom    = data.get("customer_details", {}).get("name", "") or "Client"
            amount = data.get("amount_total", 0) / 100

            # Determine le plan selon le montant
            if amount >= 350:    plan = "scale"
            elif amount >= 130:  plan = "pro"
            else:                plan = "starter"

            uid = db.upsert_user(email, nom, plan=plan)
            log.info("Nouveau client: %s (%s) -> plan %s", email, nom, plan)

            envoyer_email_bienvenue(email, nom, plan)
            notifier_telegram(
                f"<b>NOUVEAU CLIENT</b>\n"
                f"Email: {email}\n"
                f"Nom: {nom}\n"
                f"Plan: {plan.upper()}\n"
                f"Montant: {amount}EUR"
            )

        # ── Abonnement cree ───────────────────────────────────────────────────
        elif event_type == "customer.subscription.created":
            customer_id = data.get("customer", "")
            price_id    = data.get("items", {}).get("data", [{}])[0].get("price", {}).get("id", "")
            plan        = get_plan_from_price(price_id)
            status      = data.get("status", "")
            log.info("Abonnement cree: customer=%s plan=%s status=%s", customer_id, plan, status)

        # ── Plan change ───────────────────────────────────────────────────────
        elif event_type == "customer.subscription.updated":
            price_id = data.get("items", {}).get("data", [{}])[0].get("price", {}).get("id", "")
            plan     = get_plan_from_price(price_id)
            status   = data.get("status", "")
            log.info("Abonnement mis a jour: plan=%s status=%s", plan, status)

            if status == "active":
                # Met a jour le plan dans la DB via customer email
                # (necessite de recuperer l'email depuis Stripe API)
                log.info("Plan actif: %s", plan)

        # ── Resiliation ───────────────────────────────────────────────────────
        elif event_type == "customer.subscription.deleted":
            log.info("Abonnement resilie")
            notifier_telegram("<b>RESILIATION</b>\nUn client a resilie son abonnement.")

        # ── Echec paiement ────────────────────────────────────────────────────
        elif event_type == "invoice.payment_failed":
            email  = data.get("customer_email", "?")
            amount = data.get("amount_due", 0) / 100
            log.warning("Echec paiement: %s -> %.2fEUR", email, amount)
            notifier_telegram(
                f"<b>ECHEC PAIEMENT</b>\n"
                f"Email: {email}\n"
                f"Montant: {amount:.2f}EUR"
            )

    except Exception as e:
        log.error("Erreur traitement webhook: %s", e)
        return jsonify({"error": str(e)}), 500

    return jsonify({"received": True}), 200


@app.route("/webhook/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


@app.route("/webhook/test-lead", methods=["POST"])
def test_lead():
    """Endpoint de test pour capturer un lead manuellement."""
    data  = request.get_json() or {}
    email = data.get("email", "")
    nom   = data.get("nom", "")
    if email:
        from modules import database as db
        db.save_lead(email, nom, data.get("societe",""), "", data.get("ca",0), "api")
        notifier_telegram(f"<b>NOUVEAU LEAD</b>\n{email} - {nom}")
        return jsonify({"success": True})
    return jsonify({"error": "email manquant"}), 400


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sep = "=" * 60
    print(f"\n{sep}")
    print("  InvoiceGuard AI -- Stripe Webhook Server")
    print(f"{sep}")
    print("  Endpoint : http://localhost:5000/webhook/stripe")
    print("  Health   : http://localhost:5000/webhook/health")
    print("")
    print("  Config Stripe Dashboard :")
    print("  -> Webhooks -> Add endpoint")
    print("  -> URL: https://VOTRE_DOMAINE/webhook/stripe")
    print("  -> Events: checkout.session.completed,")
    print("             customer.subscription.*,")
    print("             invoice.payment_failed")
    print(f"{sep}\n")

    if not STRIPE_WEBHOOK_SECRET:
        print("  [WARN] STRIPE_WEBHOOK_SECRET non configure")
        print("  -> Mode dev sans verification de signature\n")

    app.run(host="0.0.0.0", port=5000, debug=False)
