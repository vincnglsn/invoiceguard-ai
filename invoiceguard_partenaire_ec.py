"""
InvoiceGuard AI — Tableau de Bord Partenaire Expert-Comptable
Interface dédiée aux EC pour piloter les impayés de leurs clients PME.
C'est le canal d'acquisition n°1 : 1 EC = 200-300 clients potentiels.
"""

import streamlit as st
import pandas as pd
import os
import sys
import random
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))
from modules import invoice_scanner

st.set_page_config(
    page_title="InvoiceGuard — Espace Partenaire EC",
    page_icon="🏦",
    layout="wide",
)

# ─── Faux clients EC pour la démo ─────────────────────────────────────────────
CLIENTS_EC_DEMO = [
    {"nom": "BTP Martin SARL",         "secteur": "BTP",         "ca": 850000,  "impayés": 34200},
    {"nom": "Cabinet Conseil Sud",     "secteur": "Conseil",     "ca": 420000,  "impayés": 18700},
    {"nom": "Transport Express 06",    "secteur": "Transport",   "ca": 1200000, "impayés": 62000},
    {"nom": "Optique Vision Pro",      "secteur": "Santé",       "ca": 280000,  "impayés": 8400},
    {"nom": "Imprimerie Centrale",     "secteur": "Industrie",   "ca": 560000,  "impayés": 22100},
    {"nom": "SCI Les Acacias",         "secteur": "Immobilier",  "ca": 190000,  "impayés": 14300},
    {"nom": "Restaurant Le Gourmet",   "secteur": "HCR",         "ca": 380000,  "impayés": 5600},
    {"nom": "Pharmacie du Centre",     "secteur": "Santé",       "ca": 2100000, "impayés": 31000},
]

# ─── Header ───────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🏦 Espace Partenaire Expert-Comptable")
    st.caption("Pilotez les impayés de tous vos clients PME depuis un seul tableau de bord")
with col_h2:
    st.markdown("### Votre cabinet")
    cabinet_nom = st.text_input("Nom du cabinet", value="Cabinet Expert & Co",
                                 label_visibility="collapsed")

st.divider()

# ─── KPIs agrégés sur tous les clients ────────────────────────────────────────
total_impayés = sum(c["impayés"] for c in CLIENTS_EC_DEMO)
total_ca = sum(c["ca"] for c in CLIENTS_EC_DEMO)
clients_alertes = sum(1 for c in CLIENTS_EC_DEMO if c["impayés"] > 20000)
commission_potentielle = total_impayés * 0.72 * 0.20  # 20% commission EC

c1, c2, c3, c4 = st.columns(4)
c1.metric("👥 Clients PME suivis", len(CLIENTS_EC_DEMO))
c2.metric("💸 Impayés agrégés", f"{total_impayés:,.0f}€",
          delta=f"{total_impayés/total_ca*100:.1f}% du CA total", delta_color="inverse")
c3.metric("🚨 Clients en alerte", f"{clients_alertes}",
          delta=f"(> 20 000€ d'impayés)")
c4.metric("💰 Votre commission potentielle",
          f"{commission_potentielle:,.0f}€",
          delta="20% sur les montants récupérés",
          help="InvoiceGuard verse 20% de la commission de récupération à ses partenaires EC")

st.divider()

tab_clients, tab_alertes, tab_commission, tab_onboard = st.tabs([
    ":material/group: Mes clients",
    ":material/notifications: Alertes",
    ":material/euro: Mes commissions",
    ":material/person_add: Inviter un client",
])

