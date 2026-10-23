"""Robot des rappels.

Chaque matin, il relit donnees/obligations.csv et prévient quand une échéance approche :
aux jours indiqués dans la colonne « rappels » (30, 7…), et toujours le jour même.
Il ne fait rien d'autre : c'est la personne désignée dans la colonne « qui » qui agit.
"""
import calendar
import re
import sys
from datetime import date

from commun import (aujourdhui, dans, date_fr, envoyer_courriel, lire_date, lire_tableau,
                    normaliser, ouvrir_ticket, resume)

TABLEAU = "donnees/obligations.csv"
HORIZON = 60  # jours affichés dans le résumé
RAPPELS_PAR_DEFAUT = {30, 7}


def decaler(d, mois):
    """La même date, quelques mois plus tard (le 31 devient le dernier jour du mois)."""
    total = d.month - 1 + mois
    annee, mois_ = d.year + total // 12, total % 12 + 1
    return date(annee, mois_, min(d.day, calendar.monthrange(annee, mois_)[1]))


def prochaine(d, repetition, jour):
    """La prochaine fois que l'échéance tombe, à partir d'aujourd'hui."""
    r = normaliser(repetition)
    pas = 1 if ("mois" in r or "mensu" in r) else 12 if "an" in r else 0
    if not pas:
        return d
    n = 0
    while decaler(d, n * pas) < jour:
        n += 1
    return decaler(d, n * pas)


def main():
    jour = aujourdhui()
    erreurs, a_venir, a_rappeler = [], [], []

    for numero, ligne in enumerate(lire_tableau(TABLEAU), start=2):
        echeance = lire_date(ligne.get("date"))
        quoi = ligne.get("quoi", "")
        if not echeance or not quoi:
            erreurs.append(f"ligne {numero} : date ou tâche illisible ({ligne.get('date') or 'vide'})")
            continue
        echeance = prochaine(echeance, ligne.get("repetition", ""), jour)
        if echeance < jour:
            continue  # échéance passée, sans répétition
        try:
            jours = {int(x) for x in re.split(r"[\s,;/]+", ligne.get("rappels", "")) if x}
        except ValueError:
            erreurs.append(f"ligne {numero} : colonne « rappels » illisible ({ligne.get('rappels')})")
            jours = set()
        jours = (jours or RAPPELS_PAR_DEFAUT) | {0}
        tache = {"date": echeance, "reste": (echeance - jour).days, "quoi": quoi,
                 "qui": ligne.get("qui") or "Bureau", "lien": ligne.get("lien", "")}
        if tache["reste"] <= HORIZON:
            a_venir.append(tache)
        if tache["reste"] in jours:
            a_rappeler.append(tache)

    a_venir.sort(key=lambda t: t["date"])
    a_rappeler.sort(key=lambda t: t["date"])

    texte = [f"## Rappels du {date_fr(jour)}"]
    if a_venir:
        texte.append(f"Échéances des {HORIZON} prochains jours :\n\n| Date | Quoi | Qui |\n|---|---|---|\n" +
                     "\n".join(f"| {date_fr(t['date'])} ({dans(t['reste'])}) | {t['quoi']} | {t['qui']} |"
                               for t in a_venir))
    else:
        texte.append(f"Aucune échéance dans les {HORIZON} prochains jours.")
    texte.append(f"Rappel(s) à envoyer aujourd'hui : **{len(a_rappeler)}**.")
    resume("\n\n".join(texte))

    if a_rappeler:
        corps = []
        for qui in sorted({t["qui"] for t in a_rappeler}):
            corps.append(f"### {qui}")
            for t in (t for t in a_rappeler if t["qui"] == qui):
                ligne = f"- [ ] **{t['quoi']}** : échéance le {date_fr(t['date'])} ({dans(t['reste'])})."
                if t["lien"]:
                    ligne += f" [Lien utile]({t['lien']})"
                corps.append(ligne)
            corps.append("")
        corps.append("---\nOuvert par le robot des rappels, à partir de `donnees/obligations.csv`. "
                     "Cochez les cases au fur et à mesure, puis fermez le ticket.")
        ouvrir_ticket(f"Rappels du {date_fr(jour, avec_jour=False)}", "\n".join(corps))
        for qui in sorted({t["qui"] for t in a_rappeler}):
            lignes = [f"- {t['quoi']} : le {date_fr(t['date'])} ({dans(t['reste'])})"
                      for t in a_rappeler if t["qui"] == qui]
            envoyer_courriel(qui, f"Rappel du club : {len(lignes)} échéance(s) à venir",
                             "Bonjour,\n\nÉchéances à préparer :\n" + "\n".join(lignes) +
                             "\n\nMessage envoyé par le robot des rappels du club.")

    if erreurs:
        # Une ligne mal remplie fait échouer l'exécution, exprès : l'alerte part et le robot de garde la voit.
        resume("### Lignes à corriger dans " + TABLEAU + "\n\n" + "\n".join(f"- {e}" for e in erreurs))
        sys.exit(1)


if __name__ == "__main__":
    main()
