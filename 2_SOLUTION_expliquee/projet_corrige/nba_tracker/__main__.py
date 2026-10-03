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


def main(argv: Sequence[str] | None = None) -> int:
    """Interface en ligne de commande. Renvoie le code de sortie (0 = succès, 1 = fichier introuvable).

    Options : `fichier` (positionnel), `--top N` (défaut 3), `--format {texte,json}` (défaut texte),
    `--verbose` (affiche les durées journalisées par @chronometre).
    Les lignes rejetées sont listées sur stderr ("N ligne(s) rejetée(s)") ; stdout ne contient que le résultat
    (format json : uniquement le JSON).
    """
    parseur = argparse.ArgumentParser(prog="nba_tracker", description="Statistiques basket depuis un CSV.")
    parseur.add_argument("fichier", type=Path, help="chemin du CSV de matchs")
    parseur.add_argument("--top", type=int, default=3, help="taille du classement (défaut : 3)")
    parseur.add_argument("--format", choices=("texte", "json"), default="texte")
    parseur.add_argument("--verbose", action="store_true", help="affiche les durées d'exécution")
    args = parseur.parse_args(argv)  # argv=None -> lit sys.argv ; une liste -> pratique pour les tests

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    try:
        performances, rejets = charger_csv(args.fichier)
    except FichierIntrouvableError as erreur:
        print(f"Erreur : {erreur}", file=sys.stderr)
        return 1

    if rejets:
        print(f"{len(rejets)} ligne(s) rejetée(s) :", file=sys.stderr)
        for rejet in rejets:
            print(f"  - ligne {rejet.numero_ligne} : {rejet.raison}", file=sys.stderr)

    joueurs = construire_joueurs(performances)
    if args.format == "json":
        print(ExporteurJSON().exporter(joueurs.values()))
    else:
        print(ExporteurTexte().exporter(joueurs.values()))
        print(f"\nTop {args.top} (points moyens) :")
        for rang, (nom, score) in enumerate(classement(joueurs, n=args.top), start=1):
            print(f"{rang}. {nom} — {score:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