# ─── Tab 1 : Clients ──────────────────────────────────────────────────────────
with tab_clients:
    st.subheader("Tableau de bord multi-clients")

    # Filtres
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        secteur_filtre = st.multiselect(
            "Secteur",
            list(set(c["secteur"] for c in CLIENTS_EC_DEMO)),
            default=list(set(c["secteur"] for c in CLIENTS_EC_DEMO)),
        )
    with col_f2:
        seuil_alerte = st.slider("Seuil d'alerte (€ d'impayés)", 0, 70000, 10000, step=5000)

    clients_filtres = [c for c in CLIENTS_EC_DEMO if c["secteur"] in secteur_filtre]

    # Table clients avec statuts
    rows = []
    for c in clients_filtres:
        taux = c["impayés"] / c["ca"] * 100
        statut = "🔴 Critique" if c["impayés"] > seuil_alerte * 2 else (
                 "🟠 Alerte" if c["impayés"] > seuil_alerte else "🟢 OK")
        rows.append({
            "Client": c["nom"],
            "Secteur": c["secteur"],
            "CA annuel": c["ca"],
            "Impayés": c["impayés"],
            "% CA": round(taux, 1),
            "Statut": statut,
            "DSO estimé (j)": round(c["impayés"] / c["ca"] * 365, 0),
        })

    df_clients = pd.DataFrame(rows)
    st.dataframe(
        df_clients,
        column_config={
            "CA annuel": st.column_config.NumberColumn(format="%.0f €"),
            "Impayés": st.column_config.NumberColumn(format="%.0f €"),
            "% CA": st.column_config.NumberColumn(format="%.1f %%"),
            "DSO estimé (j)": st.column_config.NumberColumn(format="%.0f j"),
        },
        hide_index=True, use_container_width=True,
    )

    # Chart comparatif
    import plotly.graph_objects as go
    fig = go.Figure()
    colors = ["#FF4B4B" if c["impayés"] > seuil_alerte * 2 else
              "#FFA500" if c["impayés"] > seuil_alerte else "#00C853"
              for c in clients_filtres]
    fig.add_trace(go.Bar(
        x=[c["nom"] for c in clients_filtres],
        y=[c["impayés"] for c in clients_filtres],
        marker_color=colors,
        text=[f"{c['impayés']:,.0f}€" for c in clients_filtres],
        textposition="outside",
    ))
    fig.update_layout(
        title="Impayés par client",
        paper_bgcolor="#0A0F1E", plot_bgcolor="#0A0F1E",
        font=dict(color="white"),
        xaxis=dict(color="white", tickangle=-30),
        yaxis=dict(color="white", tickformat=",.0f"),
        height=350, margin=dict(t=50, b=80, l=60, r=20),
    )
    st.plotly_chart(fig, use_container_width=True)

# ─── Tab 2 : Alertes ─────────────────────────────────────────────────────────
with tab_alertes:
    st.subheader("🚨 Alertes à traiter en priorité")

    alertes = [c for c in CLIENTS_EC_DEMO if c["impayés"] > 15000]
    if not alertes:
        st.success("✅ Aucune alerte critique — tous vos clients sont dans les normes.")
    else:
        for c in sorted(alertes, key=lambda x: x["impayés"], reverse=True):
            with st.container(border=True):
                col_a1, col_a2, col_a3 = st.columns([3, 1, 1])
                with col_a1:
                    st.markdown(f"**{c['nom']}** · {c['secteur']}")
                    st.caption(f"Impayés : **{c['impayés']:,.0f}€** ({c['impayés']/c['ca']*100:.1f}% du CA)")
                with col_a2:
                    st.metric("Récupérable", f"{c['impayés']*0.72:,.0f}€")
                with col_a3:
                    if st.button(f"Activer InvoiceGuard", key=f"act_{c['nom']}",
                                 type="primary", use_container_width=True):
                        st.success(f"✅ Invitation envoyée à {c['nom']} !")

