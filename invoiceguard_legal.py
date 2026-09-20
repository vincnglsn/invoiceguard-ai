"""
InvoiceGuard AI -- Mentions Legales, CGV & Politique de confidentialite
Conforme droit français (Loi Hamon, RGPD, LCEN).
"""

import streamlit as st
from datetime import date

st.set_page_config(page_title="Mentions legales — InvoiceGuard AI", page_icon="⚖️", layout="centered")
st.html('<style>[data-testid="stAppViewContainer"]{background:#0A0F1E}</style>')

tab_ml, tab_cgv, tab_rgpd = st.tabs(["⚖️ Mentions legales", "📋 CGV", "🔒 Confidentialite RGPD"])

ANNEE = date.today().year

# ─── MENTIONS LEGALES ─────────────────────────────────────────────────────────
with tab_ml:
    st.title("Mentions legales")
    st.caption(f"Derniere mise a jour : {date.today().strftime('%d/%m/%Y')}")
    st.markdown(f"""
### 1. Editeur du site

**InvoiceGuard AI** est une marque editee par :

- **Raison sociale** : InvoiceGuard AI (en cours d'immatriculation)
- **Forme juridique** : SAS (Societe par Actions Simplifiee)
- **Siege social** : France
- **Email** : hello@invoiceguard.fr
- **Directeur de la publication** : Vincent N.

### 2. Hebergement

L'application est hebergee sur :
- **Streamlit Community Cloud** — 651 Howard St, San Francisco, CA 94105, USA
- **GitHub** — 88 Colin P Kelly Jr St, San Francisco, CA 94107, USA

### 3. Propriete intellectuelle

L'ensemble des elements constituant l'application InvoiceGuard AI (textes, graphiques,
logiciels, base de donnees) sont la propriete exclusive d'InvoiceGuard AI ou font l'objet
de licences d'utilisation accordees par leurs titulaires.

Toute reproduction, representation, modification, publication ou adaptation de tout ou
partie des elements de l'application est interdite sans accord prealable ecrit.

### 4. Limitation de responsabilite

InvoiceGuard AI s'efforce d'assurer l'exactitude des informations disponibles sur
l'application. Toutefois, InvoiceGuard AI ne peut garantir l'exactitude, la completude ou
la mise a jour de ces informations. L'utilisateur est seul responsable de l'utilisation
qu'il fait des informations fournies.

### 5. Liens hypertextes

InvoiceGuard AI ne peut etre tenu responsable du contenu des sites tiers vers lesquels
des liens hypertextes sont etablis depuis l'application.

### 6. Droit applicable et juridiction competente

Les presentes mentions legales sont regies par la loi française. En cas de litige,
les tribunaux français seront seuls competents.
""")

# ─── CGV ──────────────────────────────────────────────────────────────────────
with tab_cgv:
    st.title("Conditions Generales de Vente")
    st.caption(f"Version en vigueur depuis le {date.today().strftime('%d/%m/%Y')}")
    st.markdown(f"""
### Article 1 — Objet

Les presentes Conditions Generales de Vente (CGV) regissent les relations contractuelles
entre InvoiceGuard AI (ci-apres "le Prestataire") et toute personne physique ou morale
(ci-apres "le Client") souscrivant a un abonnement InvoiceGuard AI.

### Article 2 — Description du service

InvoiceGuard AI est un logiciel SaaS (Software as a Service) de gestion et d'automatisation
du recouvrement de creances pour professionnels. Le service comprend :

- Analyse et scoring des factures impayees par intelligence artificielle
- Generation automatisee de relances conformes a la Loi LME
- Tableau de bord de suivi de tresorerie
- Export de rapports PDF professionnels
- Campagnes de relances en masse

### Article 3 — Tarifs et abonnements

**Plans disponibles :**

| Plan | Prix mensuel HT | Engagement |
|------|----------------|-----------|
| Starter | 49 EUR | Mensuel, sans engagement |
| Pro | 149 EUR | Mensuel, sans engagement |
| Scale | 399 EUR | Mensuel, sans engagement |

Les prix s'entendent hors taxes. La TVA applicable au taux en vigueur sera ajoutee.

**Commission au resultat :** 3% des montants effectivement recuperes grace au service,
preleves uniquement en cas de succes verifiable.

**Periode d'essai :** 14 jours gratuits, sans engagement, sans carte bancaire requise.
A l'issue de la periode d'essai, l'abonnement est automatiquement active si le Client
a fourni ses coordonnees de paiement.

### Article 4 — Modalites de paiement

Le paiement est effectue par carte bancaire via Stripe (prestataire de paiement securise
certifie PCI-DSS). Les abonnements sont renouveles automatiquement chaque mois a la date
anniversaire de souscription.

### Article 5 — Droit de retractation

Conformement a l'article L221-28 du Code de la consommation, le droit de retractation
ne s'applique pas aux services numeriques dont l'execution a commence avant la fin du
delai de retractation, avec l'accord expres du consommateur.

Toutefois, tout abonnement peut etre resilie a tout moment, sans frais, avec effet
a la fin de la periode de facturation en cours.

### Article 6 — Obligations du Prestataire

Le Prestataire s'engage a :
- Assurer la disponibilite du service (objectif : 99,9% de disponibilite mensuelle)
- Sauvegarder les donnees clients de facon securisee
- Maintenir la conformite du service avec la legislation en vigueur (Loi LME, RGPD)
- Repondre aux demandes de support dans un delai de 48h ouvrables

### Article 7 — Obligations du Client

Le Client s'engage a :
- Fournir des informations exactes lors de l'inscription
- Utiliser le service dans le respect du droit applicable
- Ne pas utiliser le service a des fins de harcelement ou de pratiques commerciales deloyales
- Conserver confidentiels ses identifiants de connexion

### Article 8 — Protection des donnees (voir aussi Politique RGPD)

Les donnees du Client sont traitees conformement au Reglement General sur la Protection
des Donnees (RGPD — Reglement UE 2016/679). Le Client dispose d'un droit d'acces,
de rectification et de suppression de ses donnees.

### Article 9 — Responsabilite

InvoiceGuard AI est un outil d'aide au recouvrement. Il appartient au Client de
verifier la conformite juridique de chaque relance avant envoi et d'assumer la
responsabilite des communications envoyees a ses clients.

La responsabilite d'InvoiceGuard AI ne pourra etre engagee pour :
- Les pertes de revenus consecutives a un echec de recouvrement
- Les erreurs de traitement des donnees importees par le Client
- Les interruptions de service inferieures a 72h consécutives

### Article 10 — Resiliation

Chaque partie peut resilier le contrat a tout moment. La resiliation prend effet
a la fin de la periode de facturation en cours. Aucun remboursement pro rata n'est
effectue pour la periode restante.

En cas de violation grave des presentes CGV, InvoiceGuard AI se reserve le droit
de suspendre ou resilier immediatement le compte du Client, sans preavis ni remboursement.

### Article 11 — Droit applicable

Les presentes CGV sont soumises au droit français. Tout litige sera soumis aux
tribunaux competents du ressort du siege social d'InvoiceGuard AI, sauf disposition
legale contraire applicable aux consommateurs.

**Version {ANNEE}.1 — En vigueur au {date.today().strftime('%d/%m/%Y')}**
""")

