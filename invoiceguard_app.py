"""
InvoiceGuard AI — Application Principale v2
Récupérez automatiquement vos factures impayées grâce à l'IA.
Version complète : Dashboard · Factures · Relance IA · Campagne · Rapport PDF · Analyse
"""

import streamlit as st
import pandas as pd
import os
import sys
from dotenv import load_dotenv

load_dotenv()
if not os.environ.get("GEMINI_API_KEY"):
    load_dotenv("../.env")
    load_dotenv("../worldmonitor_test/.env")

sys.path.insert(0, os.path.dirname(__file__))

from modules import invoice_scanner, ai_agent, email_sender, dashboard
from modules import campaign as campaign_mod
try:
    from modules import pdf_export
    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False

# ─── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InvoiceGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.html("""
<style>
  [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 800 !important; }
  .ig-badge {
    display:inline-block; padding:2px 10px; border-radius:99px;
    font-size:.78rem; font-weight:700;
  }
  .ig-badge.red   { background:#FF4B4B22; color:#FF4B4B; }
  .ig-badge.orange{ background:#FFA50022; color:#FFA500; }
  .ig-badge.green { background:#00C85322; color:#00C853; }
  .campaign-card {
    background:#1F2937; border-radius:12px; padding:1.2rem 1.5rem;
    border:1px solid #374151; margin-bottom:.8rem;
  }
  .step-label {
    font-size:.8rem; font-weight:700; color:#00D4AA;
    text-transform:uppercase; letter-spacing:.05em;
  }
</style>
""")

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ InvoiceGuard AI")
    st.caption("Recouvrement intelligent · Loi LME · RGPD")
    st.divider()

    st.markdown("### :material/upload_file: Source de données")
    mode_source = st.radio(
        "Source",
        ["📊 Démonstration (12 factures)", "📁 Importer un CSV"],
        label_visibility="collapsed",
    )

    df_factures = None
    if mode_source == "📁 Importer un CSV":
        uploaded = st.file_uploader("Vos factures (CSV)", type=["csv"],
            help="Colonnes : client, montant, date_echeance, email_client")
        if uploaded:
            try:
                df_factures = invoice_scanner.load_from_csv(uploaded.read())
                st.success(f"✅ {len(df_factures)} factures chargées")
            except Exception as e:
                st.error(f"Erreur : {e}")
    else:
        df_factures = invoice_scanner.load_demo_data()
        st.info("📊 Mode démo · 12 factures exemples")

    st.divider()
    st.markdown("### :material/settings: Options")
    mode_demo_emails = st.toggle("Simuler les envois (démo)", value=True)
    st.divider()

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if api_key:
        st.success(":material/check_circle: Gemini connecté")
    else:
        st.error(":material/error: Clé API manquante")
        with st.expander("Comment configurer ?"):
            st.code('GEMINI_API_KEY=votre_clé_ici', language="bash")
            st.caption("Ajoutez cette ligne dans votre fichier `.env`")

    st.divider()
    st.caption("v2.0 · InvoiceGuard AI")
    st.caption("🇫🇷 Made in France")

# ─── Garde principale ─────────────────────────────────────────────────────────
if df_factures is None or len(df_factures) == 0:
    st.title("🛡️ InvoiceGuard AI")
    st.info("Chargez vos données via la barre latérale.")
    st.stop()

kpis = invoice_scanner.get_kpis(df_factures)

# ─── Header ──────────────────────────────────────────────────────────────────
col_h1, col_h2, col_h3 = st.columns([3, 1, 1])
with col_h1:
    st.title("🛡️ InvoiceGuard AI")
    st.caption("Tableau de bord de recouvrement intelligent")
with col_h2:
    st.metric("DSO", f"{kpis['dso']}j", help="Days Sales Outstanding — plus c'est bas, mieux c'est")
with col_h3:
    st.metric("Taux retard", f"{kpis['taux_retard_pct']:.0f}%",
              delta="du portefeuille", delta_color="inverse")

st.divider()

# ─── Navigation ──────────────────────────────────────────────────────────────
tabs = st.tabs([
    ":material/dashboard: Dashboard",
    ":material/receipt_long: Factures",
    ":material/robot: Relance IA",
    ":material/campaign: Campagne",
    ":material/analytics: Analyse IA",
    ":material/picture_as_pdf: Rapport PDF",
])

tab_dash, tab_fact, tab_relance, tab_camp, tab_analyse, tab_pdf = tabs

# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
with tab_dash:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(":material/payments: Total facturé", f"{kpis['montant_total']:,.0f}€")
    c2.metric(":material/warning: En retard", f"{kpis['montant_en_retard']:,.0f}€",
              delta=f"{kpis['nb_en_retard']} factures", delta_color="inverse")
    c3.metric(":material/crisis_alert: Critiques", f"{kpis['nb_critiques']} dossiers",
              delta=f"{kpis['montant_critique']:,.0f}€", delta_color="inverse")
    c4.metric(":material/trending_up: Récupérable (est.)",
              f"{kpis['montant_en_retard'] * 0.72:,.0f}€",
              delta="~72% taux moyen de recouvrement")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(dashboard.chart_repartition_retards(df_factures), use_container_width=True)
    with col2:
        st.plotly_chart(dashboard.chart_top_debiteurs(df_factures), use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(dashboard.chart_timeline_encaissements(df_factures), use_container_width=True)
    with col4:
        st.plotly_chart(dashboard.chart_score_risque(df_factures), use_container_width=True)

    # Alerte intelligente
    critiques = df_factures[df_factures["score_risque"] >= 70]
    if len(critiques) > 0:
        montant_crit = critiques["montant"].sum()
        st.error(
            f"⚡ **{len(critiques)} dossier(s) critique(s)** représentant **{montant_crit:,.0f}€** "
            f"nécessitent une action immédiate. → Allez dans l'onglet **Campagne** pour lancer une relance groupée.",
            icon=":material/crisis_alert:",
        )

# ═══════════════════════════════════════════════════════════════════════════
# FACTURES
# ═══════════════════════════════════════════════════════════════════════════
with tab_fact:
    st.subheader("Portefeuille de factures")

    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        filtre_prio = st.multiselect("Priorité", df_factures["priorite"].unique().tolist(),
                                     default=df_factures["priorite"].unique().tolist())
    with col_f2:
        retard_min = st.number_input("Retard min. (j)", 0, value=0)
    with col_f3:
        montant_min = st.number_input("Montant min. (€)", 0, value=0)
    with col_f4:
        tri = st.selectbox("Trier par", ["score_risque", "montant", "jours_retard", "client"])

    mask = (
        df_factures["priorite"].isin(filtre_prio) &
        (df_factures["jours_retard"] >= retard_min) &
        (df_factures["montant"] >= montant_min)
    )
    df_f = df_factures[mask].sort_values(tri, ascending=False)

    cols_show = [c for c in ["numero_facture","client","montant","date_echeance","jours_retard","priorite","score_risque"]
                 if c in df_f.columns]

    st.dataframe(
        df_f[cols_show].rename(columns={
            "numero_facture":"N° Facture","client":"Client",
            "montant":"Montant (€)","date_echeance":"Échéance",
            "jours_retard":"Retard (j)","priorite":"Priorité","score_risque":"Score Risque",
        }),
        column_config={
            "Montant (€)": st.column_config.NumberColumn(format="%.2f €"),
            "Score Risque": st.column_config.ProgressColumn(min_value=0, max_value=100),
            "Échéance": st.column_config.DateColumn(format="DD/MM/YYYY"),
        },
        hide_index=True,
        use_container_width=True,
    )
    st.caption(f"**{len(df_f)}** factures · Total : **{df_f['montant'].sum():,.2f}€**")

    # Export CSV
    csv_bytes = df_f.to_csv(index=False).encode("utf-8")
    st.download_button(
        ":material/download: Exporter CSV",
        csv_bytes, "invoiceguard_export.csv", "text/csv",
    )

# ═══════════════════════════════════════════════════════════════════════════
# RELANCE IA (facture unique)
# ═══════════════════════════════════════════════════════════════════════════
with tab_relance:
    st.subheader(":material/robot: Agent de Relance IA")
    st.caption("Relance ultra-personnalisée · Adapté au droit français (LME) · Ton automatique")

    if "historique_relances" not in st.session_state:
        st.session_state.historique_relances = []

    en_retard = df_factures[df_factures["jours_retard"] > 0].sort_values("score_risque", ascending=False)

    if len(en_retard) == 0:
        st.success("✅ Aucune facture en retard — votre trésorerie est saine !")
    else:
        options = [
            f"{r['numero_facture']} — {r['client']} — {r['montant']:,.0f}€ ({int(r['jours_retard'])}j) {r['priorite']}"
            for _, r in en_retard.iterrows()
        ]
        idx_map = {o: i for i, o in enumerate(options)}

        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            sel = st.selectbox("Sélectionner une facture", options)
        row = en_retard.iloc[idx_map[sel]]
        with col_s2:
            st.metric("Score risque", f"{int(row['score_risque'])}/100")

        # Info facture
        with st.container(border=True):
            ci1, ci2, ci3, ci4 = st.columns(4)
            ci1.metric("Client", row["client"])
            ci2.metric("Montant", f"{row['montant']:,.0f}€")
            ci3.metric("Retard", f"{int(row['jours_retard'])}j")
            ci4.metric("Priorité", row["priorite"])

        # Options
        col_o1, col_o2, col_o3 = st.columns(3)
        with col_o1:
            canal = st.segmented_control("Canal", ["email", "sms"], default="email",
                format_func=lambda x: "📧 Email" if x == "email" else "📱 SMS")
        with col_o2:
            ton = st.selectbox("Ton", ["auto","doux","ferme","urgent","mise_en_demeure"],
                format_func=lambda x: {"auto":"🤖 Auto","doux":"😊 Doux","ferme":"😐 Ferme",
                                       "urgent":"😤 Urgent","mise_en_demeure":"⚖️ Mise en demeure"}[x])
        with col_o3:
            email_dest = st.text_input("Email", value=row.get("email_client",""))

        if not api_key:
            st.error("⚠️ Clé Gemini requise.")
        else:
            if st.button(":material/auto_awesome: Générer la relance", type="primary"):
                with st.spinner("✍️ Rédaction en cours..."):
                    try:
                        res = ai_agent.generer_relance(
                            client_nom=row["client"], montant=float(row["montant"]),
                            numero_facture=row["numero_facture"],
                            date_echeance=str(row["date_echeance"])[:10],
                            jours_retard=int(row["jours_retard"]),
                            canal=canal or "email", ton=ton,
                        )
                        st.session_state.relance_res = res
                        st.session_state.relance_row_id = row["numero_facture"]
                    except Exception as e:
                        st.error(f"Erreur IA : {e}")

            if "relance_res" in st.session_state:
                res = st.session_state.relance_res
                st.divider()
                st.markdown(f"**Ton :** `{res['ton_utilise']}` · **Canal :** `{canal}`")
                if canal == "email":
                    st.markdown(f"**📧 Objet :** {res['sujet']}")
                body = st.text_area("Message (éditable)", res["corps"], height=280,
                                    label_visibility="collapsed")

                col_b1, col_b2, col_b3 = st.columns(3)
                with col_b1:
                    if st.button(":material/send: Envoyer", type="primary", use_container_width=True):
                        send_res = email_sender.envoyer_email(
                            destinataire=email_dest or "demo@invoiceguard.fr",
                            sujet=res["sujet"], corps=body, mode_demo=mode_demo_emails,
                        )
                        if send_res["success"]:
                            st.success(f"✅ {'Simulé' if mode_demo_emails else 'Envoyé'} ! ID: {send_res['message_id']}")
                            log = email_sender.log_relance(
                                row["numero_facture"], row["client"],
                                canal or "email", res["ton_utilise"], send_res,
                            )
                            st.session_state.historique_relances.append(log)
                        else:
                            st.error(f"❌ {send_res.get('error')}")
                with col_b2:
                    st.download_button(":material/download: Télécharger",
                                       body.encode(), f"relance_{row['numero_facture']}.txt")
                with col_b3:
                    st.info("💡 Ou copiez-collez dans votre messagerie")

        if st.session_state.historique_relances:
            st.divider()
            st.subheader("📋 Historique des relances")
            st.dataframe(pd.DataFrame(st.session_state.historique_relances),
                         hide_index=True, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# CAMPAGNE EN MASSE
# ═══════════════════════════════════════════════════════════════════════════
with tab_camp:
    st.subheader(":material/campaign: Campagne de Relances en Masse")
    st.caption("Lancez une relance orchestrée sur tout ou partie de votre portefeuille")

    col_camp1, col_camp2 = st.columns([1, 1])

    with col_camp1:
        st.markdown("### 🎯 1. Ciblage")
        critere = st.selectbox("Cibles de la campagne", [
            "all_late", "critiques", "elevees", "over_30j", "over_60j"
        ], format_func=lambda x: {
            "all_late":   "🔴 Toutes les factures en retard",
            "critiques":  "🚨 Dossiers critiques uniquement (score ≥70)",
            "elevees":    "⚠️  Priorité élevée+ (score ≥40)",
            "over_30j":   "📅 Retard > 30 jours",
            "over_60j":   "📅 Retard > 60 jours",
        }[x])

    with col_camp2:
        st.markdown("### 📋 2. Séquence de relance")
        sequence = st.selectbox("Stratégie", ["standard", "agressive", "douce"],
            format_func=lambda x: {
                "standard": "Standard (4 étapes sur 21j)",
                "agressive": "Agressive (3 étapes sur 7j)",
                "douce": "Douce (3 étapes sur 30j)",
            }[x])

    # Calcul des cibles
    targets = campaign_mod.filter_campaign_targets(df_factures, critere)
    estimation = campaign_mod.estimate_recovery(targets)
    plan = campaign_mod.build_campaign_plan(targets, sequence)

    # Métriques campagne
    st.divider()
    cm1, cm2, cm3, cm4 = st.columns(4)
    cm1.metric("Factures ciblées", len(targets))
    cm2.metric("Montant total en jeu", f"{estimation['total_en_jeu']:,.0f}€")
    cm3.metric("Montant récupérable (est.)", f"{estimation['total_recuperable']:,.0f}€",
               delta=f"~{estimation['taux_global']*100:.0f}% de recouvrement")
    cm4.metric("Commission InvoiceGuard", f"{estimation['commission_invoiceguard']:,.0f}€",
               help="3% sur le montant récupéré — vous payez sur les résultats")

    # Visualisation par tranche
    if estimation["par_tranche"]:
        st.divider()
        st.markdown("#### Détail par ancienneté")
        tranche_data = []
        for tranche, d in estimation["par_tranche"].items():
            tranche_data.append({
                "Tranche": tranche,
                "Nb factures": d["nb"],
                "Montant total": f"{d['montant_total']:,.0f}€",
                "Récupérable": f"{d['montant_recuperable']:,.0f}€",
                "Taux recouvrement": f"{d['taux']*100:.0f}%",
            })
        st.dataframe(pd.DataFrame(tranche_data), hide_index=True, use_container_width=True)

    # Plan de campagne
    if len(plan) > 0:
        st.divider()
        st.markdown("#### 📅 Plan d'envoi généré")
        st.dataframe(
            plan[["client","numero_facture","montant","date_envoi","etape","ton","canal"]].rename(columns={
                "client":"Client","numero_facture":"Facture","montant":"Montant €",
                "date_envoi":"Date envoi","etape":"Étape","ton":"Ton","canal":"Canal",
            }),
            column_config={
                "Montant €": st.column_config.NumberColumn(format="%.0f €"),
            },
            hide_index=True, use_container_width=True,
        )

        st.divider()
        # Lancement de la campagne IA
        if not api_key:
            st.error("⚠️ Clé Gemini requise pour générer les messages.")
        else:
            col_launch1, col_launch2 = st.columns([1, 2])
            with col_launch1:
                launch_btn = st.button(
                    f":material/rocket_launch: Lancer la campagne ({len(targets)} relances)",
                    type="primary", use_container_width=True,
                )
            with col_launch2:
                st.info(f"✏️ L'IA va rédiger **{len(targets)}** messages personnalisés — "
                        f"{'simulés' if mode_demo_emails else 'envoyés réellement'}")

            if launch_btn:
                results = []
                progress = st.progress(0, text="Initialisation...")
                status_placeholder = st.empty()

                for i, (_, target) in enumerate(targets.iterrows()):
                    pct = (i + 1) / len(targets)
                    progress.progress(pct, text=f"⚙️ Traitement de {target['client']}... ({i+1}/{len(targets)})")

                    try:
                        msg = ai_agent.generer_relance(
                            client_nom=target["client"],
                            montant=float(target["montant"]),
                            numero_facture=target["numero_facture"],
                            date_echeance=str(target["date_echeance"])[:10],
                            jours_retard=int(target["jours_retard"]),
                            canal="email", ton="auto",
                        )
                        send_res = email_sender.envoyer_email(
                            destinataire=target.get("email_client", "demo@invoiceguard.fr"),
                            sujet=msg["sujet"], corps=msg["corps"],
                            mode_demo=mode_demo_emails,
                        )
                        results.append({
                            "client": target["client"],
                            "facture": target["numero_facture"],
                            "montant": f"{target['montant']:,.0f}€",
                            "ton": msg["ton_utilise"],
                            "statut": "✅ Envoyé" if send_res["success"] else "❌ Erreur",
                        })
                    except Exception as e:
                        results.append({
                            "client": target["client"],
                            "facture": target["numero_facture"],
                            "montant": f"{target['montant']:,.0f}€",
                            "ton": "—", "statut": f"❌ {e}",
                        })

                progress.empty()
                nb_ok = sum(1 for r in results if "✅" in r["statut"])
                st.success(f"🎉 Campagne terminée ! **{nb_ok}/{len(targets)}** relances envoyées avec succès.")
                st.dataframe(pd.DataFrame(results), hide_index=True, use_container_width=True)

                # Ajout à l'historique global
                for r in results:
                    st.session_state.setdefault("historique_relances", []).append({
                        "numero_facture": r["facture"],
                        "client": r["client"],
                        "canal": "email",
                        "ton": r["ton"],
                        "date_envoi": pd.Timestamp("today").strftime("%d/%m/%Y %H:%M"),
                        "succes": "✅" in r["statut"],
                        "message_id": "campagne",
                    })

# ═══════════════════════════════════════════════════════════════════════════
# ANALYSE IA
# ═══════════════════════════════════════════════════════════════════════════
with tab_analyse:
    st.subheader(":material/psychology: Analyse IA du portefeuille")
    st.caption("Diagnostic personnalisé + Recommandations d'actions prioritaires")

    if not api_key:
        st.error("⚠️ Clé Gemini requise.")
    else:
        col_a1, col_a2 = st.columns([1, 2])
        with col_a1:
            if st.button(":material/play_arrow: Lancer l'analyse complète",
                         type="primary", use_container_width=True):
                en_ret = df_factures[df_factures["jours_retard"] > 0]
                lignes = [
                    f"- {r['client']} : {r['montant']:,.0f}€ — {int(r['jours_retard'])}j retard ({r['priorite']})"
                    for _, r in en_ret.iterrows()
                ]
                resume = "\n".join(lignes)
                resume += f"\n\nTotal : {kpis['montant_en_retard']:,.0f}€ · {kpis['nb_en_retard']} factures · DSO={kpis['dso']}j"

                with st.spinner("🧠 Analyse en cours..."):
                    try:
                        st.session_state.analyse_result = ai_agent.analyser_portefeuille(resume)
                    except Exception as e:
                        st.error(f"Erreur : {e}")

        if "analyse_result" in st.session_state:
            with st.container(border=True):
                st.markdown("### 📋 Rapport d'analyse IA")
                st.markdown(st.session_state.analyse_result)

        st.divider()
        st.subheader("💬 Assistant trésorerie IA")
        st.caption("Posez n'importe quelle question sur vos impayés, votre DSO, votre stratégie...")

        if "chat_analyse" not in st.session_state:
            st.session_state.chat_analyse = []

        for msg in st.session_state.chat_analyse:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ex: Quels clients appeler en priorité ? Comment réduire mon DSO ?"):
            st.session_state.chat_analyse.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                try:
                    from google import genai as _g
                    from google.genai import types as _t
                    c = _g.Client(api_key=api_key)
                    sys_p = (
                        "Tu es expert en recouvrement et trésorerie pour PME françaises. "
                        "Connais la Loi LME, RGPD, injonction de payer. Réponds en français, "
                        f"de façon concise et actionnable. Contexte : {kpis['nb_en_retard']} factures "
                        f"en retard ({kpis['montant_en_retard']:,.0f}€), DSO={kpis['dso']}j."
                    )
                    hist = [
                        _t.Content(role="user" if m["role"]=="user" else "model",
                                   parts=[_t.Part.from_text(text=m["content"])])
                        for m in st.session_state.chat_analyse[:-1]
                    ]
                    hist.append(_t.Content(role="user", parts=[_t.Part.from_text(text=prompt)]))
                    resp = c.models.generate_content(
                        model="gemini-2.5-flash", contents=hist,
                        config=_t.GenerateContentConfig(system_instruction=sys_p, temperature=0.4),
                    )
                    answer = resp.text
                    st.markdown(answer)
                    st.session_state.chat_analyse.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Erreur : {e}")

# ═══════════════════════════════════════════════════════════════════════════
# RAPPORT PDF
# ═══════════════════════════════════════════════════════════════════════════
with tab_pdf:
    st.subheader(":material/picture_as_pdf: Rapport PDF Professionnel")
    st.caption("Générez un rapport complet pour votre expert-comptable ou votre DAF")

    col_p1, col_p2 = st.columns([1, 1])

    with col_p1:
        with st.container(border=True):
            st.markdown("#### 📄 Contenu du rapport")
            incl_kpis = st.checkbox("KPIs de synthèse", value=True)
            incl_table = st.checkbox("Tableau des factures en retard", value=True)
            incl_legal = st.checkbox("Mentions légales (LME)", value=True)
            incl_analyse = st.checkbox("Analyse IA (si disponible)", value=True)

    with col_p2:
        with st.container(border=True):
            st.markdown("#### ℹ️ Aperçu du rapport")
            en_ret = df_factures[df_factures["jours_retard"] > 0]
            st.write(f"**Pages estimées :** {1 + len(en_ret)//20}")
            st.write(f"**Factures en retard :** {len(en_ret)}")
            st.write(f"**Montant total :** {kpis['montant_en_retard']:,.0f}€")
            st.write(f"**Analyse IA :** {'✅ Disponible' if 'analyse_result' in st.session_state else '⚠️ Non générée (onglet Analyse IA)'}")

    st.divider()

    if not PDF_AVAILABLE:
        st.warning("⚠️ Module PDF non disponible. Lancez : `pip install fpdf2`")
    else:
        if st.button(":material/picture_as_pdf: Générer le rapport PDF", type="primary"):
            with st.spinner("📄 Génération du rapport..."):
                try:
                    analyse_txt = st.session_state.get("analyse_result", "") if incl_analyse else ""
                    pdf_bytes = pdf_export.generer_rapport_pdf(df_factures, kpis, analyse_txt)
                    from datetime import date as _date
                    filename = f"invoiceguard_rapport_{_date.today().strftime('%Y%m%d')}.pdf"
                    st.success("✅ Rapport généré !")
                    st.download_button(
                        ":material/download: Télécharger le PDF",
                        pdf_bytes, filename, "application/pdf",
                        use_container_width=True,
                        type="primary",
                    )
                except Exception as e:
                    st.error(f"Erreur génération PDF : {e}")

    st.divider()
    st.markdown("#### 💡 Conseils d'utilisation du rapport")
    with st.expander("Pour votre expert-comptable"):
        st.markdown("""
- Partagez ce rapport **chaque mois** avec votre EC pour qu'il suive l'évolution de votre DSO
- Le tableau des factures en retard lui permet d'intégrer les provisions pour créances douteuses
- Les mentions légales LME incluses valident la conformité de vos relances
        """)
    with st.expander("Pour votre DAF ou investisseurs"):
        st.markdown("""
- Le DSO et le taux de retard sont des **indicateurs clés de santé financière**
- La prévision d'encaissement sur 90j aide à planifier la trésorerie
- Le rapport peut être joint aux reporting mensuels et aux reportings de covenants bancaires
        """)
