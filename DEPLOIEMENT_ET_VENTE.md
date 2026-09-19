# 🚀 InvoiceGuard AI — Guide de Déploiement & Mise en Vente
# Actions concrètes pour encaisser les premiers euros AUJOURD'HUI

## ════════════════════════════════════════════════════════════
## ÉTAPE 1 — DÉPLOIEMENT PUBLIC (30 minutes)
## ════════════════════════════════════════════════════════════

### Option A : Streamlit Community Cloud (GRATUIT — recommandé pour commencer)

1. Créez un compte GitHub sur github.com (si pas déjà fait)
2. Créez un nouveau repository PUBLIC nommé "invoiceguard-ai"
3. Uploadez tous les fichiers du projet (ou git push)
4. Allez sur https://share.streamlit.io
5. Cliquez "Create app" → sélectionnez votre repo
6. Main file path : `streamlit_app.py`
7. Dans "Advanced settings" → "Secrets", collez :
   ```
   GEMINI_API_KEY = "votre_cle_gemini"
   ```
8. Cliquez Deploy → URL publique en 3 minutes

Résultat : https://votre-app.streamlit.app (URL publique, gratuit)

---

### Option B : Railway.app (5€/mois — plus fiable)

1. Créez un compte sur railway.app
2. New Project → Deploy from GitHub repo
3. Add Variable : GEMINI_API_KEY = votre_clé
4. Domaine custom possible (invoiceguard.fr)

---

### Option C : Déploiement local + tunnel Ngrok (IMMÉDIAT — 0 min setup)
```powershell
# Installez ngrok : https://ngrok.com/download
ngrok http 8502
# → URL publique temporaire (ex: https://xxxx.ngrok.io)
# Valable pour démos clients en temps réel
```

---

## ════════════════════════════════════════════════════════════
## ÉTAPE 2 — PAIEMENTS STRIPE (15 minutes)
## ════════════════════════════════════════════════════════════

1. Créez un compte Stripe : https://stripe.com/fr
2. Vérifiez votre identité (IBAN requis pour les virements)
3. Dans Products > Payment Links, créez 3 abonnements :

   | Plan    | Prix    | Période | Description                           |
   |---------|---------|---------|---------------------------------------|
   | Starter | 49€     | Mensuel | InvoiceGuard AI — Plan Starter        |
   | Pro     | 149€    | Mensuel | InvoiceGuard AI — Plan Pro            |
   | Scale   | 399€    | Mensuel | InvoiceGuard AI — Plan Scale          |

4. Activez "14 jours d'essai gratuit" sur chaque plan
5. Copiez les liens générés (buy.stripe.com/xxxxx)
6. Collez-les dans `invoiceguard_pricing.py` à la ligne STRIPE_LINKS

---

## ════════════════════════════════════════════════════════════
## ÉTAPE 3 — CALENDLY (5 minutes — essentiel)
## ════════════════════════════════════════════════════════════

1. Créez un compte Calendly : https://calendly.com (gratuit)
2. Créez un événement "Démo InvoiceGuard 15 min"
3. Description : "Je vous montre comment récupérer vos impayés automatiquement"
4. Copiez votre lien Calendly
5. Remplacez "https://calendly.com/invoiceguard/demo-15min" dans le code

---

## ════════════════════════════════════════════════════════════
## ÉTAPE 4 — LANCEMENT (Aujourd'hui même)
## ════════════════════════════════════════════════════════════

### Ce matin (30 min) :
[ ] Déployer sur Streamlit Cloud (Étape 1)
[ ] Créer les 3 plans Stripe (Étape 2)
[ ] Configurer Calendly (Étape 3)
[ ] Mettre à jour les liens dans la landing page

### Aujourd'hui (2h) :
[ ] Publier le POST LINKEDIN n°1 du kit VENTE_KIT_COMPLET.md
[ ] Envoyer 5 emails froids PME (variante 1) à votre réseau proche
[ ] Contacter 1-2 experts-comptables de votre connaissance (email EC du kit)

### Cette semaine :
[ ] POST LINKEDIN n°2 (mercredi)
[ ] POST LINKEDIN n°3 (vendredi)
[ ] 20 cold emails PME supplémentaires
[ ] Démo avec au moins 1 EC intéressé

### Objectif J+14 :
→ 5 clients en essai gratuit
→ 2 clients payants = 298€ MRR
→ 1 EC partenaire = pipeline de 50+ prospects

---

## ════════════════════════════════════════════════════════════
## RESSOURCES GÉNÉRÉES
## ════════════════════════════════════════════════════════════

| Fichier | Usage |
|---------|-------|
| `VENTE_KIT_COMPLET.md` | LinkedIn posts + cold emails + PH copy |
| `invoiceguard_pricing.py` | Page pricing avec Stripe links |
| `invoiceguard_prospecteur.py` | Génère les cold emails automatiquement |
| `invoiceguard_partenaire_ec.py` | Démo pour convaincre les EC |
| `invoiceguard_landing/index.html` | Landing page de conversion |
| `streamlit_app.py` | Point d'entrée pour Streamlit Cloud |
| `requirements.txt` | Dépendances pour le déploiement |
