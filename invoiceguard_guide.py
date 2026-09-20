"""
InvoiceGuard AI — Générateur de Guide Lead Magnet
Génère un guide PDF de 28 pages "Le Guide du Recouvrement pour PME françaises"
via Gemini + fpdf2. À télécharger depuis la landing page.
"""

import streamlit as st
import os, sys
from dotenv import load_dotenv

load_dotenv()
if not os.environ.get("GEMINI_API_KEY"):
    load_dotenv("../.env")

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="Guide Recouvrement PME — InvoiceGuard",
    page_icon="📘",
    layout="centered",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0A0F1E; }
</style>
""", unsafe_allow_html=True)

st.title("📘 Guide Gratuit — Recouvrement PME")
st.caption("Généré personnalisé par l'IA selon votre secteur d'activité")
st.divider()

col1, col2 = st.columns(2)
with col1:
    prenom = st.text_input("Votre prénom", placeholder="Marie")
    societe = st.text_input("Votre entreprise", placeholder="Ma PME SAS")
with col2:
    email = st.text_input("Email (pour recevoir le guide)", placeholder="marie@mapme.fr")
    secteur = st.selectbox("Votre secteur", [
        "BTP / Construction",
        "Transport / Logistique",
        "Prestation de services B2B",
        "Commerce de gros",
        "IT / Tech / SaaS",
        "Santé / Paramédical",
        "Industrie / Fabrication",
        "Autre",
    ])

ca_annuel = st.number_input("Chiffre d'affaires annuel (€)", min_value=0, value=500000, step=50000,
                              format="%d", help="Permet de personnaliser les exemples et les montants")

st.divider()

if st.button("📥 Générer mon guide personnalisé", type="primary", use_container_width=True):
    if not email:
        st.error("Entrez votre email")
        st.stop()

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error("Clé API Gemini manquante")
        st.stop()

    # Sauvegarde le lead
    try:
        from modules import database as db
        db.save_lead(email, prenom, societe, "", ca_annuel, "guide_magnet")
    except Exception:
        pass

    with st.spinner("🧠 L'IA génère votre guide personnalisé (30 secondes)..."):
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)

            prompt = f"""Tu es un expert en recouvrement de créances pour PME françaises.

Génère un guide complet et ultra-pratique intitulé "Le Guide du Recouvrement {secteur} 2026"
personnalisé pour {prenom} de {societe} (CA: {ca_annuel:,}€).

Le guide doit contenir ces sections :

1. INTRODUCTION : Pourquoi le recouvrement est vital pour une PME {secteur} (2 paragraphes)

2. LES CHIFFRES QUI FONT PEUR : Statistiques impayés France + spécifiques au secteur {secteur}

3. LA LOI LME EXPLIQUÉE SIMPLEMENT : 
   - Délais légaux (60j date facture / 45j fin de mois)
   - Pénalités de retard (BCE + 10 pts = ~13% actuellement)
   - Indemnité forfaitaire de recouvrement de 40€
   - Comment les calculer sur une facture de 10 000€ à 60j de retard

4. LE PROCESSUS EN 4 ÉTAPES :
   - J+1 : Vérification réception facture
   - J+15 : 1ère relance douce (email modèle inclus)
   - J+30 : 2ème relance ferme (email modèle inclus)
   - J+60 : Mise en demeure (email modèle inclus)
   - J+90 : Procédures judiciaires (injonction de payer)

5. 5 ERREURS À ÉVITER ABSOLUMENT dans le secteur {secteur}

6. MODÈLES D'EMAILS PRÊTS À L'EMPLOI (3 emails adaptés au secteur {secteur}) :
   - Email 1 : Relance amiable
   - Email 2 : Relance ferme avec pénalités
   - Email 3 : Mise en demeure

7. COMMENT RÉDUIRE VOS IMPAYÉS À L'AVENIR :
   - Clause de réserve de propriété
   - Acomptes et jalons
   - Vérification solvabilité
   - Conditions générales de vente

