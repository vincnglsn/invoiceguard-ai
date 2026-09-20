"""
InvoiceGuard AI -- Notifications Fondateur
Configure les alertes Telegram en temps reel :
  - Nouveau lead captu re
  - Nouveau client payant
  - Echec paiement
  - Relance envoyee avec succes
  - Rapport hebdomadaire automatique

Usage:
  python setup_telegram.py          # Guide de configuration
  python setup_telegram.py --test   # Test la connexion
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()


def send_telegram(token: str, chat_id: str, message: str, parse_mode: str = "HTML") -> bool:
    """Envoie un message Telegram."""
    try:
        url  = f"https://api.telegram.org/bot{token}/sendMessage"
        data = json.dumps({
            "chat_id":    chat_id,
            "text":       message,
            "parse_mode": parse_mode,
        }).encode("utf-8")
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            resp = json.loads(r.read())
            return resp.get("ok", False)
    except Exception as e:
        print(f"Erreur Telegram: {e}")
        return False


def test_connexion(token: str, chat_id: str) -> bool:
    """Teste la connexion Telegram."""
    msg = f"""<b>InvoiceGuard AI - Test de connexion</b>

Les notifications sont activees !

Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}

Vous recevrez des alertes pour :
- Nouveau lead (formulaire)
- Nouveau client payant
- Echec de paiement
- Rapport hebdomadaire

<i>InvoiceGuard AI - Made in France</i>"""
    return send_telegram(token, chat_id, msg)


def rapport_hebdomadaire(token: str, chat_id: str):
    """Envoie le rapport hebdomadaire au fondateur."""
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from modules import database as db

        stats   = db.get_founder_stats()
        users   = db.get_all_users()
        leads   = db.get_leads()

        # MRR calcule
        prix   = {"trial": 0, "starter": 49, "pro": 149, "scale": 399}
        mrr    = users["plan"].map(prix).fillna(0).sum() if not users.empty else 0

        # Leads cette semaine
        semaine_passee = (date.today() - timedelta(days=7)).isoformat()
        leads_semaine  = len(leads[leads["created_at"] >= semaine_passee]) if not leads.empty else 0

        msg = f"""<b>InvoiceGuard AI - Rapport Hebdomadaire</b>
{date.today().strftime('%d/%m/%Y')}

<b>Revenus</b>
MRR : {mrr:.0f} EUR
ARR : {mrr * 12:.0f} EUR

<b>Utilisateurs</b>
Total : {stats['total_users']}
Leads totaux : {stats['total_leads']}
Leads cette semaine : {leads_semaine}

<b>Usage</b>
Relances IA : {stats['total_relances']}
Taux de succes : {stats['taux_succes_relances']:.0f}%

<i>Objectif semaine : +2 utilisateurs, +10 leads</i>"""

        return send_telegram(token, chat_id, msg)
    except Exception as e:
        print(f"Erreur rapport: {e}")
        return False


def sauvegarder_config(token: str, chat_id: str):
    """Sauvegarde dans .env."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    # Lit le .env existant
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = [l for l in f.readlines()
                     if not l.startswith("TELEGRAM_TOKEN") and not l.startswith("TELEGRAM_CHAT_ID")]
    lines.append(f"\nTELEGRAM_TOKEN={token}\n")
    lines.append(f"TELEGRAM_CHAT_ID={chat_id}\n")
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("[OK] Configuration sauvegardee dans .env")


def guide_creation_bot():
    """Guide pas-a-pas pour creer le bot Telegram."""
    print("""
============================================================
  InvoiceGuard AI -- Configuration Notifications Telegram
============================================================

ETAPE 1 : Creer votre bot Telegram (2 minutes)
  1. Ouvrez Telegram et cherchez @BotFather
  2. Envoyez /newbot
  3. Donnez un nom : "InvoiceGuard Alertes"
  4. Donnez un username : invoiceguard_alertes_bot
  5. BotFather vous envoie un TOKEN -- copiez-le

ETAPE 2 : Obtenir votre Chat ID
  1. Demarrez une conversation avec votre nouveau bot
  2. Envoyez n'importe quel message
  3. Ouvrez : https://api.telegram.org/bot<VOTRE_TOKEN>/getUpdates
  4. Cherchez "chat":{"id":XXXXXXXX} -- c'est votre Chat ID

ETAPE 3 : Configurer
  Ajoutez dans votre .env :
    TELEGRAM_TOKEN=1234567890:ABCdef...
    TELEGRAM_CHAT_ID=123456789

  Ou lancez :
    python setup_telegram.py --token VOTRE_TOKEN --chat VOTRE_CHAT_ID

ETAPE 4 : Tester
  python setup_telegram.py --test
============================================================
""")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Setup Telegram InvoiceGuard AI")
    parser.add_argument("--token",   help="Token du bot Telegram")
    parser.add_argument("--chat",    help="Chat ID Telegram")
    parser.add_argument("--test",    action="store_true", help="Tester la connexion")
    parser.add_argument("--rapport", action="store_true", help="Envoyer le rapport maintenant")
    args = parser.parse_args()

    token   = args.token   or os.environ.get("TELEGRAM_TOKEN", "")
    chat_id = args.chat    or os.environ.get("TELEGRAM_CHAT_ID", "")

    if not token or not chat_id:
        guide_creation_bot()
        print("\nPour configurer maintenant :")
        print("  python setup_telegram.py --token VOTRE_TOKEN --chat VOTRE_CHAT_ID")
        sys.exit(0)

    if args.token and args.chat:
        sauvegarder_config(token, chat_id)

    if args.rapport:
        print("Envoi du rapport hebdomadaire...")
        ok = rapport_hebdomadaire(token, chat_id)
        print("[OK] Rapport envoye !" if ok else "[ERR] Echec envoi")
        sys.exit(0)

    print("Test de connexion Telegram...")
    ok = test_connexion(token, chat_id)
    if ok:
        print("[OK] Connexion Telegram etablie !")
        print("     Vous avez recu un message de confirmation.")
        sauvegarder_config(token, chat_id)
    else:
        print("[ERR] Connexion echouee. Verifiez votre token et chat ID.")
        sys.exit(1)
