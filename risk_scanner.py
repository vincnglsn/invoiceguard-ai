import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

# Chargement de la clé API
load_dotenv("../worldmonitor_test/.env")
api_key = os.environ.get("GEMINI_API_KEY")

st.set_page_config(page_title="Supplier Risk Scanner", page_icon="⚠️", layout="centered")

# Design
st.markdown("""
<style>
    .upsell-box { padding: 25px; background-color: #1e1e1e; border: 2px solid #ff4b4b; border-radius: 10px; text-align: center; margin-top: 30px;}
    .upsell-btn { background-color: #635bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 18px; display: inline-block; margin-top: 15px;}
    .upsell-btn:hover { background-color: #4f46e5; color: white; }
</style>
""", unsafe_allow_html=True)

st.title("⚠️ Supplier Risk Scanner")
st.markdown("### Découvrez à quel point votre Supply Chain est vulnérable.")
st.markdown("Importez la liste de vos fournisseurs actuels. Notre IA va identifier vos risques de dépendance géopolitique et calculer votre **Score de Survie**.")

st.info("💡 Fichier accepté : CSV ou Excel (Colonnes recommandées : Nom du Fournisseur, Pays, Volume d'achat).")

uploaded_file = st.file_uploader("Glissez votre fichier ici", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)
            
        st.dataframe(df, use_container_width=True)
        
        if st.button("🚨 Lancer l'Audit de Fragilité", type="primary"):
            if not api_key or not genai:
                st.error("Erreur : Clé API Gemini manquante.")
            else:
                with st.spinner("Analyse des dépendances géographiques et des risques de rupture..."):
                    client = genai.Client(api_key=api_key)
                    
                    prompt = f"""
                    Agis comme un auditeur de risques Supply Chain impitoyable et alarmiste.
                    Voici la base de fournisseurs d'une entreprise : {df.to_json()}
                    
                    Rédige un audit très court et percutant (format Markdown).
                    1. Donne un 'Score de Survie' sur 100 très bas (ex: 34/100) en grand et en rouge (utilise des emojis).
                    2. Explique en 3 points chocs pourquoi leur chaîne d'approvisionnement est en danger critique de mort (dépendance excessive à un pays, risque de guerre, blocage maritime).
                    3. Ne donne AUCUNE solution. Fais-leur comprendre que si une crise éclate, l'usine ferme.
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(temperature=0.7)
                    )
                    
                    st.divider()
                    st.error("### RÉSULTAT DE L'AUDIT : RISQUE CRITIQUE DÉTECTÉ")
                    st.markdown(response.text)
                    
                    # Le fameux Upsell (Le piège à conversion)
                    st.markdown("""
                    <div class="upsell-box">
                        <h3 style="color: #ff4b4b; margin-top:0;">🛑 Votre Supply Chain ne survivra pas au prochain choc.</h3>
                        <p style="font-size: 16px;">Ne restez pas dans cette situation. Notre Bouclier IA analyse le marché mondial et vous génère instantanément un plan de secours avec des fournisseurs alternatifs locaux.</p>
                        <a href="https://buy.stripe.com/8x2aEX6AU1Dt8Qldh387K00" target="_blank" class="upsell-btn">🛡️ Sécuriser ma Supply Chain maintenant (49€)</a>
                    </div>
                    """, unsafe_allow_html=True)
                    
    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
