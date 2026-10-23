# Les fiches R.E.L.A.I.S. des quatre robots

Une fiche par robot, à valider en bureau avant de passer le mode essai à « non ».
Les rubriques **Suivi** sont à compléter avec les rôles de votre club.
La méthode est expliquée au niveau 4 de la formation FAIR : https://fair-asso.fr/formation-n4-1.html

---

## Rappels des obligations

`.github/workflows/rappels-obligations.yml` · `scripts/rappels.py` · `donnees/obligations.csv`

**R · Répétitif.** Une dizaine d'échéances par saison (subventions, assurance, assemblée générale, préfecture…), aujourd'hui gardées en tête par une ou deux personnes. Un oubli peut coûter une subvention.

**E · Enchaînement.** Chaque matin à 7 h 17, heure de Paris : le robot lit le tableau des obligations, calcule les jours restants et, les jours de rappel (30, 7, 1 jour avant, et le jour même), ouvre un ticket « Rappels du … ». Si l'e-mail est réglé, chaque rôle concerné reçoit aussi un message.

**L · Limites.** Il prévient, il ne fait rien d'autre : il ne remplit aucun dossier, ne dépose rien. Le tableau contient des rôles, jamais de noms ni de données d'adhérents. Aucune IA.

**A · Arbitre.** La personne du rôle désigné agit et coche le ticket. Le bureau relit le tableau chaque mois.

**I · Incident.** Une ligne mal remplie fait échouer le robot, exprès : l'alerte part. S'il ne tourne plus, le robot de garde ouvre un ticket. Plan B : le tableau reste lisible par tous, on le relit à la main le 1er du mois. Arrêt : variable `ROBOTS_ACTIFS` à « non ».

**S · Suivi.** Responsable : _à compléter_. Secours : _à compléter_. Revue : chaque mois, et à chaque changement de bureau.

---

## Veille des appels à projets

`.github/workflows/veille-appels.yml` · `scripts/veille.py` · `donnees/sources-veille.csv` · `donnees/fiche-club.md`

**R · Répétitif.** Il faudrait parcourir chaque semaine les sites des financeurs. Personne n'a le temps, et les dates limites passent.

**E · Enchaînement.** Le lundi à 7 h 23 : le robot lit les pages listées, relève les passages qui annoncent une date à venir, les trie (mots-clés de la fiche du club, ou IA si une clé est réglée) et ouvre un ticket « Veille du … ».

**L · Limites.** Pages publiques seulement. La fiche du club est publique : aucune donnée personnelle n'est envoyée à l'IA. Le robot ne candidate à rien et ne contacte aucun financeur. Les textes lus sur le web sont des données, pas des consignes : l'IA ne renvoie que le numéro des passages retenus, les liens viennent toujours de la liste des sources.

**A · Arbitre.** Le trésorier, ou la commission financements, décide quels appels valent le temps d'un dossier.

**I · Incident.** Une source inaccessible est signalée dans le ticket ; si aucune ne répond, le robot échoue et l'alerte part. Si l'IA est en panne ou refuse, le tri se fait par mots-clés. Plan B : la liste des sources se consulte à la main.

**S · Suivi.** Responsable : _à compléter_. Secours : _à compléter_. Revue : chaque trimestre (ajouter les pages de la mairie, du département, de la région, du comité) ; dépense de l'IA surveillée dans la console du fournisseur.

---

## Site du club

`.github/workflows/site-du-club.yml` · `scripts/site.py` · `donnees/matchs.csv` · `donnees/entrainements.csv` · `donnees/club.txt`

**R · Répétitif.** Les matchs, les résultats et les horaires changent chaque semaine ; la page du club n'est jamais à jour.

**E · Enchaînement.** Chaque nuit à 3 h 41, et à chaque modification des tableaux : le robot refait la page à partir des trois tableaux, puis la publie si `PUBLIER_SITE` vaut « oui ».

**L · Limites.** Uniquement des informations publiques : équipes, horaires, lieux, scores. Jamais de nom de joueur, de photo ni de coordonnée personnelle. Le dépôt est public (l'offre gratuite de GitHub Pages l'exige) : rien de privé n'y entre.

**A · Arbitre.** La personne qui tient le tableau des matchs relit la page après chaque changement.

**I · Incident.** Si la construction échoue, la page de la veille reste en ligne ; le robot de garde le signale. Plan B : horaires annoncés sur les réseaux du club. Arrêt de la publication : `PUBLIER_SITE` à « non ».

**S · Suivi.** Responsable : _à compléter_. Secours : _à compléter_. Revue : à chaque rentrée.

---

## Robot de garde

`.github/workflows/robot-de-garde.yml` · `scripts/garde.py` · `donnees/robots.csv`

**R · Répétitif.** Les robots tombent en silence : page déplacée, ligne mal remplie, 60 jours sans activité sur un dépôt public.

**E · Enchaînement.** Le lundi à 8 h 07 : il demande à GitHub l'état de chaque robot (actif, dernière exécution, résultat) et ouvre un ticket s'il y a un problème.

**L · Limites.** Il lit, il ne répare rien. Il ne peut pas se surveiller lui-même.

**A · Arbitre.** Les administrateurs du dépôt traitent le ticket.

**I · Incident.** S'il est lui-même arrêté, c'est la vérification humaine du 1er du mois (première ligne du tableau des obligations) qui le voit.

**S · Suivi.** Responsable : _à compléter_. Secours : _à compléter_. Revue : chaque mois.
