"""
InvoiceGuard AI — Module Email Sender
Envoi des relances via Resend API (ou simulation en mode démo).
"""

import os
import requests
import json
from datetime import datetime


RESEND_API_URL = "https://api.resend.com/emails"


def envoyer_email(
    destinataire: str,
    sujet: str,
    corps: str,
    expediteur_nom: str = "InvoiceGuard AI",
    expediteur_email: str = "relances@invoiceguard.fr",
    mode_demo: bool = True,
) -> dict:
    """
    Envoie un email de relance.

    En mode démo (mode_demo=True), simule l'envoi et retourne un succès fictif.
    En production, utilise l'API Resend.

    Returns:
        dict avec 'success' (bool), 'message_id' (str), 'timestamp' (str)
    """
    timestamp = datetime.now().strftime("%d/%m/%Y à %H:%M")

    if mode_demo:
        # Mode démo : simulation
        return {
            "success": True,
            "message_id": f"demo-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": timestamp,
            "mode": "DÉMONSTRATION (email non envoyé réellement)",
        }

    # Mode production : Resend API
    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        return {
            "success": False,
            "error": "Clé API Resend manquante (RESEND_API_KEY dans .env)",
            "timestamp": timestamp,
        }

    payload = {
        "from": f"{expediteur_nom} <{expediteur_email}>",
        "to": [destinataire],
        "subject": sujet,
        "text": corps,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(RESEND_API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "message_id": data.get("id", "unknown"),
                "timestamp": timestamp,
                "mode": "PRODUCTION",
            }
        else:
            return {
                "success": False,
                "error": f"Erreur Resend {response.status_code}: {response.text}",
                "timestamp": timestamp,
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": timestamp,
        }


def log_relance(
    numero_facture: str,
    client: str,
    canal: str,
    ton: str,
    resultat: dict,
) -> dict:
    """Crée un enregistrement de la relance pour l'historique."""
    return {
        "numero_facture": numero_facture,
        "client": client,
        "canal": canal,
        "ton": ton,
        "date_envoi": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "succes": resultat.get("success", False),
        "message_id": resultat.get("message_id", ""),
    }
