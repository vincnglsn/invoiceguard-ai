"""
InvoiceGuard AI — Module Dashboard
Graphiques et visualisations pour le tableau de bord trésorerie.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


# Palette de couleurs InvoiceGuard
COLORS = {
    "primary": "#00D4AA",
    "danger": "#FF4B4B",
    "warning": "#FFA500",
    "success": "#00C853",
    "neutral": "#6B7280",
    "bg": "#111827",
    "card": "#1F2937",
}


def chart_repartition_retards(df: pd.DataFrame) -> go.Figure:
    """Donut chart : répartition des factures par statut de retard."""
    bins = [-1, 0, 15, 30, 60, 90, float("inf")]
    labels = ["À l'heure", "1-15j", "16-30j", "31-60j", "61-90j", "+90j"]
    colors_list = [
        COLORS["success"], COLORS["primary"], "#FFD700",
        COLORS["warning"], COLORS["danger"], "#8B0000"
    ]

    df["tranche"] = pd.cut(df["jours_retard"], bins=bins, labels=labels)
    counts = df.groupby("tranche", observed=True)["montant"].sum().reset_index()

    fig = go.Figure(data=[go.Pie(
        labels=counts["tranche"],
        values=counts["montant"],
        hole=0.6,
        marker=dict(colors=colors_list[:len(counts)]),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>%{value:,.0f}€<br>%{percent}<extra></extra>",
    )])

    fig.update_layout(
        title=dict(text="Répartition des impayés par ancienneté", font=dict(color="white", size=16)),
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color="white"),
        showlegend=False,
        margin=dict(t=50, b=20, l=20, r=20),
        height=320,
    )
    return fig


def chart_top_debiteurs(df: pd.DataFrame, n: int = 8) -> go.Figure:
    """Bar chart horizontal : top débiteurs par montant."""
    en_retard = df[df["jours_retard"] > 0].copy()
    top = en_retard.nlargest(n, "montant")

    fig = go.Figure(go.Bar(
        x=top["montant"],
        y=top["client"],
        orientation="h",
        marker_color=[
            COLORS["danger"] if s >= 70 else COLORS["warning"] if s >= 40 else COLORS["primary"]
            for s in top["score_risque"]
        ],
        text=[f"{m:,.0f}€" for m in top["montant"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>%{x:,.0f}€<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="Top débiteurs (montant dû)", font=dict(color="white", size=16)),
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color="white"),
        xaxis=dict(showgrid=False, color="white", tickformat=",.0f"),
        yaxis=dict(color="white", autorange="reversed"),
        margin=dict(t=50, b=20, l=20, r=80),
        height=320,
    )
    return fig


def chart_timeline_encaissements(df: pd.DataFrame) -> go.Figure:
    """Bar chart : prévision d'encaissement sur 90 jours."""
    from datetime import date, timedelta
    import numpy as np

    today = pd.Timestamp(date.today())

    periodes = {
        "Cette semaine": (today, today + pd.Timedelta(days=7)),
        "J+8 à J+30": (today + pd.Timedelta(days=8), today + pd.Timedelta(days=30)),
        "J+31 à J+60": (today + pd.Timedelta(days=31), today + pd.Timedelta(days=60)),
        "J+61 à J+90": (today + pd.Timedelta(days=61), today + pd.Timedelta(days=90)),
    }

    labels, montants, probas = [], [], []
    for label, (start, end) in periodes.items():
        mask = (df["date_echeance"] >= start) & (df["date_echeance"] <= end)
        montant = df[mask]["montant"].sum()

        # Probabilité de recouvrement basée sur le retard moyen
        retard_moyen = df[mask]["jours_retard"].mean() if mask.any() else 0
        proba = max(0.3, 1.0 - retard_moyen * 0.008)

        labels.append(label)
        montants.append(montant)
        probas.append(montant * proba)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Montant facturé",
        x=labels, y=montants,
        marker_color=COLORS["neutral"],
        opacity=0.5,
    ))
    fig.add_trace(go.Bar(
        name="Encaissement probable",
        x=labels, y=probas,
        marker_color=COLORS["primary"],
    ))

    fig.update_layout(
        title=dict(text="Prévision d'encaissement (90 jours)", font=dict(color="white", size=16)),
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color="white"),
        barmode="overlay",
        xaxis=dict(color="white"),
        yaxis=dict(color="white", tickformat=",.0f", title="€"),
        legend=dict(font=dict(color="white")),
        margin=dict(t=50, b=20, l=60, r=20),
        height=320,
    )
    return fig


def chart_score_risque(df: pd.DataFrame) -> go.Figure:
    """Scatter chart : matrice risque (montant vs ancienneté)."""
    en_retard = df[df["jours_retard"] > 0].copy()

    color_map = {
        "🔴 Critique": COLORS["danger"],
        "🟠 Élevée": COLORS["warning"],
        "🟡 Modérée": "#FFD700",
        "🟢 Faible": COLORS["success"],
    }

    fig = go.Figure()
    for priorite, color in color_map.items():
        subset = en_retard[en_retard["priorite"] == priorite]
        if len(subset) == 0:
            continue
        fig.add_trace(go.Scatter(
            x=subset["jours_retard"],
            y=subset["montant"],
            mode="markers+text",
            name=priorite,
            marker=dict(size=14, color=color, opacity=0.85),
            text=subset["client"].apply(lambda x: x[:12] + "…" if len(x) > 12 else x),
            textposition="top center",
            textfont=dict(size=9, color="white"),
            hovertemplate="<b>%{text}</b><br>Retard: %{x}j<br>Montant: %{y:,.0f}€<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="Matrice de risque (ancienneté × montant)", font=dict(color="white", size=16)),
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color="white"),
        xaxis=dict(title="Jours de retard", color="white", gridcolor="#1F2937"),
        yaxis=dict(title="Montant (€)", color="white", tickformat=",.0f", gridcolor="#1F2937"),
        legend=dict(font=dict(color="white")),
        margin=dict(t=50, b=40, l=60, r=20),
        height=380,
    )
    return fig
