"""
InvoiceGuard AI — Module Scanner de Factures
Extraction, analyse et scoring des factures impayées.
"""

import pandas as pd
from datetime import datetime, date
import io
import os

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


def load_demo_data() -> pd.DataFrame:
    """Charge les données de démonstration."""
    demo_path = os.path.join(os.path.dirname(__file__), "..", "demo_data", "sample_invoices.csv")
    df = pd.read_csv(demo_path)
    df["date_emission"] = pd.to_datetime(df["date_emission"])
    df["date_echeance"] = pd.to_datetime(df["date_echeance"])
    df = _enrich_dataframe(df)
    return df


def load_from_csv(file_content: bytes) -> pd.DataFrame:
    """Charge et analyse les factures depuis un fichier CSV uploadé."""
    df = pd.read_csv(io.BytesIO(file_content))
    # Normalisation des colonnes
    col_map = {
        "facture": "numero_facture", "invoice": "numero_facture", "num": "numero_facture",
        "client": "client", "société": "client", "entreprise": "client",
        "montant": "montant", "amount": "montant", "total": "montant",
        "echéance": "date_echeance", "echeance": "date_echeance", "due_date": "date_echeance",
        "emission": "date_emission", "issue_date": "date_emission",
        "statut": "statut", "status": "statut",
        "email": "email_client",
    }
    df.columns = [col_map.get(c.lower().strip(), c.lower().strip()) for c in df.columns]

    if "date_emission" in df.columns:
        df["date_emission"] = pd.to_datetime(df["date_emission"], errors="coerce")
    if "date_echeance" in df.columns:
        df["date_echeance"] = pd.to_datetime(df["date_echeance"], errors="coerce")

    df = _enrich_dataframe(df)
    return df


def _enrich_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Enrichit le dataframe avec les métriques calculées."""
    today = pd.Timestamp(date.today())

    if "date_echeance" in df.columns:
        df["jours_retard"] = (today - df["date_echeance"]).dt.days
        df["jours_retard"] = df["jours_retard"].clip(lower=0)
    else:
        df["jours_retard"] = 0

    # Statut automatique si non fourni
    if "statut" not in df.columns:
        df["statut"] = "En attente"

    # Score de risque (0-100)
    df["score_risque"] = df.apply(_calcule_score_risque, axis=1)

    # Label de priorité
    df["priorite"] = df["score_risque"].apply(_label_priorite)

    return df


def _calcule_score_risque(row) -> int:
    """Calcule un score de risque de 0 (faible) à 100 (critique)."""
    score = 0
    retard = row.get("jours_retard", 0)

    # Pondération par retard
    if retard > 90:
        score += 60
    elif retard > 60:
        score += 45
    elif retard > 30:
        score += 30
    elif retard > 15:
        score += 15
    elif retard > 0:
        score += 5

    # Pondération par montant
    montant = float(row.get("montant", 0))
    if montant > 15000:
        score += 40
    elif montant > 5000:
        score += 25
    elif montant > 2000:
        score += 15
    elif montant > 500:
        score += 5

    return min(score, 100)


def _label_priorite(score: int) -> str:
    if score >= 70:
        return "🔴 Critique"
    elif score >= 40:
        return "🟠 Élevée"
    elif score >= 20:
        return "🟡 Modérée"
    else:
        return "🟢 Faible"


def get_kpis(df: pd.DataFrame) -> dict:
    """Calcule les KPIs principaux pour le dashboard."""
    total_factures = len(df)
    montant_total = df["montant"].sum()

    retard_mask = df["jours_retard"] > 0
    factures_en_retard = df[retard_mask]
    montant_en_retard = factures_en_retard["montant"].sum()
    nb_en_retard = len(factures_en_retard)

    critiques = df[df["score_risque"] >= 70]
    montant_critique = critiques["montant"].sum()

    # DSO (Days Sales Outstanding) approximatif
    if montant_total > 0:
        dso = (montant_en_retard / montant_total) * 30
    else:
        dso = 0

    return {
        "total_factures": total_factures,
        "montant_total": montant_total,
        "nb_en_retard": nb_en_retard,
        "montant_en_retard": montant_en_retard,
        "taux_retard_pct": (nb_en_retard / total_factures * 100) if total_factures > 0 else 0,
        "nb_critiques": len(critiques),
        "montant_critique": montant_critique,
        "dso": round(dso, 1),
    }
