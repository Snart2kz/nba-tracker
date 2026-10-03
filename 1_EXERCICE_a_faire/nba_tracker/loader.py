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

def charger_csv(chemin: str | Path) -> tuple[list[Performance], list[LigneRejetee]]:
    """Lit le CSV (UTF-8) et renvoie (performances valides, lignes rejetées).

    Une ligne invalide ne fait JAMAIS échouer le chargement : elle est rejetée avec sa raison.
    Une ligne dont le couple (date, joueur) a déjà été vu est rejetée avec une raison contenant « doublon »
    (la première occurrence est conservée). Fichier absent -> FichierIntrouvableError.
    

    Quand `chronometre` (Partie 2) fonctionne : décore cette fonction avec @chronometre.
    """
    raise NotImplementedError('TODO : à implémenter')
