import csv
from datetime import datetime, timedelta

posts = [
    """Combien d'heures votre équipe perd-elle chaque semaine à répondre aux mêmes questions ? 🤔

« Où en est ma commande ? », « Quels sont vos horaires ? », « Avez-vous ce produit en stock ? »

Hier, j'ai configuré un Agent IA pour un client en un temps record. Il est connecté à leur base de connaissances, répond instantanément 24h/24, et ne fait jamais d'erreurs. 

Résultat : Le service client est passé d'un centre de coût à une machine de conversion. 

L'IA n'est plus de la science-fiction, c'est un avantage concurrentiel vital. Votre entreprise est-elle équipée ? 🚀

#IntelligenceArtificielle #Business #Automatisation #Tech""",
    
    """J'ai construit un "Cerveau Numérique" d'entreprise en 10 minutes ce matin. 🧠

Le concept est simple : 
1. On aspire l'intégralité d'un site web (FAQ, politiques, services).
2. On injecte ces données dans un modèle IA ultra-sécurisé.
3. On obtient un Assistant expert capable de qualifier des leads et de closer des ventes à 3h du matin.

Si vous voulez voir à quoi ressemblerait le "Cerveau" de VOTRE entreprise, envoyez-moi le lien de votre site en message privé. Je vous fais une démo personnalisée avec mon outil. 👇

#Innovation #Entrepreneur #SaaS #IA""",
    
    """L'erreur n°1 des PME avec l'Intelligence Artificielle ❌

Penser que c'est réservé à Google ou Amazon. 

La vérité ? Les outils d'IA n'ont jamais été aussi accessibles. Mais utiliser ChatGPT comme un simple moteur de recherche, c'est utiliser une Formule 1 pour faire ses courses.

La vraie valeur, c'est l'INTÉGRATION. 
Brancher l'IA sur VOTRE CRM. 
Brancher l'IA sur VOS emails. 
Brancher l'IA sur VOTRE service client.

C'est exactement ce que nous mettons en place. Si vous faites encore des tâches répétitives sur Excel, il faut qu'on parle. 📞

#PME #Productivite #FuturDuTravail #Automation""",
    
    """Imaginez une agence (ou une boutique) qui ne dort jamais. 🏢🌙

Il est 23h. Un client potentiel visite votre site web. Il a un gros budget et cherche une réponse urgente. 

Sans IA : Il remplit un formulaire ennuyeux. Un commercial le rappellera le lendemain à 10h (s'il n'est pas déjà parti chez la concurrence).
Avec IA : Un assistant virtuel engage la conversation, qualifie le besoin du prospect, répond à ses questions expertes, et cale un RDV directement dans votre agenda. 

Ce système n'est pas pour demain. Nous le déployons aujourd'hui pour nos clients. 

#Croissance #Vente #LeadGen #IntelligenceArtificielle""",
    
    """Êtes-vous sûr de ne pas jeter de l'argent par les fenêtres ? 💸

80% des entreprises que j'analyse paient des abonnements logiciels inutiles ou perdent des dizaines d'heures sur des tâches administratives 100% automatisables.

Cette semaine, j'ouvre 3 créneaux pour un "Audit de Productivité IA" gratuit de 30 minutes. 

On va passer votre entreprise au peigne fin : 
✅ Vos processus actuels
✅ Vos goulets d'étranglement (ce qui vous fait perdre du temps)
✅ Les solutions IA exactes à implémenter pour réduire vos coûts

Les 3 premiers à commenter "AUDIT" sous ce post sécurisent leur place. Prêts ? 👇

#Consulting #CEO #Management #Tech"""
]

base_date = datetime.now() + timedelta(days=1)

with open('linkedin_posts.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['Texte du Post', 'Date de publication', 'Statut', 'URL de l\'image'])
    
    for i, post in enumerate(posts):
        pub_date = (base_date + timedelta(days=i)).strftime("%d/%m/%Y")
        writer.writerow([post.strip(), pub_date, 'En attente', ''])

print("Fichier CSV genere avec succes !")
