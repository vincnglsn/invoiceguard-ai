"""
InvoiceGuard AI — Module Agent IA
Génération intelligente de relances ultra-personnalisées via Gemini API.
"""

import os
from datetime import date
from google import genai
from google.genai import types

# Profils de ton selon l'urgence
TONE_PROFILES = {
    "doux": "professionnel, bienveillant et compréhensif, en supposant un oubli de bonne foi",
    "ferme": "professionnel et direct, rappelant clairement les obligations contractuelles",
    "urgent": "sérieux et urgent, mentionnant les conséquences légales possibles (pénalités de retard LME, mise en demeure)",
    "mise_en_demeure": "juridique et formel, indiquant que l'affaire sera transmise à un cabinet de recouvrement sous 72h si non règlement"
}


def _get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Clé API Gemini manquante. Vérifiez votre fichier .env")
    return genai.Client(api_key=api_key)


def generer_relance(
    client_nom: str,
    montant: float,
    numero_facture: str,
    date_echeance: str,
    jours_retard: int,
    email_client: str = "",
    canal: str = "email",
    ton: str = "auto",
) -> dict:
    """
    Génère un message de relance personnalisé via Gemini.

    Returns:
        dict avec 'sujet', 'corps', 'ton_utilise'
    """
    # Sélection automatique du ton
    if ton == "auto":
        if jours_retard <= 15:
            ton_final = "doux"
        elif jours_retard <= 45:
            ton_final = "ferme"
        elif jours_retard <= 90:
            ton_final = "urgent"
        else:
            ton_final = "mise_en_demeure"
    else:
        ton_final = ton

    description_ton = TONE_PROFILES.get(ton_final, TONE_PROFILES["ferme"])
    today_str = date.today().strftime("%d/%m/%Y")

    if canal == "sms":
        prompt = f"""Tu es un agent de recouvrement professionnel français.

Rédige un SMS de relance pour impayé, ton {description_ton}.

Infos :
- Client : {client_nom}
- Facture n° : {numero_facture}
- Montant : {montant:,.2f}€
- Échéance : {date_echeance}
- Retard : {jours_retard} jours
- Date du jour : {today_str}

Règles SMS :
- Maximum 160 caractères
- Inclure le numéro de facture et le montant
- Un appel à l'action clair (ex: "Répondez à cet SMS ou appelez le...")
- Ton {description_ton}

Retourne UNIQUEMENT le texte du SMS, sans guillemets ni explication."""

        client_gemini = _get_client()
        response = client_gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.4),
        )
        return {
            "sujet": f"Relance SMS — {client_nom}",
            "corps": response.text.strip(),
            "ton_utilise": ton_final,
        }

    # Email
    prompt = f"""Tu es un agent de recouvrement professionnel français, expert en droit des affaires et en relation client.

Rédige un email de relance de facture impayée, avec un ton {description_ton}.

Informations sur la facture :
- Entreprise débitrice : {client_nom}
- Numéro de facture : {numero_facture}
- Montant TTC dû : {montant:,.2f}€
- Date d'échéance contractuelle : {date_echeance}
- Nombre de jours de retard : {jours_retard} jours
- Date d'envoi de ce message : {today_str}

Contexte légal français à respecter :
- La loi LME impose des pénalités de retard automatiques (taux directeur BCE + 10 points minimum, soit ~13% actuellement)
- Une indemnité forfaitaire de recouvrement de 40€ est due de droit
- Au-delà de 90 jours, la procédure d'injonction de payer est possible

Instructions de rédaction :
1. Objet de l'email accrocheur et professionnel
2. Corps de l'email en 3 paragraphes maximum : rappel des faits, conséquences, appel à l'action clair
3. Mentionner les références légales si le ton est "urgent" ou "mise_en_demeure"
4. Terminer par une formule de politesse professionnelle adaptée au ton
5. Pas de formatage markdown dans le corps, juste du texte brut propre

Retourne le résultat au format exact suivant :
OBJET: [l'objet de l'email ici]
---
CORPS:
[le corps complet de l'email ici]"""

    client_gemini = _get_client()
    response = client_gemini.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.3),
    )

    raw = response.text.strip()

    # Parsing de la réponse
    sujet = ""
    corps = raw
    if "OBJET:" in raw and "---" in raw:
        parts = raw.split("---", 1)
        sujet_line = parts[0].strip()
        sujet = sujet_line.replace("OBJET:", "").strip()
        corps_part = parts[1].strip()
        if corps_part.startswith("CORPS:"):
            corps = corps_part[len("CORPS:"):].strip()
        else:
            corps = corps_part

    return {
        "sujet": sujet or f"Relance facture {numero_facture} — Règlement requis sous 72h",
        "corps": corps,
        "ton_utilise": ton_final,
    }


def analyser_portefeuille(factures_resumees: str) -> str:
    """
    Analyse globale du portefeuille d'impayés avec recommandations IA.
    """
    client_gemini = _get_client()
    prompt = f"""Tu es un expert en gestion de trésorerie pour PME françaises.

Analyse ce portefeuille de factures impayées et fournis :
1. Un diagnostic de la situation (2-3 phrases)
2. Les 3 actions prioritaires à mener immédiatement
3. Une estimation du délai de recouvrement réaliste
4. Un conseil pour éviter ces situations à l'avenir

Données du portefeuille :
{factures_resumees}

Sois précis, actionnable et concis. Utilise des chiffres quand c'est pertinent."""

    response = client_gemini.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.4),
    )
    return response.text.strip()
