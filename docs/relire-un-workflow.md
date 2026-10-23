# Relire un robot avant de l'activer : 8 points

À faire pour chaque fichier de `.github/workflows/`, qu'il ait été écrit par un bénévole ou par une IA.
Un seul « non », et le robot reste en mode essai.

1. **Les autorisations sont le strict nécessaire.** Le bloc `permissions:` est écrit en haut du fichier, et chaque droit sert à quelque chose (`issues: write` pour ouvrir un ticket, rien de plus).
2. **Rien de sensible n'est écrit dans le fichier.** Mots de passe, clés et adresses e-mail passent par les secrets (`${{ secrets.… }}`). Les secrets et les valeurs saisies au lancement passent par `env:`, jamais collés directement dans une commande `run:`.
3. **Les outils extérieurs sont figés.** Chaque ligne `uses:` pointe vers une empreinte (une longue suite de chiffres et de lettres), pas vers une étiquette comme `@v7`, qui peut changer sans prévenir.
4. **L'horaire est à l'heure de Paris.** La ligne `cron:` est accompagnée de `timezone: "Europe/Paris"`, et ne tombe pas à l'heure pile (7 h 17 plutôt que 7 h 00).
5. **Le mode essai protège.** Tant que le bureau n'a pas validé, `MODE_ESSAI` n'est pas à « non » : rien ne sort du dépôt.
6. **On peut tout arrêter.** Le travail porte `if: vars.ROBOTS_ACTIFS != 'non'` et une durée maximale (`timeout-minutes`).
7. **Aucune donnée personnelle.** Le robot ne lit ni n'écrit de données d'adhérents, et le dépôt n'en contient aucune.
8. **Il est documenté.** Sa fiche R.E.L.A.I.S. et sa ligne du registre sont écrites, avec un responsable et une personne de secours.
