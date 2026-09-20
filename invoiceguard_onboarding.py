"""
InvoiceGuard AI -- Onboarding Guide
Parcours guide interactif pour la premiere utilisation.
Etape 1 : Compte  |  Etape 2 : Import  |  Etape 3 : Relance  |  Etape 4 : Dashboard
"""

import streamlit as st
import os, sys, time
from dotenv import load_dotenv

load_dotenv()
if not os.environ.get("GEMINI_API_KEY"):
    load_dotenv("../.env")

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="Demarrage — InvoiceGuard AI",
    page_icon="🛡️",
    layout="centered",
)

st.html("""<style>
[data-testid="stAppViewContainer"] { background: #0A0F1E; }
.step-done  { background:#00D4AA22; border:1px solid #00D4AA; border-radius:10px; padding:12px 16px; margin:6px 0; }
.step-active{ background:#3B82F622; border:1px solid #3B82F6; border-radius:10px; padding:12px 16px; margin:6px 0; }
.step-todo  { background:#1F293780; border:1px solid #374151; border-radius:10px; padding:12px 16px; margin:6px 0; color:#6B7280; }
</style>""")

# ─── State ────────────────────────────────────────────────────────────────────
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = 1

step = st.session_state.onboarding_step

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("## 🛡️ InvoiceGuard AI — Demarrage")
st.caption("Vous serez operationnel en moins de 5 minutes")

# Barre de progression
progress = (step - 1) / 4
st.progress(progress, text=f"Etape {step}/4")
st.divider()

# ─── Etapes laterales ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Parcours d'installation")
    etapes = [
        (1, "Votre compte"),
        (2, "Importer vos factures"),
        (3, "Premiere relance IA"),
        (4, "Tableau de bord"),
    ]
    for num, titre in etapes:
        if num < step:
            st.markdown(f'<div class="step-done">✅ {num}. {titre}</div>', unsafe_allow_html=True)
        elif num == step:
            st.markdown(f'<div class="step-active">▶️ {num}. <strong>{titre}</strong></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="step-todo">⬜ {num}. {titre}</div>', unsafe_allow_html=True)

    st.divider()
    st.caption("Besoin d'aide ? hello@invoiceguard.fr")

# ─── ETAPE 1 : Compte ─────────────────────────────────────────────────────────
if step == 1:
    st.subheader("👋 Etape 1 — Dites-nous qui vous etes")
    st.caption("Ces informations personnalisent vos relances et rapports")

    col1, col2 = st.columns(2)
    with col1:
        nom_societe = st.text_input("Nom de votre entreprise *", placeholder="Ma PME SAS",
                                    value=st.session_state.get("nom_societe",""))
        prenom      = st.text_input("Votre prenom *", placeholder="Marie",
                                    value=st.session_state.get("prenom",""))
    with col2:
        email       = st.text_input("Email professionnel *", placeholder="marie@mapme.fr",
                                    value=st.session_state.get("email",""))
        secteur     = st.selectbox("Secteur d'activite", [
            "BTP / Construction",
            "Transport / Logistique",
            "Services B2B",
            "Commerce de gros",
            "IT / Tech",
            "Sante",
            "Industrie",
            "Autre",
        ])

    st.divider()
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        with st.container(border=True):
            st.warning("Cle Gemini requise pour les relances IA")
            api_input = st.text_input("Cle API Gemini (AIzaSy...)", type="password",
                                      help="Obtenez votre cle gratuite sur aistudio.google.com")
            if api_input:
                os.environ["GEMINI_API_KEY"] = api_input
                env_path = os.path.join(os.path.dirname(__file__), ".env")
                with open(env_path, "a", encoding="utf-8") as f:
                    f.write(f"\nGEMINI_API_KEY={api_input}\n")
                st.success("Cle sauvegardee !")
    else:
        st.success("Gemini AI connecte")

    if st.button("Continuer →", type="primary", use_container_width=True,
                 disabled=not (nom_societe and email and prenom)):
        st.session_state.nom_societe = nom_societe
        st.session_state.prenom      = prenom
        st.session_state.email       = email
        st.session_state.secteur     = secteur

        # Enregistre dans SQLite
        try:
            from modules import database as db
            db.upsert_user(email, f"{prenom}", nom_societe, plan="trial")
        except Exception:
            pass

        st.session_state.onboarding_step = 2
        st.rerun()

