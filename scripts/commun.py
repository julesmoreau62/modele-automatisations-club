"""Outils communs aux robots du club.

Dates à l'heure de Paris, lecture des tableaux, tickets GitHub, e-mails et mode essai.
Aucune dépendance à installer : uniquement la bibliothèque standard de Python.
"""
import csv
import json
import os
import re
import smtplib
import ssl
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime
from email.message import EmailMessage

try:
    from zoneinfo import ZoneInfo
    PARIS = ZoneInfo("Europe/Paris")
except Exception:  # Windows sans le paquet tzdata : on garde l'heure de l'ordinateur
    PARIS = None

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
NAVIGATEUR = "Mozilla/5.0 (compatible; robot-de-club; modele-automatisations-club)"


# ---------------------------------------------------------------- Dates

def maintenant():
    return datetime.now(PARIS) if PARIS else datetime.now()


def aujourdhui():
    """La date du jour à Paris, ou DATE_SIMULEE (AAAA-MM-JJ) pour faire un essai."""
    simulee = os.environ.get("DATE_SIMULEE", "").strip()
    if simulee:
        d = lire_date(simulee)
        if not d:
            raise SystemExit(f"DATE_SIMULEE illisible : {simulee!r}. Format attendu : AAAA-MM-JJ.")
        return d
    return maintenant().date()


def lire_date(texte):
    """Lit 15/11/2026, 2026-11-15 ou 15-11-2026. Renvoie None si la date est illisible."""
    texte = (texte or "").strip()
    for forme in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(texte, forme).date()
        except ValueError:
            pass
    return None


def date_fr(d, avec_jour=True):
    """samedi 1er novembre 2026"""
    texte = f"{d.day}{'er' if d.day == 1 else ''} {MOIS[d.month - 1]} {d.year}"
    return f"{JOURS[d.weekday()]} {texte}" if avec_jour else texte


def dans(jours):
    if jours == 0:
        return "aujourd'hui"
    if jours == 1:
        return "demain"
    return f"dans {jours} jours"


# ---------------------------------------------------------------- Textes et tableaux

def normaliser(texte):
    """Minuscules, sans accents : pour comparer « Trésorière » et « tresoriere »."""
    texte = unicodedata.normalize("NFD", (texte or "").lower())
    return "".join(c for c in texte if unicodedata.category(c) != "Mn").strip()


def chemin(*morceaux):
    return os.path.join(RACINE, *morceaux)


def lire_texte(fichier):
    with open(chemin(fichier), encoding="utf-8-sig") as f:
        return f.read()


def telecharger(adresse, limite=3_000_000):
    """Télécharge une page ou un fichier. Lève une erreur lisible en cas d'échec."""
    requete = urllib.request.Request(adresse, headers={"User-Agent": NAVIGATEUR})
    try:
        with urllib.request.urlopen(requete, timeout=30) as reponse:
            brut = reponse.read(limite)
            jeu = reponse.headers.get_content_charset() or "utf-8"
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"le site répond « erreur {e.code} »") from None
    except (urllib.error.URLError, TimeoutError) as e:
        raise RuntimeError(f"site injoignable ({getattr(e, 'reason', e)})") from None
    return brut.decode(jeu, errors="replace")


def lire_tableau(source):
    """Lit un tableau CSV, dans le dépôt ou à une adresse web, séparé par « ; » ou « , ».

    Les lignes vides et celles qui commencent par # sont ignorées.
    Chaque ligne devient un dictionnaire dont les clés sont les en-têtes, en minuscules.
    """
    if source.startswith(("http://", "https://")):
        texte = telecharger(source)
    else:
        texte = lire_texte(source)
    lignes = [l for l in texte.splitlines() if l.strip() and not l.lstrip().startswith("#")]
    if not lignes:
        return []
    separateur = ";" if lignes[0].count(";") >= lignes[0].count(",") else ","
    tableau = []
    for ligne in csv.DictReader(lignes, delimiter=separateur):
        tableau.append({normaliser(k or ""): (v or "").strip() for k, v in ligne.items()})
    return tableau


# ---------------------------------------------------------------- Résumé, tickets, e-mails

def mode_essai():
    """Tant que la variable MODE_ESSAI ne vaut pas « non », rien ne sort du dépôt."""
    return normaliser(os.environ.get("MODE_ESSAI", "")) != "non"


