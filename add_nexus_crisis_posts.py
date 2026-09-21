import csv
from datetime import datetime, timedelta

# Posts Nexus AI (Supply Chain Shield) — hook basé sur la crise réelle du 21/09/2026
# A regenerer chaque semaine avec les signaux actuels de worldmonitor.app/dashboard
new_posts = [
    """🔴 En ce moment : Mer Rouge en alerte élevée, Détroit d'Ormuz à 35-40% de risque de perturbation, brouillage GPS actif en Mer Noire.

Si vous importez d'Asie ou du Moyen-Orient, votre Supply Chain est déjà exposée — que vous le sachiez ou non.

90% des directeurs Achats/Logistique découvrent l'impact d'une crise en ouvrant Excel en panique, une fois le conteneur déjà bloqué.

→ Nexus AI croise votre fichier fournisseurs avec les alertes géopolitiques mondiales en direct
→ Calcule l'exposition réelle de votre portefeuille
→ Génère en 1 clic un plan de continuité avec fournisseurs alternatifs et surcoût fret estimé

Testez avec votre propre fichier Excel. 49€/mois, résiliable à tout moment.

#SupplyChain #Logistique #ImportExport #IntelligenceArtificielle #Achats""",

    """Avant Nexus AI :
❌ On apprend la crise par les infos, 3 jours trop tard
❌ Excel + appels paniqués aux fournisseurs
❌ Aucune idée du coût réel de l'exposition

Après Nexus AI :
✅ Alerte croisée avec votre portefeuille dès que le risque apparaît
✅ Score d'exposition par fournisseur, par route
✅ Plan de continuité généré par IA en 2 minutes

Un conteneur bloqué 3 semaines, c'est en moyenne 50 000€ de marge perdue pour une PME industrielle.
Nexus AI coûte 49€/mois.

#Achats #Industrie #Risque #SaaS #CEO""",

    """Le vrai coût d'une rupture Supply Chain, ce n'est jamais le fret aérien de remplacement.

C'est la ligne de production à l'arrêt, le client final qui va voir ailleurs, et votre équipe qui cherche des alternatives dans l'urgence.

Avec les tensions actuelles (Ormuz, Mer Rouge, Mer Noire), ce n'est plus une hypothèse d'école — c'est un scénario probable pour toute entreprise qui importe d'Asie ou du Moyen-Orient.

Nexus AI croise votre fichier fournisseurs avec les alertes mondiales en direct et vous donne un plan B avant d'en avoir besoin.

#SupplyChain #Logistique #GestionDeRisque #PME #Industrie"""
]

file_path = 'linkedin_posts.csv'
last_date = datetime.now()

try:
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = list(csv.reader(f, delimiter=';'))
        if len(reader) > 1:
            last_date_str = reader[-1][1]
            last_date = datetime.strptime(last_date_str, "%d/%m/%Y")
except Exception:
    pass

with open(file_path, 'a', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f, delimiter=';')
    for i, post in enumerate(new_posts):
        pub_date = (last_date + timedelta(days=i + 1)).strftime("%d/%m/%Y")
        writer.writerow([post.strip(), pub_date, 'En attente', ''])

print("3 posts Nexus AI (crise du jour) ajoutes a la machine LinkedIn.")