# ─── ETAPE 2 : Import factures ────────────────────────────────────────────────
elif step == 2:
    st.subheader("📁 Etape 2 — Importez vos factures")

    tab_demo, tab_csv = st.tabs(["📊 Mode demonstration (recommande)", "📁 Importer mon CSV"])

    with tab_demo:
        st.info("12 factures exemples realistes — parfait pour decouvrir l'outil")
        st.markdown("""
**Contenu de la demonstration :**
- 8 factures en retard (15 a 95 jours)
- 4 factures a echeance proche
- Clients issus de secteurs varies (BTP, IT, Immobilier...)
- Montants entre 850€ et 22 000€
        """)
        if st.button("Utiliser les donnees de demonstration", type="primary", use_container_width=True):
            st.session_state.mode_import = "demo"
            st.session_state.onboarding_step = 3
            st.rerun()

    with tab_csv:
        st.markdown("""
**Format CSV accepte :**

| Colonne | Description | Requis |
|---------|------------|--------|
| `client` | Nom du client | ✅ |
| `montant` | Montant TTC en euros | ✅ |
| `date_echeance` | Date echeance (YYYY-MM-DD) | ✅ |
| `email_client` | Email du debiteur | Recommande |
| `numero_facture` | Reference facture | Optionnel |
| `date_emission` | Date emission | Optionnel |
        """)
        uploaded = st.file_uploader("Selectionnez votre fichier CSV", type=["csv"])
        if uploaded:
            try:
                from modules import invoice_scanner
                df = invoice_scanner.load_from_csv(uploaded.read())
                st.success(f"{len(df)} factures importees avec succes !")
                st.dataframe(df[["client","montant","date_echeance","statut"]].head(5),
                             hide_index=True, use_container_width=True)
                st.session_state.df_import = df
                st.session_state.mode_import = "csv"
                if st.button("Continuer avec ces factures →", type="primary", use_container_width=True):
                    st.session_state.onboarding_step = 3
                    st.rerun()
            except Exception as e:
                st.error(f"Erreur import : {e}")

    col_back, _ = st.columns([1, 3])
    with col_back:
        if st.button("← Retour"):
            st.session_state.onboarding_step = 1
            st.rerun()

# ─── ETAPE 3 : Premiere relance ───────────────────────────────────────────────
elif step == 3:
    st.subheader("🤖 Etape 3 — Votre premiere relance IA")
    st.caption("L'IA va generer un email de relance personnalise pour le debiteur le plus urgent")

    from modules import invoice_scanner
    df = invoice_scanner.load_demo_data()

    # Plus urgente
    en_retard = df[df["jours_retard"] > 0].sort_values("score_risque", ascending=False)
    if en_retard.empty:
        st.info("Aucune facture en retard dans les donnees de demo.")
    else:
        cible = en_retard.iloc[0]
        with st.container(border=True):
            st.markdown("**Facture selectionnee automatiquement (score le plus eleve) :**")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Client", cible["client"])
            c2.metric("Montant", f"{cible['montant']:,.0f}EUR")
            c3.metric("Retard", f"{int(cible['jours_retard'])} jours")
            c4.metric("Priorite", cible["priorite"].replace("🔴","").replace("🟠","").replace("🟡","").replace("🟢","").strip())

        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            st.error("Cle Gemini manquante — revenez a l'etape 1")
        else:
            if st.button("Generer la relance IA maintenant", type="primary", use_container_width=True):
                with st.spinner("L'IA redige votre relance... (4 secondes)"):
                    try:
                        from modules import ai_agent
                        result = ai_agent.generer_relance(
                            client_nom    = cible["client"],
                            montant       = float(cible["montant"]),
                            numero_facture= cible.get("numero_facture","INV-001"),
                            date_echeance = str(cible["date_echeance"])[:10],
                            jours_retard  = int(cible["jours_retard"]),
                            ton           = "auto",
                        )
                        st.session_state.demo_relance = result
                        st.session_state.demo_cible   = cible.to_dict()
                    except Exception as e:
                        st.error(f"Erreur : {e}")

            if "demo_relance" in st.session_state:
                r = st.session_state.demo_relance
                st.success("Relance generee en 4 secondes !")
                with st.container(border=True):
                    st.markdown(f"**Objet :** {r.get('sujet','')}")
                    st.divider()
                    st.markdown(r.get("corps",""))
                    st.caption(f"Ton : {r.get('ton_utilise','auto')} | Conforme Loi LME")

                st.markdown("**C'est ca, InvoiceGuard AI.** Chaque email adapte au profil exact du debiteur.")

                if st.button("Excellent ! Acceder au dashboard complet →", type="primary", use_container_width=True):
                    st.session_state.onboarding_step = 4
                    st.rerun()

    col_back, _ = st.columns([1, 3])
    with col_back:
        if st.button("← Retour"):
            st.session_state.onboarding_step = 2
            st.rerun()

# ─── ETAPE 4 : Terminé ────────────────────────────────────────────────────────
elif step == 4:
    st.balloons()

    nom     = st.session_state.get("prenom", "")
    societe = st.session_state.get("nom_societe", "votre entreprise")

    st.markdown(f"## Bravo {nom} !")
    st.success(f"InvoiceGuard AI est pret pour **{societe}**")

    with st.container(border=True):
        st.markdown("### Ce que vous pouvez faire maintenant :")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
**Dans l'app principale :**
- Voir vos KPIs en temps reel
- Lancer une campagne de relances en masse
- Generer un rapport PDF pour votre EC
- Analyser votre portefeuille avec l'IA
            """)
        with col2:
            st.markdown("""
**Pour maximiser le recouvrement :**
- Commencez par les factures a priorite critique
- Parametrez la sequence de relances automatique
- Exportez le rapport PDF pour votre banquier
- Configurez vos vrais emails (Resend API)
            """)

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Ouvrir le dashboard principal", type="primary", use_container_width=True):
            import webbrowser
            webbrowser.open("http://localhost:8502")
    with col_b:
        if st.button("Voir les fonctionnalites Pro", use_container_width=True):
            import webbrowser
            webbrowser.open("http://localhost:8507")

    # Envoie l'email de bienvenue
    email = st.session_state.get("email", "")
    if email and not st.session_state.get("bienvenue_envoye"):
        try:
            from modules.email_bienvenue import envoyer_bienvenue
            envoyer_bienvenue(email, nom, "trial")
            st.session_state.bienvenue_envoye = True
            st.caption("Email de bienvenue envoye !")
        except Exception:
            pass
