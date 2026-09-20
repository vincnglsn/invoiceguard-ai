"""
InvoiceGuard AI — Campagne Cold Emails Automatisée
Envoie les emails de prospection via Gmail SMTP avec rate limiting
et suivi de campagne. 100% automatique.

Usage:
    python campagne_emails_auto.py --liste prospects.csv --template pme
    python campagne_emails_auto.py --liste experts.csv --template ec
    python campagne_emails_auto.py --demo   # Simule sans envoyer

Formats CSV acceptés:
    email, prenom, societe, secteur, ca_estime (optionnel)
"""

import smtplib
import csv
import time
import os
import sys
import json
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ─── Templates ────────────────────────────────────────────────────────────────

TEMPLATES = {
    "pme": {
        "sujet": "Vos factures impayées vous coûtent {montant_estime}€ par an — solution IA",
        "corps": """Bonjour {prenom},

Je développe InvoiceGuard AI, un outil qui récupère automatiquement les factures impayées des PME françaises via l'intelligence artificielle.

En 30 secondes, l'IA génère la relance parfaite : bon ton, bonne urgence, conforme Loi LME — et l'envoie directement à votre client.

Résultat : -40% de DSO en 60 jours pour nos premiers utilisateurs.

Seriez-vous partant pour un essai gratuit de 14 jours ?
→ https://baby-rss-textile-rap.trycloudflare.com

(Aucune carte bancaire requise, 5 minutes pour importer vos factures)

Bonne journée,
Vincent
InvoiceGuard AI — Recouvrement intelligent pour PME françaises

P.S. : Si ce n'est pas votre problème prioritaire, pas de souci — mais si vos impayés dépassent 2% de votre CA, on peut récupérer la quasi-totalité en quelques semaines.
""",
    },
    "pme_btp": {
        "sujet": "BTP : 1 PME sur 3 dépose le bilan à cause des impayés — comment éviter ça",
        "corps": """Bonjour {prenom},

Le BTP est le secteur où les impayés font le plus de dégâts : délais de paiement non respectés, sous-traitants en attente, trésorerie sous tension.

J'ai construit InvoiceGuard AI spécialement pour ce contexte :
• Détection automatique des retards (Loi LME BTP)
• Relances calibrées selon l'ancienneté du chantier
• Mise en demeure juridique en 1 clic
• Rapport mensuel pour votre expert-comptable

Essai 14 jours gratuit → https://baby-rss-textile-rap.trycloudflare.com

Vincent | InvoiceGuard AI
""",
    },
    "ec": {
        "sujet": "Partenariat Expert-Comptable — 20% de commission récurrente sur vos clients PME",
        "corps": """Bonjour {prenom},

Je lance InvoiceGuard AI, un SaaS de recouvrement d'impayés pour PME françaises (IA + Loi LME).

Je recherche des experts-comptables partenaires pour recommander l'outil à leurs clients.

Ce que vous y gagnez :
• 20% de commission récurrente sur chaque abonnement souscrit
→ 1 client Pro (149€/mois) = 29,80€/mois à vie
→ 10 clients = 298€/mois passifs, sans effort

Ce que vos clients y gagnent :
• DSO réduit de 40% en 60 jours
• Rapport mensuel prêt à intégrer à votre reporting
• Conformité Loi LME garantie

Je peux vous montrer l'outil en 15 minutes en visio.
Créneau disponible cette semaine ?

Vincent | InvoiceGuard AI
→ https://baby-rss-textile-rap.trycloudflare.com
""",
    },
}

# ─── Envoi SMTP ───────────────────────────────────────────────────────────────

def envoyer_email_smtp(
    to: str,
    sujet: str,
    corps: str,
    gmail_user: str,
    gmail_password: str,
    expediteur_nom: str = "Vincent — InvoiceGuard AI",
    mode_demo: bool = False,
) -> dict:
    """Envoie un email via Gmail SMTP avec App Password."""
    if mode_demo:
        return {"success": True, "mode": "DEMO", "to": to}

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = sujet
        msg["From"]    = f"{expediteur_nom} <{gmail_user}>"
        msg["To"]      = to

        # Corps texte brut
        msg.attach(MIMEText(corps, "plain", "utf-8"))

        # Corps HTML minimal
        html_corps = corps.replace("\n", "<br>")
        html = f"""<html><body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;max-width:600px">
{html_corps}
<br><br>
<hr style="border:1px solid #eee">
<small style="color:#888">InvoiceGuard AI · <a href="https://invoiceguard.fr">invoiceguard.fr</a> · Se désabonner</small>
</body></html>"""
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, [to], msg.as_bytes())

        return {"success": True, "to": to}
    except Exception as e:
        return {"success": False, "to": to, "error": str(e)}


# ─── Personnalisation ─────────────────────────────────────────────────────────

def personnaliser(template: str, contact: dict) -> tuple[str, str]:
    ca = float(contact.get("ca_estime", 500000))
    montant_estime = int(ca * 0.035)  # 3.5% de taux d'impayés moyen

    variables = {
        "prenom":          contact.get("prenom", ""),
        "societe":         contact.get("societe", "votre entreprise"),
        "secteur":         contact.get("secteur", ""),
        "montant_estime":  f"{montant_estime:,}".replace(",", " "),
    }

    # Choisit le bon template
    tpl_key = template
    secteur = contact.get("secteur", "").lower()
    if template == "pme" and "btp" in secteur:
        tpl_key = "pme_btp"

    tpl = TEMPLATES.get(tpl_key, TEMPLATES["pme"])
    sujet = tpl["sujet"].format(**variables)
    corps = tpl["corps"].format(**variables)
    return sujet, corps


