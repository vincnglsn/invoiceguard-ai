"""
InvoiceGuard AI — Planificateur LinkedIn & Contenu Marketing
Affiche les posts LinkedIn avec le timing optimal et génère
du contenu frais via Gemini si besoin.
"""

import streamlit as st
import os, sys
from datetime import date, datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(page_title="Planificateur Marketing — InvoiceGuard", page_icon="📅", layout="wide")

st.markdown("<style>[data-testid='stAppViewContainer']{background:#0A0F1E}</style>", unsafe_allow_html=True)
st.title("📅 Planificateur Marketing — InvoiceGuard AI")
st.caption("Posts LinkedIn · Cold emails · Product Hunt · Timing optimal")
st.divider()

# ─── Calendrier de publication ────────────────────────────────────────────────

aujourd_hui = date.today()
lundi_prochain = aujourd_hui + timedelta(days=(7 - aujourd_hui.weekday()) % 7 or 7)

CALENDRIER = [
    {
        "date":    lundi_prochain,
        "heure":   "08h00",
        "canal":   "LinkedIn",
        "type":    "Post n°1 — Choc",
        "priorite":"🔴 URGENT",
        "sujet":   "Angle : la perte silencieuse d'argent",
        "contenu": """🔴 12 milliards d'euros.

C'est ce que les PME françaises perdent CHAQUE ANNÉE en factures impayées.

Pas à cause de clients malhonnêtes.
À cause d'un processus de relance trop lent, trop mou, pas conforme à la loi.

Voici ce qui se passe réellement :
→ Facture envoyée à 90 jours : taux de recouvrement 35%
→ Facture relancée à 30 jours : taux de recouvrement 85%
→ Différence : 50% de votre CA en jeu

J'ai construit InvoiceGuard AI pour résoudre ça.

L'IA analyse chaque débiteur, choisit le bon ton, génère la relance parfaite en 4 secondes — conforme Loi LME, avec les pénalités de retard calculées automatiquement.

Essai gratuit 14 jours : [lien dans les commentaires]

#PME #Trésorerie #Recouvrement #FacturationElectronique #IA""",
    },
    {
        "date":    lundi_prochain + timedelta(days=2),
        "heure":   "07h30",
        "canal":   "LinkedIn",
        "type":    "Post n°2 — Social proof",
        "priorite":"🟠 Cette semaine",
        "sujet":   "Angle : résultat concret + chiffre",
        "contenu": """💰 Récapitulatif de la semaine pour un de nos utilisateurs beta :

Factures en retard au lundi : 47 500€
Relances envoyées par InvoiceGuard AI : 12 emails
Paiements reçus au vendredi : 31 200€

En 5 jours. Sans appeler personne. Sans stress.

Comment ?

L'outil a analysé chaque débiteur :
• Groupe Immobilier → 22 000€ → Mise en demeure (95j retard)
• TechSolutions SAS → 12 800€ → Relance ferme (38j retard)
• Cabinet Leblanc → 6 200€ → Relance urgente (67j retard)

Chaque email adapté au profil, à l'ancienneté, au montant.
Conformité Loi LME automatique. Pénalités mentionnées.

Ça marche.

14 jours gratuits → [lien dans les commentaires]

#Trésorerie #PME #IA #Recouvrement #Innovation""",
    },
    {
        "date":    lundi_prochain + timedelta(days=4),
        "heure":   "12h00",
        "canal":   "LinkedIn",
        "type":    "Post n°3 — EC partenaire",
        "priorite":"🟠 Cette semaine",
        "sujet":   "Angle : cibler les experts-comptables",
        "contenu": """📊 Aux experts-comptables qui lisent ceci :

Vos clients PME ont en moyenne 4,2% de leur CA en impayés.
Sur un client à 2M€ de CA, c'est 84 000€ qui dorment.

Vous pouvez changer ça — et être rémunérés pour le faire.

InvoiceGuard AI, c'est :
✅ Un outil IA de recouvrement conforme Loi LME
✅ Un rapport mensuel intégrable à votre reporting
✅ Un programme partenaire EC avec 20% de commission récurrente

→ 10 clients PME abonnés = 298€/mois passifs pour votre cabinet

Je cherche 5 cabinets pilotes pour lancer le programme.
Formation offerte + co-branding possible.

Message privé ou lien dans les commentaires.

#ExpertComptable #EC #PME #Innovation #IA #Partenariat""",
    },
    {
        "date":    lundi_prochain + timedelta(days=7),
        "heure":   "08h00",
        "canal":   "Cold Email PME",
        "type":    "Campagne PME — 20 emails",
        "priorite":"🟡 Semaine 2",
        "sujet":   "Secteurs : BTP, Transport, IT",
        "contenu": "Lancer : python campagne_emails_auto.py --template pme --max 20 --demo",
    },
    {
        "date":    lundi_prochain + timedelta(days=7),
        "heure":   "09h00",
        "canal":   "Cold Email EC",
        "type":    "Campagne EC — 10 emails",
        "priorite":"🟡 Semaine 2",
        "sujet":   "Experts-comptables locaux",
        "contenu": "Lancer : python campagne_emails_auto.py --template ec --max 10 --demo",
    },
    {
        "date":    lundi_prochain + timedelta(days=7),
        "heure":   "18h00",
        "canal":   "Product Hunt",
        "type":    "Lancement PH",
        "priorite":"🟡 Semaine 2",
        "sujet":   "Publier le dimanche soir 23h59 PST",
        "contenu": """TITLE: InvoiceGuard AI

TAGLINE: Recover unpaid invoices automatically with AI — French LME law compliant

TOPICS: Artificial Intelligence, Finance, SaaS, Small Business

DESCRIPTION:
InvoiceGuard AI uses Gemini 2.5 Flash to generate the perfect collection email for each debtor — right tone, right urgency, with automatic French LME law penalties (13% annual rate + €40 flat fee).

Results: -40% DSO in 60 days for our beta users.

FIRST COMMENT:
Hey PH! 👋

I built this after watching my PME clients struggle with unpaid invoices. They'd spend 4 hours/week on manual follow-ups — wrong tone, too late, no legal references.

InvoiceGuard AI solves this: upload your invoices CSV, the AI scores each debtor (0-100 risk), generates a personalized email in 4 seconds, and tracks everything.

Free for 14 days. No credit card. 🇫🇷""",
    },
]

