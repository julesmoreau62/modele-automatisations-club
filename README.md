# Modèle d'automatisations pour club sportif

Quatre petits robots prêts à copier, pour les bénévoles d'un club sportif.
Ils tournent tout seuls sur GitHub, à heure fixe, et préviennent le bureau par un ticket (et par e-mail si vous le réglez).
Ils sont livrés avec les données **fictives** de l'AS Exemple Handball, le club fil rouge de la [formation FAIR](https://fair-asso.fr/formation.html).

| Robot | Quand | Ce qu'il fait | IA |
|---|---|---|---|
| **Rappels des obligations** | Chaque matin | Prévient avant chaque échéance du club (subventions, assurance, AG, préfecture…) | Non |
| **Veille des appels à projets** | Le lundi | Relève sur les sites des financeurs les appels dont la date limite approche | Facultative |
| **Site du club** | Chaque nuit | Met à jour la page du club : prochains matchs, résultats, entraînements | Non |
| **Robot de garde** | Le lundi | Vérifie que les trois autres tournent, et prévient sinon | Non |

L'atelier pas à pas qui accompagne ce modèle : [Ma première tâche programmée](https://fair-asso.fr/formation-n4-atelier.html).

## Trois règles avant de commencer

1. **Aucune donnée d'adhérent dans ce dépôt.** Ni nom, ni téléphone, ni date de naissance, ni photo. Les robots qui touchent aux adhérents se construisent dans le tableur du club, pas ici.
2. **Le dépôt appartient au club.** Créez une organisation GitHub au nom du club (l'offre gratuite suffit) avec **deux propriétaires**, puis copiez le modèle dedans. Jamais sur le compte personnel d'un bénévole : le jour où il part, tout s'arrête.
3. **Le mode essai d'abord.** Tant que la variable `MODE_ESSAI` ne vaut pas « non », les robots n'envoient rien : ils affichent ce qu'ils auraient fait. Le bureau valide les fiches R.E.L.A.I.S. de [`docs/fiches-relais.md`](docs/fiches-relais.md), puis on passe en réel.

## Démarrer en dix minutes

1. **Copier le modèle.** Bouton vert **Use this template**, puis **Create a new repository**. Choisissez l'organisation du club comme propriétaire.
   Visibilité : **privé** si vous n'utilisez pas le site ; **public** si vous voulez le site gratuit (GitHub Pages l'exige), et dans ce cas rien de privé n'entre jamais dans le dépôt.
2. **Ouvrir l'onglet Actions.** Si GitHub le demande, activez les workflows.
3. **Lancer un robot à la main.** Choisissez **Rappels des obligations**, bouton **Run workflow**. Pour voir un jour de rappel, saisissez une date simulée, par exemple `2026-11-06`.
4. **Lire le résultat.** Cliquez sur l'exécution : le résumé affiche les échéances et le ticket qui aurait été ouvert. Le **journal** (étape « Préparer les rappels du jour ») montre chaque étape en détail.
5. **Mettre vos échéances.** Ouvrez `donnees/obligations.csv`, crayon **Edit**, remplacez les lignes d'exemple, puis **Commit changes**. Relancez le robot.
6. **Passer en réel, après validation du bureau.** **Settings**, **Secrets and variables**, **Actions**, onglet **Variables**, **New repository variable** : `MODE_ESSAI` = `non`. Les rappels deviennent des tickets (onglet **Issues**) ; les personnes qui suivent le dépôt sont prévenues.

## Les réglages

Tout se règle dans **Settings**, **Secrets and variables**, **Actions**. Une **variable** est visible par les membres du dépôt ; un **secret** ne se relit jamais, même par celui qui l'a saisi.

| Variable | Valeur | Effet |
|---|---|---|
| `MODE_ESSAI` | `non` | Les robots ouvrent les tickets et envoient les e-mails. Absente ou autre valeur : mode essai. |
| `ROBOTS_ACTIFS` | `non` | **L'interrupteur général** : plus aucun robot ne tourne. |
| `PUBLIER_SITE` | `oui` | Le site est publié sur GitHub Pages (voir plus bas). |
| `SOURCE_MATCHS` | une adresse | Facultatif : le tableau des matchs publié par le tableur du club, au format CSV, à la place de `donnees/matchs.csv`. |
| `IA_MODELE` | un nom de modèle | Facultatif : le modèle d'IA de la veille. Par défaut `claude-opus-5-5`. |

