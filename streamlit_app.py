"""
InvoiceGuard AI -- Point d'entree Streamlit Cloud.

Declare l'application multipage : c'est ce fichier que Streamlit Cloud execute
(nom canonique). Chaque page reste un script autonome, lancable seul en local
via `streamlit run <script>.py`.

Les outils internes (dashboard fondateur, prospecteur, espace partenaire) ne
sont volontairement PAS declares ici : ils restent accessibles uniquement en
local, car le depot est public.
"""

import os
import sys

# S'assure que les modules locaux sont trouvables depuis n'importe quelle page
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

# ─── Secrets Streamlit Cloud -> variables d'environnement ────────────────────
for _cle in ("GEMINI_API_KEY", "RESEND_API_KEY", "FOUNDER_PASSWORD"):
    try:
        if _cle in st.secrets:
            os.environ[_cle] = str(st.secrets[_cle])
    except Exception:
        # Pas de fichier secrets.toml en local : on se rabat sur .env
        break

# ─── Configuration globale ───────────────────────────────────────────────────
st.set_page_config(
    page_title="InvoiceGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Pages publiques ─────────────────────────────────────────────────────────
PAGES = [
    st.Page("invoiceguard_app.py", title="Application", icon="🛡️", default=True),
    st.Page("invoiceguard_onboarding.py", title="Démarrage guidé", icon="🚀"),
    st.Page("invoiceguard_pricing.py", title="Tarifs", icon="💳"),
    st.Page("invoiceguard_guide.py", title="Guide gratuit", icon="📘"),
    st.Page("invoiceguard_legal.py", title="Mentions légales", icon="⚖️"),
]

st.navigation(PAGES).run()
