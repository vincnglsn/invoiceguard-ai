"""
InvoiceGuard AI — Page de Vente & Abonnement Stripe
Interface pour choisir un plan et être redirigé vers le paiement Stripe.
"""

import streamlit as st
import os

st.set_page_config(
    page_title="InvoiceGuard AI — Choisir un plan",
    page_icon="💳",
    layout="centered",
)

st.html("""
<style>
  .plan-card {
    background: #1F2937;
    border-radius: 16px;
    padding: 2rem;
    border: 1px solid #374151;
    text-align: center;
    transition: all .2s;
  }
  .plan-card.featured {
    border: 2px solid #00D4AA;
    background: linear-gradient(135deg, rgba(0,212,170,0.08) 0%, #1F2937 100%);
  }
  .price-tag { font-size: 3rem; font-weight: 900; color: #00D4AA; }
  .plan-title { font-size: 1.3rem; font-weight: 700; margin-bottom: .5rem; }
</style>
""")

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("## 🛡️ InvoiceGuard AI")
st.markdown("### Choisissez votre plan et commencez à récupérer vos impayés dès aujourd'hui")
st.caption("✅ 14 jours gratuits · Résiliable à tout moment · Conforme RGPD")
st.divider()

# ─── Compteur d'urgence ───────────────────────────────────────────────────────
from datetime import datetime
heure = datetime.now().hour
if heure < 12:
    st.info("☀️ **Offre de lancement** : -30% sur le plan Pro ce mois-ci. Code : `LAUNCH30`")
else:
    st.warning("⏰ **Offre limitée** : Accès à vie au plan Starter pour les 20 premiers inscrits. Il reste 7 places.")

st.divider()

# ─── Plans ────────────────────────────────────────────────────────────────────
# REMPLACEZ ces URLs par vos vrais liens Stripe Payment Links
STRIPE_LINKS = {
    "starter": "https://buy.stripe.com/VOTRE_LIEN_STARTER",
    "pro":     "https://buy.stripe.com/VOTRE_LIEN_PRO",
    "scale":   "https://buy.stripe.com/VOTRE_LIEN_SCALE",
}

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("#### Starter")
        st.markdown("**49€**/mois")
        st.caption("Pour les indépendants et TPE")
        st.markdown("""
- ✅ 50 factures/mois
- ✅ Relances email auto
- ✅ Dashboard trésorerie
- ✅ Score de risque
- ✅ Support email
- ❌ SMS
- ❌ PDF rapport
        """)
        st.link_button("Démarrer — 49€/mois", STRIPE_LINKS["starter"],
                       use_container_width=True)
        st.caption("14 jours gratuits")

with col2:
    with st.container(border=True):
        st.markdown("#### ⭐ Pro — Recommandé")
        st.markdown("**149€**/mois")
        st.caption("Pour les PME (10-200 salariés)")
        st.markdown("""
- ✅ Factures illimitées
- ✅ Email + SMS
- ✅ Agent IA négociateur
- ✅ Campagnes en masse
- ✅ Rapport PDF mensuel
- ✅ Intégration Pennylane/Sage
- ✅ Support prioritaire
        """)
        st.link_button("Démarrer — 149€/mois", STRIPE_LINKS["pro"],
                       type="primary", use_container_width=True)
        st.caption("14 jours gratuits · Le plus populaire")

with col3:
    with st.container(border=True):
        st.markdown("#### Scale")
        st.markdown("**399€**/mois")
        st.caption("Pour les ETI et cabinets EC")
        st.markdown("""
- ✅ Tout le plan Pro
- ✅ Multi-utilisateurs (5)
- ✅ API complète
- ✅ Dashboard CFO avancé
- ✅ Onboarding dédié
- ✅ SLA 99.9%
- ✅ Espace partenaire EC
        """)
        st.link_button("Démarrer — 399€/mois", STRIPE_LINKS["scale"],
                       use_container_width=True)
        st.caption("14 jours gratuits")

st.divider()

# ─── Commission au résultat ───────────────────────────────────────────────────
with st.container(border=True):
    st.markdown("### 🎯 + Commission au résultat (tous plans)")
    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("Taux de commission", "3%", help="Sur chaque euro récupéré grâce à l'IA")
    col_r2.metric("Exemple", "+438€",
                  delta="Si vous récupérez 14 600€ d'impayés")
    col_r3.metric("Principe", "Pay-as-you-win",
                  delta="Vous ne payez que sur les succès")
    st.caption("La commission est calculée automatiquement et facturée en fin de mois.")

st.divider()

# ─── FAQ rapide ──────────────────────────────────────────────────────────────
st.markdown("### Questions fréquentes")

with st.expander("Comment fonctionne l'essai gratuit ?"):
    st.markdown("""
14 jours complets, sans carte bancaire requise. Accès à toutes les fonctionnalités du plan choisi.
À la fin des 14 jours, vous choisissez de continuer ou non. Aucun prélèvement automatique sans votre accord.
    """)

with st.expander("Mes données sont-elles sécurisées ?"):
    st.markdown("""
Oui. InvoiceGuard est hébergé en France, conforme RGPD. Vos données de facturation ne quittent jamais le territoire européen.
Chiffrement AES-256 au repos et TLS 1.3 en transit.
    """)

with st.expander("Est-ce que ça fonctionne avec mon logiciel de facturation ?"):
    st.markdown("""
Actuellement : import CSV universel (compatible avec Pennylane, Sage, Cegid, QuickBooks, EBP).
Prochainement : connecteurs API natifs Pennylane et Sage (Q1 2027).
    """)

with st.expander("Puis-je résilier à tout moment ?"):
    st.markdown("Oui, sans préavis, depuis votre espace client. Aucun frais de résiliation.")

st.divider()

# ─── CTA final ───────────────────────────────────────────────────────────────
st.markdown("### Prêt à récupérer vos impayés ?")
col_cta1, col_cta2 = st.columns([2, 1])
with col_cta1:
    st.link_button("🚀 Commencer l'essai gratuit (Plan Pro)",
                   STRIPE_LINKS["pro"], type="primary", use_container_width=True)
with col_cta2:
    st.link_button("📅 Voir une démo en direct",
                   "https://calendly.com/invoiceguard/demo-15min",
                   use_container_width=True)

st.caption("🔒 Paiement sécurisé par Stripe · Données hébergées en France · RGPD")
