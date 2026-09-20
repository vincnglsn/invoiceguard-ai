# 🛡️ InvoiceGuard AI

> **Récupérez automatiquement vos factures impayées grâce à l'IA**  
> SaaS B2B pour PME françaises · Conforme Loi LME & RGPD · Made in France 🇫🇷

---

## 📊 Démo

Aucune démo hébergée pour le moment — le déploiement public est en cours de
configuration. En attendant, l'application se lance en local en 5 minutes
(voir la section **Installation locale** ci-dessous).

---

## 💡 Le problème

**12 milliards d’euros** d’impayés circulent en permanence dans les PME françaises.  
Les dirigeants perdent 3-4h/semaine en relances manuelles — trop tard, mauvais ton, sans pénalités légales.

Avec InvoiceGuard AI :
- L’IA analyse chaque débiteur et choisit le bon ton automatiquement
- Les relances sont générées en 4 secondes, conformes Loi LME
- Le DSO moyen baisse de **-40%** en 60 jours

---

## ✨ Fonctionnalités

| Onglet | Ce que vous pouvez faire |
|--------|-------------------------|
| 📊 **Dashboard** | KPIs en temps réel · 4 graphiques interactifs · Alertes critiques |
| 📋 **Factures** | Filtres multi-critères · Score de risque (0-100) · Export CSV |
| 🤖 **Relance IA** | Email ou SMS personnalisé · 5 tons adaptés · Mentions LME auto |
| 🚀 **Campagne** | Relances groupées · 3 séquences · Estimation recouvrement |
| 🧠 **Analyse IA** | Diagnostic complet · Chat assistant trésorerie |
| 📄 **Rapport PDF** | Rapport professionnel pour expert-comptable / DAF |

---

## 🛠️ Installation locale (5 minutes)

```bash
git clone https://github.com/vincnglsn/invoiceguard-ai
cd invoiceguard-ai
pip install -r requirements.txt
echo GEMINI_API_KEY=votre_cle_gemini > .env
streamlit run invoiceguard_app.py
```

> Obtenez votre clé Gemini gratuite sur [aistudio.google.com](https://aistudio.google.com)

---

## ☁️ Déploiement Streamlit Cloud (gratuit, 3 min)

1. **Forkez** ce repository
2. Allez sur **[share.streamlit.io](https://share.streamlit.io)**
3. → Create app → sélectionnez votre fork
4. Main file : `streamlit_app.py`
5. Advanced settings → Secrets :
   ```toml
   GEMINI_API_KEY = "votre_cle_gemini"
   ```
6. **Deploy !** → URL publique en 3 minutes

---

## 💰 Pricing

| Plan | Prix | Cible |
|------|------|-------|
| Starter | 49€/mois | TPE · 50 factures/mois |
| **Pro** ⭐ | **149€/mois** | PME · Illimité · le plus populaire |
| Scale | 399€/mois | ETI · Multi-users · API |

**+ 3% de commission sur les montants récupérés** (pay-as-you-win)

14 jours d’essai gratuit · Sans carte bancaire · Résiliable à tout moment

---

## 📚 Stack

- **Frontend** : [Streamlit](https://streamlit.io) 1.45+
- **IA** : Google Gemini 2.5 Flash via `google-genai`
- **Visualisations** : Plotly
- **PDF** : fpdf2
- **Email** : Resend API
- **Paiements** : Stripe (Payment Links)

---

## 🔑 Variables d’environnement

```env
GEMINI_API_KEY=sk-...      # Obligatoire — clé Gemini
RESEND_API_KEY=re_...      # Optionnel — envois emails réels
```

---

## 🇫🇷 Conformité légale

- ✅ **Loi LME** — pénalités de retard automatiques (BCE + 10 pts), indemnité forfaitaire 40€
- ✅ **RGPD** — données hébergées en Union Européenne
- ✅ **Facturation électronique** — compatible avec l’obligation fr. de sept. 2026

---

## 🤝 Programme Partenaire Expert-Comptable

20% de commission récurrente sur les abonnements de vos clients PME.  
Contactez-nous : **hello@invoiceguard.fr**

---

*Fait avec ❤️ en France · [invoiceguard.fr](https://invoiceguard.fr)*