# ─── Suivi de campagne ────────────────────────────────────────────────────────

def log_campagne(result: dict, log_path: str):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({**result, "timestamp": datetime.now().isoformat()}, ensure_ascii=False) + "\n")


# ─── Main ─────────────────────────────────────────────────────────────────────

def lancer_campagne(
    liste_csv: str,
    template: str,
    gmail_user: str,
    gmail_password: str,
    mode_demo: bool = False,
    delai_secondes: float = 45.0,
    max_emails: int = 50,
):
    log_path = f"campagne_{template}_{datetime.now().strftime('%Y%m%d_%H%M')}.log"
    envoyes, erreurs = 0, 0

    print(f"\n{'='*60}")
    print(f"  InvoiceGuard AI — Campagne '{template.upper()}'")
    print(f"  Mode : {'DÉMONSTRATION' if mode_demo else 'PRODUCTION'}")
    print(f"  Liste : {liste_csv}")
    print(f"  Délai inter-email : {delai_secondes}s | Max : {max_emails}")
    print(f"{'='*60}\n")

    with open(liste_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        contacts = list(reader)

    total = min(len(contacts), max_emails)
    print(f"📧 {total} contacts à contacter\n")

    for i, contact in enumerate(contacts[:max_emails]):
        email = contact.get("email", "").strip()
        if not email or "@" not in email:
            print(f"  [{i+1}/{total}] ⏭  Email invalide : '{email}' — ignoré")
            continue

        sujet, corps = personnaliser(template, contact)
        result = envoyer_email_smtp(email, sujet, corps, gmail_user, gmail_password, mode_demo=mode_demo)
        log_campagne({**result, "sujet": sujet, "contact": contact}, log_path)

        icone = "✅" if result["success"] else "❌"
        mode_txt = " [DEMO]" if mode_demo else ""
        print(f"  [{i+1}/{total}] {icone}{mode_txt} {email} — {contact.get('prenom','')} {contact.get('societe','')}")

        if result["success"]:
            envoyes += 1
        else:
            erreurs += 1
            print(f"     → Erreur : {result.get('error','?')}")

        if i < total - 1 and not mode_demo:
            print(f"     ⏱  Pause {delai_secondes}s...")
            time.sleep(delai_secondes)

    print(f"\n{'='*60}")
    print(f"  ✅ Campagne terminée")
    print(f"  Envoyés : {envoyes} | Erreurs : {erreurs}")
    print(f"  Log : {log_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Campagne emails InvoiceGuard AI")
    parser.add_argument("--liste",    default="prospects_pme.csv", help="Fichier CSV de prospects")
    parser.add_argument("--template", default="pme", choices=["pme", "pme_btp", "ec"], help="Template email")
    parser.add_argument("--demo",     action="store_true", help="Mode démonstration (ne pas envoyer)")
    parser.add_argument("--max",      type=int, default=20, help="Nombre max d'emails")
    parser.add_argument("--delai",    type=float, default=45.0, help="Délai entre emails (secondes)")
    args = parser.parse_args()

    gmail_user     = os.environ.get("GMAIL_USER", "")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD", "")

    if not args.demo and (not gmail_user or not gmail_password):
        print("\n⚠️  Configuration email manquante !")
        print("\nAjoutez dans votre fichier .env :")
        print("  GMAIL_USER=votre@gmail.com")
        print("  GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx  (App Password Gmail)")
        print("\nComment créer un App Password Gmail :")
        print("  1. Allez sur myaccount.google.com/security")
        print("  2. Activez la validation en 2 étapes")
        print("  3. Cherchez 'Mots de passe d'application'")
        print("  4. Créez un mot de passe pour 'Courrier'")
        print("\nOu lancez en mode démo d'abord :")
        print("  python campagne_emails_auto.py --demo")
        sys.exit(1)

    if not os.path.exists(args.liste):
        # Crée un fichier de demo
        demo_csv = args.liste
        with open(demo_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["email", "prenom", "societe", "secteur", "ca_estime"])
            if args.template == "ec":
                w.writerows([
                    ["ec1@cabinet-dupont.fr", "Jean", "Cabinet Dupont", "Expert-Comptable", ""],
                    ["direction@leblanc-ec.fr", "Sophie", "Leblanc & Associés", "Expert-Comptable", ""],
                    ["contact@cabinet-martin.fr", "Pierre", "Cabinet Martin EC", "Expert-Comptable", ""],
                ])
            else:
                w.writerows([
                    ["daf@techsolutions.fr", "Marie", "TechSolutions SAS", "IT", "800000"],
                    ["contact@btprenov.fr", "Luc", "BTP Renov & Co", "BTP", "1200000"],
                    ["admin@logisticsexpress.fr", "Karim", "Logistics Express", "Transport", "2000000"],
                    ["direction@imprimerie-centrale.fr", "Anne", "Imprimerie Centrale", "Industrie", "400000"],
                    ["compta@gis.fr", "Thomas", "Groupe Immobilier Sud", "Immobilier", "5000000"],
                ])
        print(f"📄 Fichier exemple créé : {demo_csv}")

    lancer_campagne(
        liste_csv=args.liste,
        template=args.template,
        gmail_user=gmail_user,
        gmail_password=gmail_password,
        mode_demo=args.demo,
        delai_secondes=args.delai,
        max_emails=args.max,
    )