# ─── Affichage ────────────────────────────────────────────────────────────────

tab_cal, tab_gen, tab_ph = st.tabs(["📅 Calendrier", "✍️ Générer contenu IA", "🚀 Product Hunt"])

with tab_cal:
    st.subheader("Plan de publication — 14 prochains jours")

    for item in CALENDRIER:
        jours_restants = (item["date"] - aujourd_hui).days
        delta_txt = "Aujourd'hui !" if jours_restants == 0 else (
            "Demain" if jours_restants == 1 else f"Dans {jours_restants} jours"
        )

        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            with c1:
                st.markdown(f"**{item['canal']}** · {item['type']}")
                st.caption(item["sujet"])
            with c2:
                st.markdown(f"📅 {item['date'].strftime('%d/%m')} · {item['heure']}")
                st.caption(delta_txt)
            with c3:
                st.markdown(item["priorite"])

            with st.expander("📋 Voir / copier le contenu"):
                st.code(item["contenu"], language=None)

with tab_gen:
    st.subheader("Générer un nouveau post LinkedIn avec l'IA")
    st.caption("Gemini 2.5 Flash génère un post optimisé en fonction de votre brief")

    angle = st.selectbox("Angle du post", [
        "Chiffre choc / statistique surprenante",
        "Histoire client (avant/après)",
        "Conseil pratique (valeur éducative)",
        "Controverse / opinion forte",
        "Transparence fondateur (behind the scenes)",
        "Résultat concret avec chiffres",
    ])
    audience = st.radio("Audience cible", ["PME / Dirigeants", "Experts-Comptables", "DAF / CFO"], horizontal=True)
    ton = st.radio("Ton", ["Autoritaire et direct", "Bienveillant et pédagogue", "Humoristique et décalé"], horizontal=True)

    if st.button("✨ Générer le post", type="primary"):
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            st.error("Clé API Gemini manquante")
        else:
            with st.spinner("Génération en cours..."):
                try:
                    from google import genai
                    from google.genai import types

                    prompt = f"""Tu es un expert en personal branding LinkedIn pour les fondateurs de startups SaaS françaises.

Génère un post LinkedIn viral pour InvoiceGuard AI.

Paramètres :
- Angle : {angle}
- Audience : {audience}
- Ton : {ton}
- Produit : InvoiceGuard AI — outil IA de recouvrement d'impayés pour PME françaises
- Problème résolu : Les PME perdent 12Mrd€/an en impayés, passent 4h/sem à relancer manuellement

Instructions :
- 150-300 mots maximum
- Structure : accroche choc (1-2 lignes) + développement (listes ou courts paragraphes) + CTA clair
- 4-6 hashtags pertinents
- Pas de jargon trop technique
- Inclure 1 chiffre marquant
- Terminer par "[Lien dans les commentaires]"

Génère UNIQUEMENT le post, sans commentaires ni explication."""

                    client = genai.Client(api_key=api_key)
                    resp = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                        config=types.GenerateContentConfig(temperature=0.7),
                    )
                    st.success("✅ Post généré !")
                    st.code(resp.text, language=None)
                    st.info("💡 Meilleur moment pour publier : Lundi/Mercredi/Vendredi · 7h30-9h ou 12h-13h")
                except Exception as e:
                    st.error(f"Erreur : {e}")

with tab_ph:
    st.subheader("🚀 Fiche Product Hunt")
    st.caption("Publiez le dimanche soir avant minuit (heure de San Francisco) pour être visible dès lundi matin français")

    ph = CALENDRIER[-1]
    st.code(ph["contenu"], language=None)

    st.divider()
    st.markdown("### 📋 Checklist avant lancement PH")
    checks = [
        "Créer un compte Product Hunt et obtenir +50 followers avant le lancement",
        "Préparer 5-10 screenshots de l'app (dashboard, relance IA, rapport PDF)",
        "Filmer une vidéo démo de 90 secondes (screen recording)",
        "Contacter 20 amis/contacts pour upvoter le jour J",
        "Préparer la réponse aux commentaires en français ET anglais",
        "Lancer le dimanche entre 23h00 et 23h59 heure SF (08h-09h lundi matin Paris)",
    ]
    for c in checks:
        st.checkbox(c)
