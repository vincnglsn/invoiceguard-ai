"""
InvoiceGuard AI — Simulateur de Paiement Stripe
Simule la réception d'un paiement et marque les factures comme réglées.
Prépare l'intégration Stripe réelle (webhooks).
"""

import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
if not os.environ.get("GEMINI_API_KEY"):
    load_dotenv("../.env")
    load_dotenv("../worldmonitor_test/.env")

sys.path.insert(0, os.path.dirname(__file__))
from modules import invoice_scanner

st.set_page_config(page_title="InvoiceGuard — Paiements", page_icon="💳", layout="wide")

st.title("💳 Suivi des Paiements & Encaissements")
st.caption("Marquez les factures comme payées · Simulez des encaissements · Préparez l'intégration Stripe")

# ─── Chargement données ───────────────────────────────────────────────────────
if "df_paiements" not in st.session_state:
    df = invoice_scanner.load_demo_data()
    df["statut_paiement"] = df.apply(
        lambda r: "✅ Payé" if r["jours_retard"] == 0 else "⏳ En attente", axis=1
    )
    df["date_paiement"] = None
    df["mode_paiement"] = None
    st.session_state.df_paiements = df

df = st.session_state.df_paiements
kpis = invoice_scanner.get_kpis(df[df["statut_paiement"] != "✅ Payé"])

# ─── KPIs ─────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
payes = df[df["statut_paiement"] == "✅ Payé"]
en_attente = df[df["statut_paiement"] != "✅ Payé"]

c1.metric("💰 Total encaissé", f"{payes['montant'].sum():,.0f}€",
          delta=f"{len(payes)} factures réglées")
c2.metric("⏳ En attente", f"{en_attente['montant'].sum():,.0f}€",
          delta=f"{len(en_attente)} factures", delta_color="inverse")
c3.metric("📊 Taux de recouvrement",
          f"{payes['montant'].sum() / df['montant'].sum() * 100:.0f}%" if df['montant'].sum() > 0 else "0%")
c4.metric("🎯 Objectif mois", "100%",
          delta=f"{(payes['montant'].sum() / df['montant'].sum() * 100):.0f}% atteint" if df['montant'].sum() > 0 else "0%")

st.divider()

tab_encaiss, tab_historique, tab_stripe = st.tabs([
    ":material/payments: Marquer comme payé",
    ":material/history: Historique encaissements",
    ":material/credit_card: Intégration Stripe",
])

# ─── Tab 1 : Marquer comme payé ───────────────────────────────────────────────
with tab_encaiss:
    st.subheader("Enregistrer un paiement reçu")

    impayees = df[df["statut_paiement"] != "✅ Payé"].copy()

    if len(impayees) == 0:
        st.success("🎉 Toutes vos factures sont réglées ! Félicitations.")
    else:
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            options_pay = [
                f"{r['numero_facture']} — {r['client']} — {r['montant']:,.0f}€"
                for _, r in impayees.iterrows()
            ]
            selected_pay = st.selectbox("Facture à marquer comme payée", options_pay)
            idx_pay = options_pay.index(selected_pay)
            row_pay = impayees.iloc[idx_pay]

        with col_s2:
            montant_recu = st.number_input(
                "Montant reçu (€)",
                min_value=0.0,
                value=float(row_pay["montant"]),
                step=100.0,
            )

        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            date_paiement = st.date_input("Date de réception")
        with col_p2:
            mode_paiement = st.selectbox("Mode de paiement", [
                "Virement bancaire", "Chèque", "Prélèvement SEPA",
                "Carte bancaire", "Espèces", "Autre",
            ])
        with col_p3:
            ref_paiement = st.text_input("Référence (optionnel)",
                                          placeholder="Ex: VIR-20260920-001")

        # Pénalités LME calculées automatiquement
        retard = int(row_pay.get("jours_retard", 0))
        if retard > 0:
            taux_penalite = 0.13  # BCE + 10 points (taux 2026)
            penalite = float(row_pay["montant"]) * taux_penalite * retard / 365
            indemnite_forfaitaire = 40.0
            with st.container(border=True):
                st.markdown("#### ⚖️ Pénalités LME applicables")
                pc1, pc2, pc3 = st.columns(3)
                pc1.metric("Pénalités de retard", f"{penalite:.2f}€",
                           help=f"Taux LME : {taux_penalite*100:.0f}% × {retard}j")
                pc2.metric("Indemnité forfaitaire", f"{indemnite_forfaitaire:.0f}€",
                           help="40€ dus de droit pour tout retard")
                pc3.metric("Total réclamable", f"{penalite + indemnite_forfaitaire:.2f}€")
                appliquer_penalites = st.checkbox(
                    f"Réclamer les pénalités LME ({penalite + indemnite_forfaitaire:.2f}€ supplémentaires)",
                    value=False,
                )

        col_btn = st.columns([1, 3])
        with col_btn[0]:
            if st.button(":material/check_circle: Confirmer le paiement",
                         type="primary", use_container_width=True):
                # Mise à jour du dataframe
                mask = st.session_state.df_paiements["numero_facture"] == row_pay["numero_facture"]
                st.session_state.df_paiements.loc[mask, "statut_paiement"] = "✅ Payé"
                st.session_state.df_paiements.loc[mask, "date_paiement"] = str(date_paiement)
                st.session_state.df_paiements.loc[mask, "mode_paiement"] = mode_paiement

                # Ajout à l'historique
                if "historique_encaissements" not in st.session_state:
                    st.session_state.historique_encaissements = []
                st.session_state.historique_encaissements.append({
                    "Date": str(date_paiement),
                    "Facture": row_pay["numero_facture"],
                    "Client": row_pay["client"],
                    "Montant reçu": montant_recu,
                    "Mode": mode_paiement,
                    "Référence": ref_paiement or "—",
                    "Pénalités": f"{penalite + indemnite_forfaitaire:.2f}€" if retard > 0 and appliquer_penalites else "—",
                    "Enregistré le": datetime.now().strftime("%d/%m/%Y %H:%M"),
                })
                st.success(f"✅ Paiement de **{montant_recu:,.2f}€** enregistré pour **{row_pay['client']}** !")
                st.rerun()

