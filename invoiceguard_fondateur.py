"""
InvoiceGuard AI — Dashboard Fondateur (MRR, Leads, Métriques SaaS)
Vue privée pour piloter la croissance du produit.
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
    page_title="InvoiceGuard — Fondateur",
    page_icon="📈",
    layout="wide",
)

# ─── Auth simple ──────────────────────────────────────────────────────────────
FOUNDER_PASSWORD = os.environ.get("FOUNDER_PASSWORD", "invoiceguard2026")

if "founder_auth" not in st.session_state:
    st.session_state.founder_auth = False

if not st.session_state.founder_auth:
    st.title("🔒 Espace Fondateur")
    pwd = st.text_input("Mot de passe", type="password")
    if st.button("Accéder"):
        if pwd == FOUNDER_PASSWORD:
            st.session_state.founder_auth = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")
    st.stop()

# ─── Données ──────────────────────────────────────────────────────────────────
stats = db.get_founder_stats()
users_df = db.get_all_users()
leads_df = db.get_leads()

# ─── Header ───────────────────────────────────────────────────────────────────
st.title("📈 Dashboard Fondateur — InvoiceGuard AI")
st.caption(f"Mis à jour le {date.today().strftime('%d/%m/%Y')}")
st.divider()

# ─── MRR simulé (basé sur les plans des users) ────────────────────────────────
PRIX_PLANS = {"trial": 0, "starter": 49, "pro": 149, "scale": 399}

mrr = 0
if not users_df.empty and "plan" in users_df.columns:
    mrr = users_df["plan"].map(PRIX_PLANS).fillna(0).sum()

# ─── KPIs ─────────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💰 MRR", f"{mrr:,.0f}€", delta="Objectif: 1 000€")
c2.metric("👥 Utilisateurs", stats["total_users"], delta="Actifs")
c3.metric("🎯 Leads capturés", stats["total_leads"])
c4.metric("📧 Relances IA", stats["total_relances"])
c5.metric("✅ Taux succès", f"{stats['taux_succes_relances']:.0f}%")

st.divider()

tab_users, tab_leads, tab_mrr, tab_actions = st.tabs([
    "👥 Utilisateurs", "🎯 Leads", "💰 Projection MRR", "🚀 Actions prioritaires"
])

# ─── Tab Users ────────────────────────────────────────────────────────────────
with tab_users:
    st.subheader("Base utilisateurs")
    if users_df.empty:
        st.info("Aucun utilisateur enregistré pour l'instant. Partagez l'URL publique !")
    else:
        PLAN_COLORS = {"trial": "🟡", "starter": "🔵", "pro": "🟢", "scale": "⭐"}
        users_df["Plan"] = users_df["plan"].map(lambda p: f"{PLAN_COLORS.get(p,'⚪')} {p.title()}")
        st.dataframe(
            users_df[["email","nom","societe","Plan","created_at"]].rename(columns={
                "email":"Email","nom":"Nom","societe":"Société","created_at":"Inscrit le"
            }),
            hide_index=True, use_container_width=True,
        )
        plan_counts = users_df["plan"].value_counts()
        fig = go.Figure(go.Pie(
            labels=[f"{PLAN_COLORS.get(k,'⚪')} {k.title()}" for k in plan_counts.index],
            values=plan_counts.values,
            hole=0.5,
            marker_colors=["#F59E0B","#3B82F6","#10B981","#8B5CF6"],
        ))
        fig.update_layout(title="Répartition par plan", paper_bgcolor="#0A0F1E",
                          font=dict(color="white"), height=300)
        st.plotly_chart(fig, use_container_width=True)

# ─── Tab Leads ────────────────────────────────────────────────────────────────
with tab_leads:
    st.subheader("Leads capturés (formulaire landing page)")
    if leads_df.empty:
        st.info("Aucun lead pour l'instant — le formulaire de capture est actif sur la landing page.")
        st.markdown("""
        **Pour générer des leads :**
        - Partagez le lien du calculateur ROI
        - Publiez les posts LinkedIn du kit de vente
        - Envoyez les cold emails aux PME cibles
        """)
    else:
        st.metric("📧 Emails collectés", len(leads_df))
        st.dataframe(
            leads_df[["email","nom","societe","ca_estime","source","created_at"]].rename(columns={
                "email":"Email","nom":"Nom","societe":"Société",
                "ca_estime":"CA estimé €","source":"Source","created_at":"Date"
            }),
            column_config={"CA estimé €": st.column_config.NumberColumn(format="%.0f €")},
            hide_index=True, use_container_width=True,
        )
        csv = leads_df.to_csv(index=False).encode()
        st.download_button("📥 Exporter leads CSV", csv, "leads_invoiceguard.csv", "text/csv")

# ─── Tab MRR Projection ───────────────────────────────────────────────────────
with tab_mrr:
    st.subheader("Projection MRR sur 12 mois")
    st.caption("Simulez votre croissance selon différents scénarios d'acquisition")

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        nouveaux_par_mois = st.slider("Nouveaux clients/mois", 1, 50, 5)
    with col_s2:
        taux_churn = st.slider("Churn mensuel (%)", 0, 20, 5) / 100
    with col_s3:
        mix_plan = st.selectbox("Plan majoritaire", ["starter (49€)", "pro (149€)", "scale (399€)"])

    prix_moyen = {"starter (49€)": 49, "pro (149€)": 149, "scale (399€)": 399}[mix_plan]

    # Simulation
    mois = list(range(1, 13))
    clients_actifs = [mrr // prix_moyen if prix_moyen > 0 else 0]
    mrr_proj = [mrr]
    for m in mois[1:]:
        actifs_prev = clients_actifs[-1]
        churned = int(actifs_prev * taux_churn)
        actifs_new = actifs_prev - churned + nouveaux_par_mois
        clients_actifs.append(max(0, actifs_new))
        mrr_proj.append(max(0, actifs_new) * prix_moyen)

    labels_mois = [f"M{m}" for m in mois]
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=labels_mois, y=mrr_proj, marker_color="#00D4AA",
                          name="MRR projeté", text=[f"{v:,.0f}€" for v in mrr_proj],
                          textposition="outside"))
    fig2.add_trace(go.Scatter(x=labels_mois, y=clients_actifs, mode="lines+markers",
                              name="Clients actifs", yaxis="y2", line=dict(color="#F59E0B", width=2)))
    fig2.update_layout(
        paper_bgcolor="#0A0F1E", plot_bgcolor="#0A0F1E", font=dict(color="white"),
        yaxis=dict(title="MRR (€)", color="white", gridcolor="#1F2937"),
        yaxis2=dict(title="Clients", overlaying="y", side="right", color="#F59E0B"),
        xaxis=dict(color="white"), height=380, legend=dict(font=dict(color="white")),
        margin=dict(t=30, b=40),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Résumé
    mrr_m12 = mrr_proj[-1]
    arr = mrr_m12 * 12
    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("MRR à M12", f"{mrr_m12:,.0f}€")
    col_r2.metric("ARR à M12", f"{arr:,.0f}€")
    col_r3.metric("Clients à M12", f"{clients_actifs[-1]}")

# ─── Tab Actions ──────────────────────────────────────────────────────────────
with tab_actions:
    st.subheader("🚀 Prochaines actions prioritaires")

    actions = [
        {"Priorité": "🔴 Urgent", "Action": "Déployer sur Streamlit Cloud (URL permanente)", "Impact": "⭐⭐⭐⭐⭐", "Temps": "10 min"},
        {"Priorité": "🔴 Urgent", "Action": "Créer les plans Stripe (paiements réels)", "Impact": "⭐⭐⭐⭐⭐", "Temps": "20 min"},
        {"Priorité": "🟠 High", "Action": "Publier POST LINKEDIN n°1 (lundi 8h)", "Impact": "⭐⭐⭐⭐", "Temps": "5 min"},
        {"Priorité": "🟠 High", "Action": "Contacter 2 experts-comptables (email EC)", "Impact": "⭐⭐⭐⭐⭐", "Temps": "30 min"},
        {"Priorité": "🟡 Medium", "Action": "Envoyer 10 cold emails PME BTP/Transport", "Impact": "⭐⭐⭐", "Temps": "45 min"},
        {"Priorité": "🟡 Medium", "Action": "Partager l'URL Cloudflare à 5 contacts test", "Impact": "⭐⭐⭐", "Temps": "10 min"},
        {"Priorité": "🟢 Nice", "Action": "Lancer sur Product Hunt (fiche prête)", "Impact": "⭐⭐⭐", "Temps": "30 min"},
    ]
    st.dataframe(pd.DataFrame(actions), hide_index=True, use_container_width=True)

    st.divider()
    st.markdown("### 💡 Métriques à surveiller cette semaine")
    cols = st.columns(3)
    cols[0].info("**Leads** → Objectif : 10 emails collectés\n\n→ Via calculateur ROI + posts LinkedIn")
    cols[1].info("**Essais** → Objectif : 3 trials démarrés\n\n→ Via démo + partage URL")
    cols[2].info("**Payants** → Objectif : 1 client à 149€\n\n→ Via réseau + EC partenaire")