def resume(texte):
    """Écrit dans le résumé de l'exécution (onglet Actions), ou à l'écran sur un ordinateur."""
    fichier = os.environ.get("GITHUB_STEP_SUMMARY")
    if fichier:
        with open(fichier, "a", encoding="utf-8") as f:
            f.write(texte.rstrip() + "\n\n")
    else:
        print(texte.rstrip() + "\n")


def github(methode, route, donnees=None):
    """Appelle l'API de GitHub avec le jeton temporaire fourni à chaque exécution."""
    jeton = os.environ.get("GITHUB_TOKEN")
    if not jeton:
        raise RuntimeError("GITHUB_TOKEN absent : ce script doit tourner dans GitHub Actions.")
    corps = json.dumps(donnees).encode() if donnees is not None else None
    requete = urllib.request.Request(
        "https://api.github.com" + route, data=corps, method=methode,
        headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {jeton}",
                 "X-GitHub-Api-Version": "2022-11-28", "User-Agent": NAVIGATEUR})
    try:
        with urllib.request.urlopen(requete, timeout=30) as reponse:
            return json.loads(reponse.read() or b"null")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        raise RuntimeError(f"GitHub refuse la demande {methode} {route} : erreur {e.code}. {detail}") from None


def ouvrir_ticket(titre, corps):
    """Ouvre un ticket (onglet Issues) : les personnes qui suivent le dépôt sont prévenues.

    En mode essai, le ticket est seulement affiché dans le résumé de l'exécution.
    Un ticket ouvert portant déjà ce titre n'est pas recréé.
    """
    if mode_essai():
        resume(f"> **Mode essai** : ce ticket n'a pas été ouvert. Pour l'activer, "
               f"passez la variable MODE_ESSAI à « non ».\n\n### {titre}\n\n{corps}")
        return None
    depot = os.environ["GITHUB_REPOSITORY"]
    for ticket in github("GET", f"/repos/{depot}/issues?state=open&per_page=100"):
        if ticket.get("title") == titre:
            resume(f"Ticket déjà ouvert : [{titre}]({ticket['html_url']})")
            return ticket["html_url"]
    ticket = github("POST", f"/repos/{depot}/issues", {"title": titre, "body": corps})
    resume(f"Ticket ouvert : [{titre}]({ticket['html_url']})")
    return ticket["html_url"]


def contacts():
    """Le secret CONTACTS, une ligne par rôle : « Trésorier = tresorier@club.fr, autre@club.fr »."""
    carnet = {}
    for ligne in os.environ.get("CONTACTS", "").splitlines():
        if "=" in ligne:
            role, adresses = ligne.split("=", 1)
            carnet[normaliser(role)] = [a.strip() for a in re.split(r"[,;]", adresses) if a.strip()]
    return carnet


def envoyer_courriel(role, sujet, texte):
    """Envoie un e-mail aux adresses du rôle, si les secrets SMTP_* et CONTACTS sont réglés.

    Les adresses ne sont jamais écrites dans le journal : seulement leur nombre.
    """
    serveur = os.environ.get("SMTP_SERVEUR", "").strip()
    if not serveur:
        return
    adresses = contacts().get(normaliser(role)) or contacts().get("bureau") or []
    if not adresses:
        resume(f"E-mail non envoyé : aucune adresse pour le rôle « {role} » ni pour « Bureau » dans le secret CONTACTS.")
        return
    if mode_essai():
        resume(f"> **Mode essai** : e-mail « {sujet} » non envoyé ({len(adresses)} destinataire(s) prévu(s)).")
        return
    message = EmailMessage()
    message["Subject"] = sujet
    message["From"] = os.environ.get("SMTP_EXPEDITEUR") or os.environ.get("SMTP_UTILISATEUR")
    message["To"] = ", ".join(adresses)
    message.set_content(texte)
    port = int(os.environ.get("SMTP_PORT") or 465)
    contexte = ssl.create_default_context()
    if port == 465:
        connexion = smtplib.SMTP_SSL(serveur, port, context=contexte, timeout=30)
    else:
        connexion = smtplib.SMTP(serveur, port, timeout=30)
        connexion.starttls(context=contexte)
    with connexion:
        connexion.login(os.environ["SMTP_UTILISATEUR"], os.environ["SMTP_MOT_DE_PASSE"])
        connexion.send_message(message)
    resume(f"E-mail « {sujet} » envoyé ({len(adresses)} destinataire(s)).")