# ─── Tab 2 : Historique ───────────────────────────────────────────────────────
with tab_historique:
    st.subheader("Historique des encaissements")

    hist = st.session_state.get("historique_encaissements", [])
    if not hist:
        st.info("Aucun paiement enregistré pour l'instant. Marquez des factures comme payées dans l'onglet précédent.")
    else:
        df_hist = pd.DataFrame(hist)
        total_encaisse = sum(h["Montant reçu"] for h in hist)
        st.metric("💰 Total encaissé dans cette session", f"{total_encaisse:,.2f}€")
        st.dataframe(df_hist, hide_index=True, use_container_width=True)
        csv = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button(":material/download: Exporter CSV", csv,
                           "historique_encaissements.csv", "text/csv")

    st.divider()
    st.subheader("État complet du portefeuille")
    display_cols = [c for c in ["numero_facture","client","montant","jours_retard",
                                 "statut_paiement","date_paiement","mode_paiement"]
                    if c in df.columns]
    st.dataframe(
        df[display_cols].rename(columns={
            "numero_facture": "N° Facture", "client": "Client",
            "montant": "Montant €", "jours_retard": "Retard (j)",
            "statut_paiement": "Statut", "date_paiement": "Date paiement",
            "mode_paiement": "Mode",
        }),
        column_config={"Montant €": st.column_config.NumberColumn(format="%.2f €")},
        hide_index=True, use_container_width=True,
    )

# ─── Tab 3 : Stripe ──────────────────────────────────────────────────────────
with tab_stripe:
    st.subheader(":material/credit_card: Intégration Stripe Payments")
    st.markdown("""
    Connectez Stripe pour recevoir les paiements en ligne directement depuis vos relances.
    Vos clients pourront payer en 1 clic depuis l'email de relance.
    """)

    with st.container(border=True):
        st.markdown("#### 🔑 Configuration Stripe")
        stripe_key = st.text_input(
            "Clé secrète Stripe (sk_live_...)",
            type="password",
            placeholder="sk_live_xxxxxxxxxxxxxxxxxxxx",
            help="Trouvez votre clé dans https://dashboard.stripe.com/apikeys",
        )
        stripe_pub = st.text_input(
            "Clé publique Stripe (pk_live_...)",
            placeholder="pk_live_xxxxxxxxxxxxxxxxxxxx",
        )

        if stripe_key and stripe_pub:
            st.success("✅ Clés Stripe configurées — prêt pour les paiements en ligne !")
            st.info("💡 Pour activer les paiements réels, intégrez stripe-python dans modules/email_sender.py")
        else:
            st.warning("⚠️ Ajoutez vos clés Stripe pour activer les paiements en ligne")

    st.divider()
    st.markdown("#### 📋 Comment ça fonctionnera")
    steps_stripe = [
        ("1", "Client reçoit email de relance InvoiceGuard"),
        ("2", "Email contient un lien de paiement Stripe sécurisé"),
        ("3", "Client clique et paye en CB en 30 secondes"),
        ("4", "Stripe webhook notifie InvoiceGuard automatiquement"),
        ("5", "Facture marquée payée · Email de reçu envoyé · Dashboard mis à jour"),
    ]
    for num, desc in steps_stripe:
        col_sn, col_sd = st.columns([0.5, 9])
        with col_sn:
            st.markdown(f"**{num}.**")
        with col_sd:
            st.markdown(desc)

    st.divider()
    st.info("""
    **💡 Prochaine étape de développement :**
    - Installer `stripe` : `pip install stripe`
    - Créer des Payment Links Stripe pour chaque facture
    - Intégrer le lien dans les emails de relance générés par l'IA
    - Configurer le webhook Stripe pour mise à jour automatique
    """)
