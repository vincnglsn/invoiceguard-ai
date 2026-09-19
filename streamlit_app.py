"""
InvoiceGuard AI — Point d'entrée Streamlit Cloud
Redirige vers l'app principale (requis pour Streamlit Community Cloud).
"""
# Ce fichier s'appelle streamlit_app.py (nom canonique pour Streamlit Cloud).
# Il importe et exécute l'app principale.

import sys
import os

# S'assure que les modules locaux sont trouvables
sys.path.insert(0, os.path.dirname(__file__))

# Utilise st.secrets si déployé sur Streamlit Cloud
import streamlit as st

# Inject GEMINI_API_KEY depuis st.secrets si disponible (Streamlit Cloud)
if "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
if "RESEND_API_KEY" in st.secrets:
    os.environ["RESEND_API_KEY"] = st.secrets["RESEND_API_KEY"]

# Lance l'app principale
exec(open(os.path.join(os.path.dirname(__file__), "invoiceguard_app.py")).read())
