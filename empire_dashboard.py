"""
Nexus AI Group — Dashboard Fondateur Unifié
Consolide InvoiceGuard AI + Nexus AI Supply Chain en une seule vue.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
import os, sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))
from modules import database as db

st.set_page_config(
    page_title="Nexus AI Group — Empire Dashboard",
    page_icon="🏛️",
    layout="wide",
)

st.html("""<style>
[data-testid="stAppViewContainer"]{background:#060B14}
[data-testid="stSidebar"]{background:#0A0F1E}
.metric-card{background:#111827;border:1px solid #1F2937;border-radius:12px;padding:20px;text-align:center}
.product-ig{border-left:3px solid #00D4AA}
.product-ns{border-left:3px solid #F59E0B}
</style>""")

# ─── Auth ─────────────────────────────────────────────────────────────────────
FOUNDER_PWD = os.environ.get("FOUNDER_PASSWORD", "empire2026")
if "empire_auth" not in st.session_state:
    st.session_state.empire_auth = False

if not st.session_state.empire_auth:
    st.title("🏛️ Nexus AI Group — Empire Dashboard")
    pwd = st.text_input("Mot de passe fondateur", type="password")
    if st.button("Accéder", type="primary"):
        if pwd == FOUNDER_PWD:
            st.session_state.empire_auth = True
            st.rerun()
        else:
            st.error("Incorrect")
    st.stop()

# ─── Données ──────────────────────────────────────────────────────────────────
stats    = db.get_founder_stats()
users_df = db.get_all_users()
leads_df = db.get_leads()

PRIX = {"trial": 0, "starter": 49, "pro": 149, "scale": 399}

# MRR par produit (source = colonne 'societe' utilisée comme tag produit)
mrr_ig = 0
mrr_ns = 0
if not users_df.empty:
    for _, u in users_df.iterrows():
        montant = PRIX.get(u.get("plan", "trial"), 0)
        if "nexus" in str(u.get("societe", "")).lower():
            mrr_ns += montant
        else:
            mrr_ig += montant

mrr_total = mrr_ig + mrr_ns
arr_total = mrr_total * 12

# ─── Header ───────────────────────────────────────────────────────────────────
col_logo, col_date = st.columns([3, 1])
with col_logo:
    st.markdown("# 🏛️ Nexus AI Group — Empire Dashboard")
with col_date:
    st.caption(f"Mis à jour le {date.today().strftime('%d/%m/%Y')}")
    st.caption("Fondateur · Vue consolidée")

st.divider()

# ─── KPIs Empire ──────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("💰 MRR Total", f"{mrr_total:,.0f}€", delta="Objectif: 500€")
c2.metric("📈 ARR", f"{arr_total:,.0f}€")
c3.metric("👥 Clients totaux", stats["total_users"])
c4.metric("🎯 Leads", stats["total_leads"])
c5.metric("🛡️ MRR InvoiceGuard", f"{mrr_ig:,.0f}€")
c6.metric("⚠️ MRR Nexus AI", f"{mrr_ns:,.0f}€")

st.divider()

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab_overview, tab_pipeline, tab_products, tab_actions = st.tabs([
    "📊 Vue d'ensemble", "🎯 Pipeline leads", "📦 Produits", "🚀 Plan d'action"
])

# ─── Overview ─────────────────────────────────────────────────────────────────
with tab_overview:
    col_left, col_right = st.columns([2, 1])

    with col_left:
        # Projection MRR 12 mois
        st.subheader("Projection MRR — Empire complet")
        mois_labels = [f"M{i}" for i in range(1, 13)]
        # Scénario réaliste : 4 clients/mois, churn 5%, prix moyen 99€
        clients = [mrr_total // 99 if mrr_total > 0 else 0]
        mrr_proj = [mrr_total]
        for _ in range(11):
            c_prev = clients[-1]
            c_new  = max(0, int(c_prev * 0.95) + 4)
            clients.append(c_new)
            mrr_proj.append(c_new * 99)

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=mois_labels, y=mrr_proj,
            marker_color=["#00D4AA" if v < 5000 else "#F59E0B" if v < 15000 else "#8B5CF6" for v in mrr_proj],
            text=[f"{v:,.0f}€" for v in mrr_proj],
            textposition="outside", name="MRR projeté",
        ))
        fig.add_hline(y=5000,  line_dash="dot", line_color="#F59E0B", annotation_text="5k€ MRR")
        fig.add_hline(y=15000, line_dash="dot", line_color="#8B5CF6", annotation_text="15k€ MRR")
        fig.update_layout(
            paper_bgcolor="#0A0F1E", plot_bgcolor="#0A0F1E",
            font=dict(color="white"), height=320,
            yaxis=dict(gridcolor="#1F2937", color="white"),
            xaxis=dict(color="white"),
            margin=dict(t=30, b=40),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Répartition MRR")
        if mrr_total > 0:
            fig2 = go.Figure(go.Pie(
                labels=["InvoiceGuard AI", "Nexus AI Supply Chain"],
                values=[mrr_ig or 1, mrr_ns or 1],
                hole=0.55,
                marker_colors=["#00D4AA", "#F59E0B"],
            ))
            fig2.update_layout(
                paper_bgcolor="#0A0F1E", font=dict(color="white"),
                height=200, margin=dict(t=10, b=10, l=10, r=10),
                showlegend=True,
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("En attente du premier client payant")

        st.divider()
        st.markdown("**Métriques clés**")
        jours_depuis_lancement = (date.today() - date(2026, 9, 19)).days
        st.metric("Jours depuis lancement", jours_depuis_lancement)
        rev_par_jour = mrr_total / 30 if mrr_total > 0 else 0
        st.metric("Revenu/jour", f"{rev_par_jour:.1f}€")
        ltv = mrr_total * 18 if mrr_total > 0 else 0  # LTV ~18 mois
        st.metric("LTV estimée (18 mois)", f"{ltv:,.0f}€")

# ─── Pipeline ─────────────────────────────────────────────────────────────────
with tab_pipeline:
    st.subheader("Pipeline leads consolidé")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 🛡️ InvoiceGuard AI")
        ig_leads = leads_df[~leads_df.get("source", pd.Series(dtype=str)).str.contains("nexus", na=False)] if not leads_df.empty else pd.DataFrame()
        if ig_leads.empty:
            st.info("Aucun lead — Publier le post LinkedIn lundi 8h")
        else:
            st.dataframe(ig_leads[["email","nom","societe","created_at"]].rename(
                columns={"email":"Email","nom":"Nom","societe":"Société","created_at":"Date"}
            ), hide_index=True, use_container_width=True)

    with col_b:
        st.markdown("#### ⚠️ Nexus AI Supply Chain")
        ns_leads = leads_df[leads_df.get("source", pd.Series(dtype=str)).str.contains("nexus", na=False)] if not leads_df.empty else pd.DataFrame()
        if ns_leads.empty:
            st.info("Aucun lead — 5 cold emails envoyés le 21/09, relancer")
        else:
            st.dataframe(ns_leads[["email","nom","societe","created_at"]].rename(
                columns={"email":"Email","nom":"Nom","societe":"Société","created_at":"Date"}
            ), hide_index=True, use_container_width=True)

    st.divider()
    st.subheader("Ajouter un lead manuellement")
    with st.form("add_lead"):
        c1, c2, c3, c4 = st.columns(4)
        l_email   = c1.text_input("Email")
        l_nom     = c2.text_input("Nom")
        l_societe = c3.text_input("Société")
        l_produit = c4.selectbox("Produit", ["invoiceguard", "nexus", "bundle"])
        if st.form_submit_button("Ajouter au pipeline", type="primary"):
            if l_email:
                db.save_lead(l_email, l_nom, l_societe, "", 0, l_produit)
                st.success(f"Lead ajouté : {l_email}")
                st.rerun()

# ─── Produits ─────────────────────────────────────────────────────────────────
with tab_products:
    col_ig, col_ns = st.columns(2)

    with col_ig:
        with st.container(border=True):
            st.markdown("### 🛡️ InvoiceGuard AI")
            st.caption("Recouvrement automatique d'impayés")
            st.metric("MRR", f"{mrr_ig:,.0f}€")
            st.metric("Clients payants", len([u for _, u in users_df.iterrows() if u.get("plan") != "trial"]) if not users_df.empty else 0)
            st.divider()
            st.markdown("""
**Pricing :**
- Starter : 49€/mois
- Pro : 149€/mois ⭐
- Scale : 399€/mois

**Apps actives :**
- [Dashboard](http://localhost:8502) (port 8502)
- [Onboarding](http://localhost:8512) (port 8512)
- [Legal](http://localhost:8513) (port 8513)

**Status Stripe :** ❌ À configurer
```
python setup_stripe_auto.py --key sk_live_...
```
""")

    with col_ns:
        with st.container(border=True):
            st.markdown("### ⚠️ Nexus AI Supply Chain")
            st.caption("Intelligence géopolitique pour l'import/export")
            st.metric("MRR", f"{mrr_ns:,.0f}€")
            st.metric("App Streamlit Cloud", "✅ LIVE")
            st.divider()
            st.markdown("""
**Pricing :**
- Starter : 49€/mois
- Pro : 149€/mois

**Apps actives :**
- [Crisis Dashboard](https://nexus-ai-empire-6yrflyffrz2l6jxaxtk9gf.streamlit.app) ✅ LIVE

**Status Stripe :** ✅ Lien actif
```
https://buy.stripe.com/cNi6oHcZifuj3w14Kx87K04
```
**Renommer produit Stripe :** "Accès API OSINT" → "Nexus AI Supply Chain"
""")

    st.divider()
    st.subheader("🔗 Bundle — Les deux produits")
    with st.container(border=True):
        col_x, col_y = st.columns([2, 1])
        with col_x:
            st.markdown("""
**Bundle Pro — 249€/mois** *(vs 298€ séparément — économie 16%)*
- Tout InvoiceGuard Pro + Tout Nexus AI Pro
- 1 seul abonnement, 1 seule facture

**Bundle Scale — 499€/mois** *(vs 548€ séparément — économie 9%)*
- Tout InvoiceGuard Scale + Tout Nexus AI Pro
- Multi-utilisateurs, API complète, SLA 99.9%

**Argument commercial :** Une PME import/export a systématiquement les deux problèmes.
Une seule conversation → deux abonnements.
""")
        with col_y:
            st.metric("Bundle Pro MRR potentiel", "249€/client")
            st.metric("LTV 18 mois", "4 482€/client")

# ─── Plan d'action ────────────────────────────────────────────────────────────
with tab_actions:
    st.subheader("🚀 Plan d'action — 7 jours")

    actions = [
        {"J": "J0 — Aujourd'hui", "Priorité": "🔴", "Action": "Envoyer lien Nexus Stripe à 3 contacts maintenant", "Impact": "★★★★★", "Fait": False},
        {"J": "J0 — Aujourd'hui", "Priorité": "🔴", "Action": "Configurer Stripe InvoiceGuard (1 commande)", "Impact": "★★★★★", "Fait": False},
        {"J": "J0 — Aujourd'hui", "Priorité": "🔴", "Action": "Activer alertes Telegram (python setup_telegram.py)", "Impact": "★★★★", "Fait": False},
        {"J": "J+1", "Priorité": "🟠", "Action": "Mettre à jour le hook géopolitique Nexus (données 30/09)", "Impact": "★★★★", "Fait": False},
        {"J": "J+1", "Priorité": "🟠", "Action": "Déployer InvoiceGuard sur Streamlit Cloud", "Impact": "★★★★★", "Fait": False},
        {"J": "J+2", "Priorité": "🟠", "Action": "Landing page Nexus AI Group (hub des 2 produits)", "Impact": "★★★", "Fait": True},
        {"J": "J+3", "Priorité": "🟡", "Action": "Campagne 10 experts-comptables (pitch double produit)", "Impact": "★★★★★", "Fait": False},
        {"J": "J+4", "Priorité": "🟡", "Action": "LinkedIn POST InvoiceGuard (lundi 8h)", "Impact": "★★★★", "Fait": False},
        {"J": "J+5", "Priorité": "🟡", "Action": "LinkedIn POST Nexus AI (mercredi 8h)", "Impact": "★★★★", "Fait": False},
        {"J": "J+6", "Priorité": "🟡", "Action": "Campagne 20 emails PME import/export pour Nexus", "Impact": "★★★", "Fait": False},
        {"J": "J+7", "Priorité": "🟢", "Action": "Product Hunt — Nexus AI Supply Chain", "Impact": "★★★", "Fait": False},
    ]

    df_actions = pd.DataFrame(actions)
    df_actions["✅"] = df_actions["Fait"].map({True: "✅", False: "⬜"})
    st.dataframe(
        df_actions[["✅","J","Priorité","Action","Impact"]],
        hide_index=True, use_container_width=True,
        column_config={"Impact": st.column_config.TextColumn(width="small")},
    )

    st.divider()
    st.info("""
**🎯 Objectif semaine :** Premier client payant sur l'un des deux produits.

**Le chemin le plus court :** Nexus AI → Stripe déjà actif → envoyer ce lien à 3 personnes maintenant :
`https://buy.stripe.com/cNi6oHcZifuj3w14Kx87K04`
""")
