import streamlit as st
import os
import urllib.request
import re
from html.parser import HTMLParser
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

class HTMLFilter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = ""
        self.in_script_or_style = False

    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style', 'noscript']:
            self.in_script_or_style = True

    def handle_endtag(self, tag):
        if tag in ['script', 'style', 'noscript']:
            self.in_script_or_style = False

    def handle_data(self, data):
        if not self.in_script_or_style:
            self.text += data + " "

def aspirer_site(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8', errors='ignore')
        f = HTMLFilter()
        f.feed(html)
        clean_text = re.sub(r'\s+', ' ', f.text)
        return clean_text.strip()[:10000]
    except Exception as e:
        return f"Erreur lors de l'aspiration : {e}"

load_dotenv("../worldmonitor_test/.env")
api_key = os.environ.get("GEMINI_API_KEY")

st.set_page_config(page_title="Nexus AI - Agence", page_icon="🚀", layout="wide")

st.title("🚀 Nexus AI : Le Système B2B Complet")
st.markdown("Gérez toute votre acquisition client depuis cette interface centralisée.")
st.divider()

if "context_data" not in st.session_state:
    st.session_state.context_data = ""

tab1, tab2 = st.tabs(["💼 1. Démonstrateur Client (L'Appât)", "🎯 2. Studio de Prospection (L'Email Parfait)"])

with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.header("⚙️ Le Cerveau")
        company_name = st.text_input("Nom de l'entreprise prospectée", value="Mon Prospect")
        
        st.markdown("### 🪄 Aspirateur Magique")
        url_cible = st.text_input("URL du site web prospect (ex: https://...)")
        
        if st.button("Aspirer le site", type="primary"):
            with st.spinner("Aspiration en cours..."):
                st.session_state.context_data = aspirer_site(url_cible)
                st.rerun()
        
        st.markdown("**Contexte Ingéré :**")
        company_context = st.text_area("Base de connaissances brute", value=st.session_state.context_data, height=300)
        st.session_state.context_data = company_context

    with col2:
        st.header("🤖 L'Assistant (Test)")
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input(f"Posez une question à {company_name}..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                if not api_key or not genai:
                    st.error("Erreur : Clé API manquante.")
                else:
                    try:
                        client = genai.Client(api_key=api_key)
                        system_prompt = f"Tu es l'assistant virtuel de {company_name}. Utilise STRICTEMENT ce contexte : {company_context}."
                        contents = []
                        for m in st.session_state.messages[:-1]:
                            role = 'user' if m['role'] == 'user' else 'model'
                            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m['content'])]))
                        contents.append(types.Content(role='user', parts=[types.Part.from_text(text=prompt)]))
                        
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=contents,
                            config=types.GenerateContentConfig(system_instruction=system_prompt, temperature=0.2)
                        )
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"Erreur : {e}")

with tab2:
    st.header("🎯 Générateur d'Approche Ultra-Personnalisée")
    st.markdown("Utilisez l'IA pour lire le site web aspiré et rédiger automatiquement l'email de prospection parfait pour CE client spécifique. Fini les emails génériques.")
    
    if st.button("🧠 Rédiger mon Email de Prospection", type="primary"):
        if not api_key or not genai:
            st.error("Erreur : Clé API manquante.")
        elif len(st.session_state.context_data) < 50:
            st.warning("⚠️ Aspirez d'abord le site web d'un prospect dans l'onglet 1 (Démonstrateur).")
        else:
            with st.spinner("Analyse du site et rédaction de l'approche commerciale..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt_email = f"""Tu es un copywriter d'élite spécialisé dans le Cold Email B2B.
                    Lis les données extraites du site web de ce prospect : 
                    {st.session_state.context_data[:5000]}
                    
                    Rédige un email de prospection court, percutant et ultra-personnalisé.
                    L'objectif : Vendre un Chatbot IA sur mesure pour leur site web.
                    
                    Règles impératives :
                    1. Mentionne obligatoirement un service précis, un détail ou une information clé de leur site pour prouver que ce n'est pas un email générique.
                    2. Met en avant la réduction du temps de réponse ou l'augmentation des conversions 24/7.
                    3. Propose un appel à l'action simple (un RDV de 10 min ou de regarder une courte vidéo).
                    4. Ton professionnel mais très direct et moderne. Pas de formules de politesse lourdes (pas de "je vous prie d'agréer").
                    """
                    
                    resp_email = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt_email,
                        config=types.GenerateContentConfig(temperature=0.7)
                    )
                    
                    st.success("✅ Email généré sur mesure !")
                    st.text_area("Copiez ce message (Email / LinkedIn) :", value=resp_email.text, height=400)
                except Exception as e:
                    st.error(f"Erreur lors de la génération : {e}")