| Secret | Pour quoi |
|---|---|
| `ANTHROPIC_API_KEY` | Facultatif : le tri de la veille par l'IA. |
| `CONTACTS` | Les adresses e-mail par rôle, une ligne par rôle : `Trésorier = tresorier@club.fr`. Une ligne `Bureau = …` sert pour les rôles sans adresse. |
| `SMTP_SERVEUR`, `SMTP_PORT`, `SMTP_UTILISATEUR`, `SMTP_MOT_DE_PASSE`, `SMTP_EXPEDITEUR` | Facultatif : la boîte d'envoi du club pour les e-mails. Port 465 (SSL) ou 587 (STARTTLS). Utilisez un mot de passe d'application, pas le mot de passe principal de la boîte. |

## Le site du club

1. Le dépôt doit être **public** (offre gratuite de GitHub).
2. **Settings**, **Pages**, **Source** : **GitHub Actions**.
3. Variable `PUBLIER_SITE` = `oui`, puis lancez **Site du club** à la main.
4. L'adresse du site s'affiche dans l'exécution (étape « Publier »).

Le site ne montre que des informations publiques : équipes, horaires, lieux, scores. Jamais de nom de joueur.
Pour que les bénévoles n'aient pas à toucher au dépôt, tenez le tableau des matchs dans le tableur du club, publiez-le au format CSV et mettez son adresse dans `SOURCE_MATCHS`.

## La veille avec l'IA

Sans clé, la veille trie avec les **mots-clés** de `donnees/fiche-club.md`. Avec le secret `ANTHROPIC_API_KEY`, l'IA choisit les appels qui concernent le club et dit pourquoi.

- La clé appartient au club : un compte d'organisation chez le fournisseur, payé par le club, jamais l'abonnement personnel d'un bénévole.
- L'IA ne reçoit que des pages publiques et la fiche publique du club : rien de personnel.
- Fixez une limite de dépense mensuelle dans la console du fournisseur. À ce volume, une veille par semaine coûte peu, mais c'est à vérifier sur vos premières factures.
- Le modèle est réglable avec la variable `IA_MODELE`. Pour un autre fournisseur, demandez à votre assistant IA d'adapter la fonction `trier_par_ia` de `scripts/veille.py`, puis relisez-la avec [`docs/relire-un-workflow.md`](docs/relire-un-workflow.md).

Ajoutez dans `donnees/sources-veille.csv` la page « appels à projets » de votre mairie, de votre département, de votre région et de votre comité : ce sont souvent les plus utiles.

## Tout arrêter

- **Un robot** : onglet **Actions**, choisir le robot, menu **…**, **Disable workflow**.
- **Tous les robots** : variable `ROBOTS_ACTIFS` = `non`.
- **Seulement le site** : variable `PUBLIER_SITE` = `non`.

## Quand ça casse

- **Un robot échoue** : GitHub envoie un e-mail à **la personne qui a modifié la ligne `cron:` en dernier**. Après un départ, un responsable actuel décale d'une minute l'horaire de chaque robot depuis son propre compte (7 h 17 devient 7 h 18) : les alertes lui arrivent ensuite. Le journal de l'exécution dit ce qui s'est passé.
- **60 jours sans modification sur un dépôt public** : GitHub coupe les robots. Le robot de garde prévient à 45 jours ; mettez à jour un tableau du dossier `donnees/`.
- **Le robot de garde ne peut pas se surveiller lui-même** : la première ligne de `donnees/obligations.csv` demande une vérification humaine chaque mois.
- **Une ligne mal remplie** dans un tableau fait échouer le robot exprès, avec la ligne à corriger dans le résumé.

## Tester sur son ordinateur

Avec Python 3.10 ou plus récent, depuis le dossier du dépôt :

```bash
python scripts/rappels.py
DATE_SIMULEE=2026-11-06 python scripts/rappels.py
python scripts/site.py
python scripts/veille.py
```

Sur un ordinateur, rien n'est envoyé : les résultats s'affichent à l'écran. Sous Windows, installez d'abord le paquet `tzdata` (`pip install tzdata`) pour l'heure de Paris.

## Ce qu'il y a dans le dépôt

```
.github/workflows/   les quatre robots : quand ils tournent, avec quels droits
scripts/             ce qu'ils font, en Python, sans dépendance (sauf l'IA de la veille)
donnees/             les tableaux que les bénévoles mettent à jour
site/                le modèle de la page du club
docs/                fiches R.E.L.A.I.S., registre des outils, relecture d'un robot
```

---

Modèle proposé par [FAIR](https://fair-asso.fr), Former les Associations à l'IA Responsable. Licence MIT : copiez-le, adaptez-le, partagez-le.
