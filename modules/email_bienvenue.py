"""
InvoiceGuard AI -- Module Email de Bienvenue
Envoie un email HTML professionnel au nouveau client via Resend
(ou SMTP Gmail en fallback).
"""

import os
import json
import requests
from datetime import datetime

RESEND_URL = "https://api.resend.com/emails"

PLANS_INFO = {
    "starter": {
        "nom":   "Starter",
        "prix":  "49EUR/mois",
        "emoji": "🚀",
        "features": [
            "50 factures par mois",
            "Relances email personnalisees",
            "Dashboard tresorerie",
            "Score de risque IA",
            "Support par email",
        ],
    },
    "pro": {
        "nom":   "Pro",
        "prix":  "149EUR/mois",
        "emoji": "⭐",
        "features": [
            "Factures illimitees",
            "Email + SMS",
            "Campagnes en masse",
            "Rapport PDF mensuel",
            "Agent IA negociateur",
            "Integrations comptables",
            "Support prioritaire",
        ],
    },
    "scale": {
        "nom":   "Scale",
        "prix":  "399EUR/mois",
        "emoji": "🏢",
        "features": [
            "Tout le plan Pro",
            "Multi-utilisateurs (5)",
            "API complete",
            "Espace partenaire EC",
            "Dashboard CFO avance",
            "SLA 99.9%",
            "Onboarding dedie",
        ],
    },
    "trial": {
        "nom":   "Essai gratuit",
        "prix":  "Gratuit 14 jours",
        "emoji": "🎁",
        "features": [
            "Toutes les fonctionnalites Pro",
            "14 jours sans carte bancaire",
            "Support inclus",
        ],
    },
}


def _build_html(nom: str, plan: str, app_url: str = "http://localhost:8502") -> str:
    info = PLANS_INFO.get(plan, PLANS_INFO["trial"])
    features_html = "".join(
        f'<li style="padding:4px 0;border-bottom:1px solid #1F2937">'
        f'<span style="color:#00D4AA;font-weight:700">✓</span> {f}'
        f'</li>'
        for f in info["features"]
    )
    prenom = nom.split()[0] if nom else "là"

    return f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0A0F1E;font-family:Arial,sans-serif;color:#F9FAFB">
