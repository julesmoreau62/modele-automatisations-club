"""Robot de garde : il surveille les autres robots.

Chaque lundi, il vérifie que chaque robot de donnees/robots.csv est actif, a tourné
récemment et n'a pas échoué. Sur un dépôt public, il prévient aussi avant que GitHub
ne coupe les robots après 60 jours sans activité. Il ne répare rien : il prévient.

Il ne peut pas se surveiller lui-même : une personne vérifie l'onglet Actions chaque mois
(c'est une ligne de donnees/obligations.csv).
"""
import os
import sys
from datetime import datetime, timezone

from commun import aujourdhui, date_fr, github, lire_tableau, ouvrir_ticket, resume

ALERTE_INACTIVITE = 45  # jours sans modification du dépôt avant de prévenir (GitHub coupe à 60)
ETATS = {
    "disabled_inactivity": "coupé par GitHub après 60 jours sans activité sur le dépôt",
    "disabled_manually": "mis en pause à la main (bouton d'arrêt)",
    "disabled_fork": "désactivé, car le dépôt est une copie (fork)",
}


def depuis(horodatage):
    quand = datetime.fromisoformat(horodatage.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - quand).days


def main():
    depot = os.environ["GITHUB_REPOSITORY"]
    attendus = {r["fichier"]: r for r in lire_tableau("donnees/robots.csv")}
    workflows = {os.path.basename(w["path"]): w
                 for w in github("GET", f"/repos/{depot}/actions/workflows?per_page=100")["workflows"]}
    alertes, bilan = [], []

    for fichier, robot in attendus.items():
        nom = robot.get("nom") or fichier
        w = workflows.get(fichier)
        if not w:
            alertes.append(f"**{nom}** : fichier `.github/workflows/{fichier}` introuvable.")
            continue
        if w["state"] != "active":
            alertes.append(f"**{nom}** : {ETATS.get(w['state'], w['state'])}. "
                           f"Pour le relancer : onglet Actions, « {w['name']} », bouton « Enable workflow ».")
            continue
        executions = github("GET", f"/repos/{depot}/actions/workflows/{w['id']}/runs?per_page=1")["workflow_runs"]
        if not executions:
            alertes.append(f"**{nom}** : n'a encore jamais tourné. Lancez-le une fois à la main pour vérifier.")
            continue
        derniere = executions[0]
        age = depuis(derniere["created_at"])
        limite = int(robot.get("jours_max") or 8)
        if derniere["conclusion"] == "failure":
            alertes.append(f"**{nom}** : la dernière exécution a échoué il y a {age} jour(s). "
                           f"[Lire le journal]({derniere['html_url']})")
        elif age > limite:
            alertes.append(f"**{nom}** : n'a pas tourné depuis {age} jours (au plus {limite} attendus).")
        bilan.append(f"| {nom} | il y a {age} jour(s) | {derniere['conclusion'] or 'en cours'} |")

    infos = github("GET", f"/repos/{depot}")
    if not infos["private"]:
        calme = depuis(infos["pushed_at"])
        if calme >= ALERTE_INACTIVITE:
            alertes.append(f"**Dépôt public sans modification depuis {calme} jours** : à 60 jours, GitHub coupe "
                           "les robots. Mettez à jour un fichier du dossier `donnees/` (par exemple les obligations).")

    resume(f"## Robot de garde, {date_fr(aujourdhui())}\n\n| Robot | Dernière exécution | Résultat |\n"
           "|---|---|---|\n" + "\n".join(bilan) +
           (f"\n\n**{len(alertes)} point(s) à vérifier.**" if alertes else "\n\nTout tourne normalement."))
    if alertes:
        ouvrir_ticket(f"Robot de garde : {len(alertes)} point(s) à vérifier",
                      "\n".join(f"- [ ] {a}" for a in alertes) +
                      "\n\n---\nOuvert par le robot de garde. Une fois tout réglé, fermez le ticket : "
                      "il en ouvrira un nouveau si un problème revient.")
        sys.exit(1)


if __name__ == "__main__":
    main()
