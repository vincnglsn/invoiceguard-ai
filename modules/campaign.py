"""
InvoiceGuard AI — Campagne de Relances en Masse
Orchestration de relances groupées avec stratégie et séquençage.
"""

import pandas as pd
from datetime import date, timedelta
from typing import Generator


SEQUENCES = {
    "standard": [
        {"jour": 0,  "ton": "doux",            "canal": "email", "label": "1ère relance (amiable)"},
        {"jour": 7,  "ton": "ferme",           "canal": "email", "label": "2ème relance (ferme)"},
        {"jour": 14, "ton": "urgent",          "canal": "email", "label": "3ème relance (urgente)"},
        {"jour": 21, "ton": "mise_en_demeure", "canal": "email", "label": "Mise en demeure"},
    ],
    "agressive": [
        {"jour": 0,  "ton": "ferme",           "canal": "email", "label": "1ère relance (ferme)"},
        {"jour": 3,  "ton": "urgent",          "canal": "email", "label": "2ème relance (urgente)"},
        {"jour": 7,  "ton": "mise_en_demeure", "canal": "email", "label": "Mise en demeure"},
    ],
    "douce": [
        {"jour": 0,  "ton": "doux",  "canal": "email", "label": "1ère relance (amiable)"},
        {"jour": 14, "ton": "ferme", "canal": "email", "label": "2ème relance (ferme)"},
        {"jour": 30, "ton": "urgent","canal": "email", "label": "3ème relance (urgente)"},
    ],
}


def filter_campaign_targets(df: pd.DataFrame, critere: str = "all_late") -> pd.DataFrame:
    """
    Sélectionne les factures cibles pour une campagne.

    criteres:
      - 'all_late'    : toutes les factures en retard
      - 'critiques'   : score >= 70 uniquement
      - 'elevees'     : score >= 40
      - 'over_30j'    : retard > 30 jours
      - 'over_60j'    : retard > 60 jours
    """
    en_retard = df[df["jours_retard"] > 0].copy()

    if critere == "critiques":
        return en_retard[en_retard["score_risque"] >= 70]
    elif critere == "elevees":
        return en_retard[en_retard["score_risque"] >= 40]
    elif critere == "over_30j":
        return en_retard[en_retard["jours_retard"] > 30]
    elif critere == "over_60j":
        return en_retard[en_retard["jours_retard"] > 60]
    else:
        return en_retard


def build_campaign_plan(df_targets: pd.DataFrame, sequence_name: str = "standard") -> pd.DataFrame:
    """
    Génère le plan de campagne : quand envoyer quoi à qui.

    Returns:
        DataFrame avec colonnes : client, facture, montant, date_envoi, etape, ton, canal
    """
    sequence = SEQUENCES.get(sequence_name, SEQUENCES["standard"])
    today = date.today()
    rows = []

    for _, facture in df_targets.iterrows():
        for etape in sequence:
            date_envoi = today + timedelta(days=etape["jour"])
            rows.append({
                "client": facture["client"],
                "numero_facture": facture["numero_facture"],
                "montant": facture["montant"],
                "jours_retard": facture["jours_retard"],
                "priorite": facture["priorite"],
                "date_envoi": date_envoi.strftime("%d/%m/%Y"),
                "etape": etape["label"],
                "ton": etape["ton"],
                "canal": etape["canal"],
                "email_client": facture.get("email_client", ""),
            })

    return pd.DataFrame(rows)


def estimate_recovery(df_targets: pd.DataFrame) -> dict:
    """
    Estime le montant récupérable par une campagne.
    Basé sur les taux de recouvrement moyens par ancienneté (données marché).
    """
    total = 0.0
    par_tranche = {}

    for _, row in df_targets.iterrows():
        retard = row["jours_retard"]
        montant = float(row["montant"])

        if retard <= 15:
            taux = 0.92
            tranche = "1-15j"
        elif retard <= 30:
            taux = 0.85
            tranche = "16-30j"
        elif retard <= 60:
            taux = 0.72
            tranche = "31-60j"
        elif retard <= 90:
            taux = 0.55
            tranche = "61-90j"
        else:
            taux = 0.35
            tranche = "+90j"

        recuperable = montant * taux
        total += recuperable

        if tranche not in par_tranche:
            par_tranche[tranche] = {"montant_total": 0, "montant_recuperable": 0, "nb": 0, "taux": taux}
        par_tranche[tranche]["montant_total"] += montant
        par_tranche[tranche]["montant_recuperable"] += recuperable
        par_tranche[tranche]["nb"] += 1

    return {
        "total_en_jeu": df_targets["montant"].sum(),
        "total_recuperable": total,
        "taux_global": total / df_targets["montant"].sum() if len(df_targets) > 0 else 0,
        "par_tranche": par_tranche,
        "commission_invoiceguard": total * 0.03,
    }