<table width="100%" cellpadding="0" cellspacing="0">
<tr><td align="center" style="padding:40px 20px">
<table width="600" style="background:#111827;border-radius:16px;overflow:hidden;border:1px solid #374151">

  <!-- Header -->
  <tr><td style="background:#0A0F1E;padding:30px 40px;text-align:center;border-bottom:2px solid #00D4AA">
    <p style="color:#00D4AA;font-size:28px;font-weight:900;margin:0">🛡️ InvoiceGuard AI</p>
    <p style="color:#9CA3AF;font-size:13px;margin:6px 0 0">Recouvrement intelligent pour PME françaises</p>
  </td></tr>

  <!-- Hero -->
  <tr><td style="padding:40px 40px 20px;text-align:center">
    <p style="font-size:40px;margin:0">{info["emoji"]}</p>
    <h1 style="color:#F9FAFB;font-size:26px;margin:12px 0 8px">Bienvenue {prenom} !</h1>
    <p style="color:#9CA3AF;font-size:15px;margin:0">
      Votre compte InvoiceGuard AI <strong style="color:#00D4AA">{info["nom"]}</strong> est actif.
    </p>
  </td></tr>

  <!-- CTA principal -->
  <tr><td style="padding:20px 40px;text-align:center">
    <a href="{app_url}" style="display:inline-block;background:#00D4AA;color:#000;font-weight:800;
      font-size:16px;padding:14px 32px;border-radius:10px;text-decoration:none">
      Accéder à mon dashboard →
    </a>
    <p style="color:#6B7280;font-size:12px;margin:10px 0 0">{app_url}</p>
  </td></tr>

  <!-- Features -->
  <tr><td style="padding:20px 40px">
    <div style="background:#1F2937;border-radius:12px;padding:24px">
      <p style="color:#00D4AA;font-weight:700;font-size:13px;text-transform:uppercase;
        letter-spacing:.05em;margin:0 0 16px">Votre plan {info["nom"]} inclut :</p>
      <ul style="list-style:none;margin:0;padding:0;color:#F9FAFB;font-size:14px">
        {features_html}
      </ul>
    </div>
  </td></tr>

  <!-- 3 etapes -->
  <tr><td style="padding:20px 40px">
    <p style="color:#F9FAFB;font-weight:700;font-size:16px;margin:0 0 16px">
      Prêt en 3 étapes :
    </p>
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td style="width:33%;padding:12px;text-align:center;background:#1F2937;border-radius:8px">
          <p style="color:#00D4AA;font-size:24px;font-weight:900;margin:0">1</p>
          <p style="color:#F9FAFB;font-size:13px;font-weight:700;margin:4px 0 2px">Importez</p>
          <p style="color:#9CA3AF;font-size:11px;margin:0">Vos factures CSV</p>
        </td>
        <td style="width:4%"></td>
        <td style="width:33%;padding:12px;text-align:center;background:#1F2937;border-radius:8px">
          <p style="color:#00D4AA;font-size:24px;font-weight:900;margin:0">2</p>
          <p style="color:#F9FAFB;font-size:13px;font-weight:700;margin:4px 0 2px">Analysez</p>
          <p style="color:#9CA3AF;font-size:11px;margin:0">Score de risque IA</p>
        </td>
        <td style="width:4%"></td>
        <td style="width:33%;padding:12px;text-align:center;background:#1F2937;border-radius:8px">
          <p style="color:#00D4AA;font-size:24px;font-weight:900;margin:0">3</p>
          <p style="color:#F9FAFB;font-size:13px;font-weight:700;margin:4px 0 2px">Relancez</p>
          <p style="color:#9CA3AF;font-size:11px;margin:0">IA en 4 secondes</p>
        </td>
      </tr>
    </table>
  </td></tr>

  <!-- Conseil -->
  <tr><td style="padding:20px 40px">
    <div style="background:#00D4AA11;border:1px solid #00D4AA44;border-radius:10px;padding:16px">
      <p style="color:#00D4AA;font-weight:700;font-size:13px;margin:0 0 6px">💡 Conseil du fondateur</p>
      <p style="color:#D1FAF0;font-size:13px;margin:0;line-height:1.5">
        Commencez par le mode démonstration pour voir l'IA à l'oeuvre, puis importez vos vraies factures.
        La plupart de nos utilisateurs récupèrent leur premier impayé dans les 48h.
      </p>
    </div>
  </td></tr>

  <!-- Support -->
  <tr><td style="padding:20px 40px 30px;text-align:center;border-top:1px solid #374151">
    <p style="color:#9CA3AF;font-size:13px;margin:0 0 8px">
      Une question ? Je réponds personnellement.
    </p>
    <a href="mailto:hello@invoiceguard.fr" style="color:#00D4AA;font-size:13px">
      hello@invoiceguard.fr
    </a>
    <p style="color:#6B7280;font-size:11px;margin:16px 0 0">
      🛡️ InvoiceGuard AI · 🇫🇷 Made in France · RGPD · Loi LME
    </p>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""