8. OUTILS ET RESSOURCES : Sites utiles, tribunaux de commerce, médiateurs

9. CONCLUSION : Récapitulatif + appel à l'action (tester InvoiceGuard AI)

Format : texte propre, sans markdown, paragraphes clairs, exemples chiffrés avec des montants réalistes.
Longueur : environ 2000 mots, très pratique et actionnable."""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.3),
            )
            contenu_guide = response.text

            # Génération PDF
            try:
                from fpdf import FPDF

                class GuidePDF(FPDF):
                    def header(self):
                        self.set_fill_color(0, 212, 170)
                        self.rect(0, 0, 210, 18, "F")
                        self.set_text_color(0, 0, 0)
                        self.set_font("Helvetica", "B", 12)
                        self.set_xy(10, 4)
                        self.cell(0, 10, f"Guide du Recouvrement {secteur} 2026 — InvoiceGuard AI", align="L")
                        self.ln(20)

                    def footer(self):
                        self.set_y(-15)
                        self.set_text_color(150, 150, 150)
                        self.set_font("Helvetica", "I", 8)
                        self.cell(0, 10, f"InvoiceGuard AI · invoiceguard.fr · Page {self.page_no()} · Offert gratuitement", align="C")

                pdf = GuidePDF()
                pdf.set_auto_page_break(auto=True, margin=20)
                pdf.add_page()

                # Page de garde
                pdf.set_fill_color(17, 24, 39)
                pdf.rect(0, 18, 210, 60, "F")
                pdf.set_text_color(0, 212, 170)
                pdf.set_font("Helvetica", "B", 22)
                pdf.set_xy(10, 25)
                pdf.multi_cell(190, 12, f"Le Guide du Recouvrement\n{secteur} 2026", align="C")
                pdf.set_text_color(200, 200, 200)
                pdf.set_font("Helvetica", "", 11)
                pdf.set_xy(10, 65)
                pdf.cell(0, 8, f"Guide personnalise pour {prenom} · {societe}", align="C")
                pdf.ln(30)

                # Contenu
                pdf.set_text_color(30, 30, 30)
                pdf.set_font("Helvetica", "", 10)
                safe = contenu_guide.encode("latin-1", errors="replace").decode("latin-1")
                pdf.multi_cell(0, 5.5, safe)

                # Page finale
                pdf.add_page()
                pdf.set_fill_color(0, 212, 170)
                pdf.rect(10, 20, 190, 80, "F")
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", "B", 16)
                pdf.set_xy(10, 35)
                pdf.multi_cell(190, 10, "Essayez InvoiceGuard AI GRATUITEMENT\n14 jours sans carte bancaire", align="C")
                pdf.set_font("Helvetica", "", 11)
                pdf.set_xy(10, 75)
                pdf.multi_cell(190, 7, "Recuperez automatiquement vos impayes avec l'IA\nConforme Loi LME · RGPD · Made in France", align="C")

                pdf_bytes = bytes(pdf.output())

                st.success("✅ Guide prêt !")
                st.download_button(
                    label=f"📥 Télécharger votre guide personnalisé ({secteur})",
                    data=pdf_bytes,
                    file_name=f"guide_recouvrement_{secteur.lower().replace('/','-').replace(' ','_')}_2026.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                )

                st.divider()
                st.markdown("### 📖 Aperçu du guide")
                with st.expander("Lire le guide en ligne"):
                    st.markdown(contenu_guide)

            except ImportError:
                st.warning("fpdf2 non disponible — affichage en texte")
                st.markdown(contenu_guide)

        except Exception as e:
            st.error(f"Erreur génération : {e}")

st.divider()
st.markdown("""
<div style='text-align:center;color:#6B7280;font-size:.85rem'>
🛡️ <strong>InvoiceGuard AI</strong> · 
<a href='http://localhost:8502' style='color:#00D4AA'>Essai gratuit 14 jours</a> · 
<a href='mailto:hello@invoiceguard.fr' style='color:#00D4AA'>Contact</a>
</div>
""", unsafe_allow_html=True)
