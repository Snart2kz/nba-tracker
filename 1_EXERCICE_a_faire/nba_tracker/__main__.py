"""Partie 5 — Point d'entrée : `python -m nba_tracker data/matchs.csv`."""
from __future__ import annotations
import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path
from .errors import FichierIntrouvableError
from .exporteurs import ExporteurJSON, ExporteurTexte
from .loader import charger_csv
from .stats import classement, construire_joueurs

def main(argv: Sequence[str] | None=None) -> int:
    """Interface en ligne de commande. Renvoie le code de sortie (0 = succès, 1 = fichier introuvable).

    Options : `fichier` (positionnel), `--top N` (défaut 3), `--format {texte,json}` (défaut texte),
    `--verbose` (affiche les durées journalisées par @chronometre).
    Les lignes rejetées sont listées sur stderr ("N ligne(s) rejetée(s)") ; stdout ne contient que le résultat
    (format json : uniquement le JSON).
    """
    raise NotImplementedError('TODO : à implémenter')
if __name__ == '__main__':
    raise SystemExit(main())
