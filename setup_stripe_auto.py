"""
InvoiceGuard AI — Setup Stripe Automatique
Lance ce script UNE SEULE FOIS avec votre clé Stripe pour créer
les 3 produits + 3 payment links automatiquement.

Usage:
    python setup_stripe_auto.py --key sk_live_VOTRE_CLE
    ou ajoutez STRIPE_SECRET_KEY dans .env
"""

import sys
import os
import json
import requests
import argparse
from dotenv import load_dotenv

load_dotenv()

PRODUITS = [
    {
        "nom":         "InvoiceGuard AI — Starter",
        "description": "Idéal pour les TPE et indépendants. 50 factures/mois, dashboard trésorerie, relances email.",
        "prix_centimes": 4900,
        "plan_id":     "starter",
        "trial_days":  14,
    },
    {
        "nom":         "InvoiceGuard AI — Pro",
        "description": "Le plan le plus populaire pour les PME. Factures illimitées, email + SMS, campagnes en masse, rapport PDF, intégrations comptables.",
        "prix_centimes": 14900,
        "plan_id":     "pro",
        "trial_days":  14,
    },
    {
        "nom":         "InvoiceGuard AI — Scale",
        "description": "Pour les ETI et cabinets experts-comptables. Multi-utilisateurs, API complète, espace partenaire EC, SLA 99.9%, onboarding dédié.",
        "prix_centimes": 39900,
        "plan_id":     "scale",
        "trial_days":  14,
    },
]

STRIPE_BASE = "https://api.stripe.com/v1"


def stripe_post(endpoint: str, data: dict, api_key: str) -> dict:
    r = requests.post(
        f"{STRIPE_BASE}/{endpoint}",
        data=data,
        auth=(api_key, ""),
        timeout=15,
    )
    if r.status_code not in (200, 201):
        print(f"  ❌ Erreur Stripe {r.status_code}: {r.text[:200]}")
        return {}
    return r.json()


def setup_stripe(api_key: str):
    print("\n" + "=" * 60)
    print("  🚀 InvoiceGuard AI — Configuration Stripe Automatique")
    print("=" * 60)

    results = {}

    for produit in PRODUITS:
        print(f"\n📦 Création du plan '{produit['plan_id'].upper()}'...")

        # 1. Créer le produit
        prod = stripe_post("products", {
            "name":        produit["nom"],
            "description": produit["description"],
        }, api_key)
        if not prod:
            continue
        prod_id = prod["id"]
        print(f"   ✅ Produit créé : {prod_id}")

        # 2. Créer le prix (abonnement mensuel)
        price = stripe_post("prices", {
            "product":          prod_id,
            "currency":         "eur",
            "unit_amount":      produit["prix_centimes"],
            "recurring[interval]": "month",
        }, api_key)
        if not price:
            continue
        price_id = price["id"]
        print(f"   ✅ Prix créé : {price_id} ({produit['prix_centimes']/100:.0f}€/mois)")

        # 3. Créer le Payment Link
        link_data = {
            "line_items[0][price]":    price_id,
            "line_items[0][quantity]": "1",
            "allow_promotion_codes":   "true",
            "after_completion[type]":  "redirect",
            "after_completion[redirect][url]": "http://localhost:8502?success=1",
        }
        if produit["trial_days"] > 0:
            link_data["subscription_data[trial_period_days]"] = str(produit["trial_days"])

        pl = stripe_post("payment_links", link_data, api_key)
        if not pl:
            continue
        payment_link_url = pl["url"]
        print(f"   ✅ Payment Link : {payment_link_url}")

        results[produit["plan_id"]] = {
            "product_id":   prod_id,
            "price_id":     price_id,
            "payment_link": payment_link_url,
        }

    if not results:
        print("\n❌ Aucun produit créé. Vérifiez votre clé API Stripe.")
        return

    # ─── Sauvegarde dans stripe_config.json ───────────────────────────────────
    config_path = os.path.join(os.path.dirname(__file__), "stripe_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Configuration sauvegardée dans : {config_path}")

    # ─── Patch automatique de invoiceguard_pricing.py ─────────────────────────
    pricing_path = os.path.join(os.path.dirname(__file__), "invoiceguard_pricing.py")
    if os.path.exists(pricing_path):
        with open(pricing_path, "r", encoding="utf-8") as f:
            content = f.read()
        for plan_id, info in results.items():
            content = content.replace(
                f"https://buy.stripe.com/VOTRE_LIEN_{plan_id.upper()}",
                info["payment_link"],
            )
        with open(pricing_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ invoiceguard_pricing.py mis à jour avec les vrais liens Stripe !")

    # ─── Résumé ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  ✅ Configuration Stripe terminée avec succès !")
    print("=" * 60)
    print("\nVos Payment Links :")
    for plan, info in results.items():
        print(f"  {plan:10s} → {info['payment_link']}")

    print("\nProchaine étape :")
    print("  Streamlit run invoiceguard_pricing.py --server.port 8507")
    print("  → Les liens Stripe sont maintenant actifs !\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup Stripe pour InvoiceGuard AI")
    parser.add_argument("--key", help="Clé secrète Stripe (sk_live_... ou sk_test_...)")
    args = parser.parse_args()

    api_key = args.key or os.environ.get("STRIPE_SECRET_KEY")

    if not api_key:
        print("\n⚠️  Clé Stripe manquante !")
        print("\nOption 1 — Argument :")
        print("   python setup_stripe_auto.py --key sk_live_VOTRE_CLE\n")
        print("Option 2 — Variable d'environnement (.env) :")
        print("   STRIPE_SECRET_KEY=sk_live_VOTRE_CLE")
        print("\nOù trouver votre clé ?")
        print("   https://dashboard.stripe.com/apikeys")
        sys.exit(1)

    setup_stripe(api_key)
