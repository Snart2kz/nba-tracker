"""Partie 4 — Lecture du CSV avec gestion d'erreurs et annotations de types."""

from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass
from pathlib import Path

from .errors import DonneeInvalideError, FichierIntrouvableError
from .models import Performance
from .utils import chronometre


@dataclass(frozen=True)
class LigneRejetee:
    """Une ligne du CSV écartée, avec le numéro de ligne dans le fichier (l'en-tête est la ligne 1)."""

    numero_ligne: int
    raison: str


@chronometre
def charger_csv(chemin: str | Path) -> tuple[list[Performance], list[LigneRejetee]]:
    """Lit le CSV (UTF-8) et renvoie (performances valides, lignes rejetées).

    Une ligne invalide ne fait JAMAIS échouer le chargement : elle est rejetée avec sa raison.
    Une ligne dont le couple (date, joueur) a déjà été vu est rejetée avec une raison contenant « doublon »
    (la première occurrence est conservée). Fichier absent -> FichierIntrouvableError.
    """
    chemin = Path(chemin)  # accepte str ET Path
    performances: list[Performance] = []
    rejets: list[LigneRejetee] = []
    vus: set[tuple[dt.date, str]] = set()  # un set : test d'appartenance en O(1)

    try:
        with chemin.open(encoding="utf-8", newline="") as fichier:  # `with` ferme le fichier quoi qu'il arrive
            lecteur = csv.DictReader(fichier)
            for numero, ligne in enumerate(lecteur, start=2):  # start=2 : la ligne 1 est l'en-tête
                try:
                    performance = Performance.depuis_ligne(ligne)
                except DonneeInvalideError as erreur:
                    rejets.append(LigneRejetee(numero, erreur.raison))
                else:  # else = « si le try a réussi » : garde le try minimal
                    cle = (performance.date, performance.joueur)
                    if cle in vus:
                        rejets.append(LigneRejetee(numero, "doublon (même joueur, même date)"))
                    else:
                        vus.add(cle)
                        performances.append(performance)
    except FileNotFoundError as exc:
        # `from exc` conserve la cause d'origine dans le traceback
        raise FichierIntrouvableError(str(chemin)) from exc

    return performances, rejets
