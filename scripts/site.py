"""Robot du site du club.

Chaque nuit, il refait la page d'accueil du site à partir de trois tableaux :
les matchs (à venir et résultats), les entraînements et la fiche du club.
Aucune donnée personnelle : des équipes, des horaires, des lieux, jamais de noms de joueurs.

La page est écrite dans le dossier _site/, que GitHub Pages publie si PUBLIER_SITE vaut « oui ».
"""
import html
import os
import shutil

from commun import (aujourdhui, chemin, date_fr, lire_date, lire_tableau, lire_texte, maintenant,
                    normaliser, resume)

FENETRE = 14  # jours avant et après aujourd'hui
SORTIE = chemin("_site")


def fiche():
    """donnees/club.txt : une information par ligne, « clé : valeur »."""
    infos = {}
    for ligne in lire_texte("donnees/club.txt").splitlines():
        if ":" in ligne and not ligne.lstrip().startswith("#"):
            cle, valeur = ligne.split(":", 1)
            infos[normaliser(cle)] = valeur.strip()
    return infos


def e(texte):
    return html.escape(texte or "")


def main():
    jour = aujourdhui()
    club = fiche()
    source = os.environ.get("SOURCE_MATCHS", "").strip() or "donnees/matchs.csv"
    matchs = []
    for m in lire_tableau(source):
        d = lire_date(m.get("date"))
        if d:
            matchs.append({**m, "jour": d})
    matchs.sort(key=lambda m: (m["jour"], m.get("heure", "")))

    a_venir = [m for m in matchs if 0 <= (m["jour"] - jour).days <= FENETRE]
    resultats = [m for m in matchs if 0 < (jour - m["jour"]).days <= FENETRE and m.get("score")]
    resultats.reverse()

    def lieu(m):
        dom = normaliser(m.get("domicile")) in {"oui", "o", "x", "dom", "domicile"}
        return ("À domicile" if dom else "À l'extérieur") + (f" · {e(m.get('lieu'))}" if m.get("lieu") else "")

    lignes = [f"<li><time datetime=\"{m['jour'].isoformat()}\">{e(date_fr(m['jour']))}"
              f"{' · ' + e(m['heure']) if m.get('heure') else ''}</time>"
              f"<p><b>{e(m.get('equipe'))}</b> contre {e(m.get('adversaire'))}</p><span>{lieu(m)}</span></li>"
              for m in a_venir]
    bloc_matchs = f"<ul class=\"liste\">{''.join(lignes)}</ul>" if lignes else \
        "<p class=\"vide\">Pas de match dans les deux prochaines semaines.</p>"

    lignes = [f"<li><time datetime=\"{m['jour'].isoformat()}\">{e(date_fr(m['jour']))}</time>"
              f"<p><b>{e(m.get('equipe'))}</b> contre {e(m.get('adversaire'))}</p><strong>{e(m['score'])}</strong></li>"
              for m in resultats]
    bloc_resultats = f"<ul class=\"liste\">{''.join(lignes)}</ul>" if lignes else \
        "<p class=\"vide\">Pas de résultat ces deux dernières semaines.</p>"

    lignes = [f"<tr><th scope=\"row\">{e(t.get('equipe'))}</th><td>{e(t.get('jour'))}</td>"
              f"<td>{e(t.get('horaire'))}</td><td>{e(t.get('lieu'))}</td></tr>"
              for t in lire_tableau("donnees/entrainements.csv")]
    bloc_entrainements = ("<table><thead><tr><th scope=\"col\">Équipe</th><th scope=\"col\">Jour</th>"
                          "<th scope=\"col\">Horaire</th><th scope=\"col\">Lieu</th></tr></thead>"
                          f"<tbody>{''.join(lignes)}</tbody></table>")

    page = lire_texte("site/modele.html")
    remplacements = {
        "NOM": e(club.get("nom", "Notre club")), "VILLE": e(club.get("ville")),
        "PRESENTATION": e(club.get("presentation")), "CONTACT": e(club.get("contact")),
        "MATCHS": bloc_matchs, "RESULTATS": bloc_resultats, "ENTRAINEMENTS": bloc_entrainements,
        "MISE_A_JOUR": e(f"{date_fr(maintenant().date())} à {maintenant():%H:%M}"),
    }
    for cle, valeur in remplacements.items():
        page = page.replace("{{" + cle + "}}", valeur)

    shutil.rmtree(SORTIE, ignore_errors=True)
    os.makedirs(SORTIE)
    with open(os.path.join(SORTIE, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    shutil.copy(chemin("site", "style.css"), SORTIE)

    texte = [f"## Site du club, {date_fr(jour)}", f"Source des matchs : `{source}`",
             f"**{len(a_venir)}** match(s) à venir, **{len(resultats)}** résultat(s) récent(s)."]
    texte += [f"- {date_fr(m['jour'])} · {m.get('equipe')} contre {m.get('adversaire')}" for m in a_venir]
    if normaliser(os.environ.get("PUBLIER_SITE")) != "oui":
        texte.append("> Page construite mais **non publiée** : passez la variable PUBLIER_SITE à « oui » "
                     "et activez GitHub Pages pour la mettre en ligne.")
    resume("\n\n".join(texte))


if __name__ == "__main__":
    main()
