"""
InvoiceGuard AI — Prospecteur Automatique
Utilise l'app demo existante pour prospecter des clients pour InvoiceGuard.
Génère des cold emails ultra-personnalisés pour vendre InvoiceGuard aux PME françaises.
"""

import streamlit as st
import os
import sys
import urllib.request
import re
from html.parser import HTMLParser
from dotenv import load_dotenv

load_dotenv()
if not os.environ.get("GEMINI_API_KEY"):
    load_dotenv("../.env")
    load_dotenv("../worldmonitor_test/.env")

try:
    from google import genai
    from google.genai import types
    GENAI_OK = True
except ImportError:
    GENAI_OK = False

api_key = os.environ.get("GEMINI_API_KEY")

# ─── Utilitaires ──────────────────────────────────────────────────────────────
class HTMLFilter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = ""
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ["script", "style", "noscript"]:
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ["script", "style", "noscript"]:
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            self.text += data + " "


def aspirer_site(url: str) -> str:
    try:
        if not url.startswith("http"):
            url = "https://" + url
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=8).read().decode("utf-8", errors="ignore")
        f = HTMLFilter()
        f.feed(html)
        return re.sub(r"\s+", " ", f.text).strip()[:8000]
    except Exception as e:
        return f"Erreur aspiration : {e}"


# ─── Interface ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InvoiceGuard — Prospecteur",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 Prospecteur InvoiceGuard AI")
st.caption("Générez des cold emails ultra-personnalisés pour vendre InvoiceGuard à vos prospects PME")
st.divider()

TEMPLATES_SUJET = [
    "Vos {X}€ d'impayés peuvent être récupérés automatiquement",
    "{Client}, avez-vous déjà calculé votre coût des impayés ?",
    "La facturation électronique vous a changé votre process de relance ?",
    "10 min pour vous montrer comment récupérer vos impayés automatiquement",
]

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### ⚙️ Paramètres")

    prospect_nom = st.text_input("Nom de l'entreprise cible", placeholder="Ex: BTP Martin SARL")
    prospect_url = st.text_input("Site web du prospect", placeholder="https://btp-martin.fr")
    secteur = st.selectbox("Secteur d'activité", [
        "BTP / Construction", "Prestation de services B2B", "Cabinet conseil / Consulting",
        "Transport / Logistique", "Industrie / Fabrication", "Commerce de gros",
        "Immobilier", "Santé / Médical", "Autre",
    ])
    nb_salaries = st.selectbox("Taille estimée", [
        "1-10 salariés (TPE)", "11-50 salariés (PME)", "51-200 salariés (ETI)",
    ])
    montant_estime = st.number_input(
        "Montant d'impayés estimé (€)", min_value=0, value=15000, step=1000,
        help="Estimation basée sur : CA moyen x 4% = impayés moyen",
    )

    angle = st.selectbox("Angle d'attaque", [
        "Douleur impayés (générique)",
        "Urgence facturation électronique (sept. 2026)",
        "Gain de temps (stop aux relances manuelles)",
        "ROI / rentabilité (chiffré)",
        "Conformité légale LME",
    ])

    with st.expander("🔮 Aspirer le site web automatiquement"):
        if st.button("Aspirer le site", disabled=not prospect_url):
            with st.spinner("Aspiration..."):
                st.session_state.site_content = aspirer_site(prospect_url)
                st.success(f"✅ {len(st.session_state.get('site_content',''))} caractères récupérés")

    site_data = st.session_state.get("site_content", "")
    if site_data:
        st.caption(f"📄 Contexte site : {len(site_data)} caractères")