def envoyer_bienvenue(
    email: str,
    nom: str,
    plan: str = "trial",
    app_url: str = "http://localhost:8502",
) -> dict:
    """
    Envoie l'email de bienvenue via Resend API.
    Fallback SMTP Gmail si RESEND_API_KEY absent.
    """
    info  = PLANS_INFO.get(plan, PLANS_INFO["trial"])
    sujet = f"Bienvenue sur InvoiceGuard AI {info['emoji']} — Votre compte est actif"
    html  = _build_html(nom, plan, app_url)
    prenom = nom.split()[0] if nom else "là"

    texte = f"""Bienvenue {prenom} !

Votre compte InvoiceGuard AI {info['nom']} est actif.
Accedez a votre dashboard : {app_url}

3 etapes pour commencer :
1. Importez vos factures (CSV)
2. L'IA analyse et score chaque debiteur
3. Envoyez la relance parfaite en 4 secondes

Une question ? Repondez a cet email.
Vincent | InvoiceGuard AI
"""

    resend_key = os.environ.get("RESEND_API_KEY", "")
    if resend_key:
        try:
            r = requests.post(
                RESEND_URL,
                json={
                    "from":    "Vincent — InvoiceGuard AI <hello@invoiceguard.fr>",
                    "to":      [email],
                    "subject": sujet,
                    "html":    html,
                    "text":    texte,
                },
                headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                timeout=10,
            )
            if r.status_code == 200:
                return {"success": True, "mode": "resend", "id": r.json().get("id")}
        except Exception as e:
            pass  # Fallback SMTP

    # Fallback SMTP Gmail
    gmail_user = os.environ.get("GMAIL_USER", "")
    gmail_pwd  = os.environ.get("GMAIL_APP_PASSWORD", "")
    if gmail_user and gmail_pwd:
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            msg = MIMEMultipart("alternative")
            msg["Subject"] = sujet
            msg["From"]    = f"InvoiceGuard AI <{gmail_user}>"
            msg["To"]      = email
            msg.attach(MIMEText(texte, "plain", "utf-8"))
            msg.attach(MIMEText(html,  "html",  "utf-8"))
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as s:
                s.login(gmail_user, gmail_pwd)
                s.sendmail(gmail_user, [email], msg.as_bytes())
            return {"success": True, "mode": "smtp_gmail"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # Mode demo
    return {"success": True, "mode": "demo_no_send"}


def envoyer_bienvenue_lead(email: str, nom: str = "") -> dict:
    """Email plus court pour les leads (pas encore clients)."""
    prenom = nom.split()[0] if nom else "vous"
    sujet  = "Votre guide recouvrement PME est pret !"
    html   = f"""<!DOCTYPE html>
<html><body style="font-family:Arial;background:#0A0F1E;color:#F9FAFB;padding:40px">
<div style="max-width:560px;margin:0 auto;background:#111827;border-radius:16px;
  padding:40px;border:1px solid #374151">
  <p style="color:#00D4AA;font-size:22px;font-weight:900;margin:0 0 16px">
    🛡️ InvoiceGuard AI
  </p>
  <h2 style="color:#F9FAFB;margin:0 0 12px">Bonjour {prenom} !</h2>
  <p style="color:#D1FAE5;line-height:1.6">
    Merci pour votre interet. Votre guide
    <strong>"Le Guide Complet du Recouvrement pour PME"</strong>
    est disponible ici :
  </p>
  <div style="text-align:center;margin:24px 0">
    <a href="http://localhost:8509" style="background:#00D4AA;color:#000;font-weight:800;
      padding:14px 28px;border-radius:8px;text-decoration:none;font-size:15px">
      Telecharger mon guide gratuit
    </a>
  </div>
  <p style="color:#9CA3AF;font-size:13px">
    Et si vous voulez voir comment <strong>l'IA recupère vos impayés automatiquement</strong> :
    <a href="http://localhost:8502" style="color:#00D4AA">Essai gratuit 14 jours</a>
    (sans carte bancaire).
  </p>
  <hr style="border:1px solid #374151;margin:24px 0">
  <p style="color:#6B7280;font-size:11px;text-align:center">
    InvoiceGuard AI · Made in France · RGPD
  </p>
</div>
</body></html>"""

    resend_key = os.environ.get("RESEND_API_KEY", "")
    if resend_key:
        try:
            r = requests.post(
                RESEND_URL,
                json={"from": "InvoiceGuard AI <hello@invoiceguard.fr>",
                      "to": [email], "subject": sujet, "html": html},
                headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                timeout=10,
            )
            return {"success": r.status_code == 200}
        except Exception:
            pass
    return {"success": True, "mode": "demo"}