# ─── RGPD ─────────────────────────────────────────────────────────────────────
with tab_rgpd:
    st.title("Politique de Confidentialite & RGPD")
    st.caption(f"Derniere mise a jour : {date.today().strftime('%d/%m/%Y')}")
    st.markdown(f"""
### 1. Responsable du traitement

**InvoiceGuard AI** — hello@invoiceguard.fr

Conformement au RGPD (Reglement UE 2016/679), nous vous informons de nos pratiques
en matiere de traitement des donnees personnelles.

### 2. Donnees collectees

**Donnees d'inscription :**
- Nom, prenom, adresse email professionnelle
- Nom de l'entreprise
- Informations de paiement (stockees et traitees exclusivement par Stripe)

**Donnees operationnelles (fournies par le Client) :**
- Factures et donnees clients de l'utilisateur (noms, emails, montants)
- Ces donnees appartiennent exclusivement au Client et sont traitees en son nom

**Donnees d'usage :**
- Logs de connexion et d'utilisation (a des fins de securite et d'amelioration)
- Cookies de session (necessaires au fonctionnement)

### 3. Finalites du traitement

| Finalite | Base legale | Duree de conservation |
|---------|-------------|----------------------|
| Execution du contrat d'abonnement | Execution du contrat | Duree de l'abonnement + 5 ans |
| Facturation et comptabilite | Obligation legale | 10 ans |
| Support client | Interet legitime | 3 ans |
| Securite | Interet legitime | 1 an |
| Marketing (avec consentement) | Consentement | Jusqu'au retrait |

### 4. Sous-traitants

| Prestataire | Pays | Usage |
|-------------|------|-------|
| Streamlit / Snowflake | USA | Hebergement application |
| Stripe | USA | Paiements securises |
| Google (Gemini API) | USA | Generation IA des relances |
| Resend | USA | Envoi d'emails transactionnels |
| GitHub | USA | Code source (chiffre) |

Transferts hors UE encadres par les Clauses Contractuelles Types (CCT) de la Commission europeenne.

### 5. Vos droits

Conformement au RGPD, vous disposez des droits suivants :

- **Droit d'acces** : obtenir une copie de vos donnees
- **Droit de rectification** : corriger des donnees inexactes
- **Droit a l'effacement** : supprimer vos donnees ("droit a l'oubli")
- **Droit a la portabilite** : recevoir vos donnees dans un format lisible
- **Droit d'opposition** : vous opposer a certains traitements
- **Droit de limitation** : suspendre temporairement un traitement

Pour exercer vos droits : **hello@invoiceguard.fr**
Reponse garantie sous 30 jours.

En cas de litige non resolu : **CNIL** — www.cnil.fr — 3 place de Fontenoy, 75007 Paris

### 6. Cookies

InvoiceGuard AI utilise uniquement des cookies strictement necessaires au fonctionnement
de l'application (session utilisateur). Aucun cookie de tracage publicitaire n'est utilise.

### 7. Securite

Vos donnees sont protegees par :
- Chiffrement HTTPS/TLS en transit
- Acces restreint aux donnees (principe du moindre privilege)
- Authentification securisee
- Sauvegardes regulieres chiffrees

---
*Pour toute question : hello@invoiceguard.fr*
""")