with col2:
    st.markdown("### 📧 Génération du message")

    canal_out = st.segmented_control(
        "Format de sortie",
        ["Cold Email", "Message LinkedIn", "Script Appel"],
        default="Cold Email",
    )

    if not api_key or not GENAI_OK:
        st.error("⚠️ Clé API Gemini manquante.")
    else:
        if st.button(":material/auto_awesome: Générer le message", type="primary", use_container_width=True):
            site_ctx = site_data[:3000] if site_data else f"Entreprise du secteur {secteur}, {nb_salaries}."

            angle_prompts = {
                "Douleur impayés (générique)":
                    "Met en avant le problème universel des impayés en PME (12 milliards en France) et propose une solution immédiate.",
                "Urgence facturation électronique (sept. 2026)":
                    "Exploite le fait que la facturation électronique est devenue obligatoire en septembre 2026. Leur process de recouvrement est-il à jour ? C'est le moment parfait pour automatiser.",
                "Gain de temps (stop aux relances manuelles)":
                    "Met en avant le temps perdu chaque semaine à faire des relances manuelles. InvoiceGuard le fait automatiquement.",
                "ROI / rentabilité (chiffré)":
                    f"Chiffre précisément le ROI : si l'entreprise a {montant_estime:,.0f}€ d'impayés, récupérer 72% = {montant_estime*0.72:,.0f}€ · Abonnement 149€/mois = ROI de {(montant_estime*0.72/149):.0f}x en 1 mois.",
                "Conformité légale LME":
                    "Rappelle les obligations légales (LME, pénalités automatiques, indemnité 40€) et propose de les activer automatiquement.",
            }

            angle_instr = angle_prompts.get(angle, angle_prompts["Douleur impayés (générique)"])

            if canal_out == "Cold Email":
                format_instr = """Rédige un cold email en français avec :
- Objet accrocheur (max 50 caractères)
- Corps en 4 parties : accroche personnalisée, problème, solution InvoiceGuard, CTA
- Maximum 150 mots dans le corps
- CTA : proposer un RDV de 10 min ou une démo gratuite
Format : OBJET: [objet]\n---\n[corps]"""
            elif canal_out == "Message LinkedIn":
                format_instr = """Rédige un message de connexion LinkedIn en français :
- Maximum 300 caractères (limite LinkedIn)
- Accroche personnalisée en 1 phrase
- Valeur proposée claire
- CTA simple
Format : [message direct, sans formule de politesse lourde]"""
            else:
                format_instr = """Rédige un script d'appel téléphonique court en français :
- Accroche (5 secondes) : phrase qui évite le raccrochage
- Qualification (30 secondes) : 2 questions pour confirmer la douleur
- Pitch (30 secondes) : valeur InvoiceGuard en 3 points
- CTA : proposer une démo de 10 min
Format structuré avec les temps et les répliques type"""

            prompt = f"""Tu es un expert en vente SaaS B2B et copywriting.

PRODUIT À VENDRE : InvoiceGuard AI
- Solution de recouvrement automatique d'impayés pour PME françaises
- L'IA analyse les factures, détecte les retards, envoie des relances personnalisées
- Conforme Loi LME et RGPD · Hébergé en France
- Tarif : 49-149€/mois · Essai gratuit 14 jours

PROSPECT :
- Entreprise : {prospect_nom or 'PME française'}
- Secteur : {secteur}
- Taille : {nb_salaries}
- Contexte site web : {site_ctx}

ANGLE D'ATTAQUE : {angle_instr}

INSTRUCTION DE FORMAT : {format_instr}

Génère un message impactant, ultra-personnalisé, qui ne ressemble pas à un email générique."""

            with st.spinner("✍️ Rédaction en cours..."):
                try:
                    client_g = genai.Client(api_key=api_key)
                    resp = client_g.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt,
                        config=types.GenerateContentConfig(temperature=0.65),
                    )
                    st.session_state.prospect_msg = resp.text.strip()
                    st.session_state.prospect_canal = canal_out
                except Exception as e:
                    st.error(f"Erreur : {e}")

        if "prospect_msg" in st.session_state:
            st.divider()
            raw = st.session_state.prospect_msg
            canal_used = st.session_state.get("prospect_canal", "")

            if canal_used == "Cold Email" and "OBJET:" in raw:
                parts = raw.split("---", 1)
                objet = parts[0].replace("OBJET:", "").strip()
                corps = parts[1].strip() if len(parts) > 1 else raw
                st.markdown(f"**📧 Objet :** `{objet}`")
                msg_edited = st.text_area("Corps du message", corps, height=300,
                                          label_visibility="collapsed")
            else:
                msg_edited = st.text_area("Message généré", raw, height=300,
                                          label_visibility="collapsed")

            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    ":material/download: Télécharger",
                    msg_edited.encode("utf-8"),
                    f"prospection_{prospect_nom or 'prospect'}.txt",
                )
            with col_dl2:
                st.info("💡 Copiez et envoyez directement")

# ─── Guide prospection ─────────────────────────────────────────────────────────
st.divider()
with st.expander("📖 Guide : Comment prospecter InvoiceGuard efficacement ?"):
    st.markdown("""
### 🎯 Cibles prioritaires (les plus convertissantes)

| Profil | Pourquoi | Comment les trouver |
|--------|----------|---------------------|
| **Gérant de PME BTP** | Toujours des impayés clients | LinkedIn · Groupes bâtiment |
| **DAF / Directeur Financier** | Souffre du DSO · Cherche des outils | LinkedIn · Événements finance |
| **Expert-comptable** | Peut recommander à 200+ clients | Via ordre des EC · LinkedIn |
| **Consultant indépendant** | Factures souvent en retard | Communautés freelance |

### 🔑 Arguments qui convertissent

1. **"12 milliards d'euros d'impayés en France"** → contextualise l'ampleur
2. **"Facturation électronique obligatoire → bon moment pour revoir le process"** → urgence réglementaire
3. **"ROI calculé : 1 facture récupérée = 6 mois d'abonnement"** → argument chiffré irrésistible
4. **"Essai gratuit 14 jours, sans carte bancaire"** → zéro risque pour eux

### 📅 Séquence de suivi recommandée

- **Jour 0** : Email/LinkedIn initial (généré ici)
- **Jour 3** : Follow-up si pas de réponse (ton légèrement différent)
- **Jour 7** : Dernier contact avec contenu de valeur (ex: "Saviez-vous que...")
- **Jour 14** : Breakup email (clôture la séquence)
    """)