# ─── Tab 3 : Commissions ──────────────────────────────────────────────────────
with tab_commission:
    st.subheader("💰 Suivi de vos commissions partenaire")
    st.markdown("""
    En tant que partenaire InvoiceGuard, vous recevez **20% de commission récurrente**
    sur tous les abonnements de vos clients PME, et **20% sur les commissions de récupération**.
    """)

    with st.container(border=True):
        col_c1, col_c2, col_c3 = st.columns(3)
        # Simulation commission mois en cours
        abonnements = len(CLIENTS_EC_DEMO) * 149  # si tous au plan Pro
        comm_abo = abonnements * 0.20
        montant_rec = total_impayés * 0.72
        comm_rec = montant_rec * 0.03 * 0.20  # 3% InvoiceGuard × 20% part EC

        col_c1.metric("Commissions abonnements", f"{comm_abo:,.0f}€/mois",
                      delta=f"{len(CLIENTS_EC_DEMO)} clients × 149€ × 20%")
        col_c2.metric("Commissions récupération", f"{comm_rec:,.0f}€",
                      delta="20% des frais de succès InvoiceGuard")
        col_c3.metric("Total potentiel / mois", f"{comm_abo + comm_rec:,.0f}€",
                      delta="Passif récurrent à vie")

    st.divider()
    st.info("""
    **📋 Comment maximiser vos commissions ?**
    1. Invitez tous vos clients PME avec un CA > 200K€ (ils ont forcément des impayés)
    2. Ciblez en priorité les secteurs BTP, Transport, Conseil (DSO élevé)
    3. Présentez InvoiceGuard lors de vos réunions de bilan annuel
    4. Partagez le rapport PDF mensuel généré par InvoiceGuard à vos clients → démo gratuite incluse
    """)

# ─── Tab 4 : Onboarding ──────────────────────────────────────────────────────
with tab_onboard:
    st.subheader(":material/person_add: Inviter un client PME sur InvoiceGuard")
    st.caption("Générez un email d'invitation personnalisé en 10 secondes")

    col_o1, col_o2 = st.columns(2)
    with col_o1:
        client_invite_nom = st.text_input("Nom du client", placeholder="BTP Dupont SARL")
        client_invite_email = st.text_input("Email du gérant", placeholder="direction@btpdupont.fr")
        client_invite_secteur = st.selectbox("Secteur", [
            "BTP", "Transport", "Conseil", "Santé", "Commerce", "Industrie", "Immobilier"
        ])
    with col_o2:
        client_invite_ca = st.number_input("CA estimé (€)", value=500000, step=50000)
        client_invite_impayés = st.number_input("Impayés estimés (€)", value=20000, step=5000)
        inclure_rapport = st.checkbox("Joindre un rapport demo personnalisé", value=True)

    if st.button(":material/send: Générer l'invitation", type="primary"):
        roi_estime = client_invite_impayés * 0.72
        with st.container(border=True):
            st.markdown("#### 📧 Email d'invitation généré")
            msg = f"""Objet : {client_invite_nom} — Je voulais vous montrer quelque chose d'utile

Bonjour,

En préparant votre bilan, j'ai réalisé que vous avez probablement aux alentours de {client_invite_impayés:,.0f}€ de factures en attente de règlement en ce moment.

J'ai trouvé un outil que j'utilise maintenant pour plusieurs de mes clients dans le {client_invite_secteur.lower()} : InvoiceGuard AI. En quelques minutes, il analyse votre portefeuille de factures et envoie automatiquement des relances personnalisées — avec le bon ton et dans le respect de la Loi LME.

Résultat typique pour un profil comme le vôtre : ~{roi_estime:,.0f}€ récupérés dans les 30 premiers jours.

C'est gratuit pendant 14 jours, sans carte bancaire. Je peux vous faire une démo de 15 min si vous souhaitez voir comment ça fonctionne.

Bien cordialement,
{cabinet_nom}

P.S. : La facturation électronique étant maintenant obligatoire à la réception, c'est aussi le bon moment pour revoir votre process de recouvrement."""

            st.text_area("", msg, height=320, label_visibility="collapsed")
            st.download_button(":material/download: Télécharger",
                               msg.encode(), f"invitation_{client_invite_nom}.txt")
