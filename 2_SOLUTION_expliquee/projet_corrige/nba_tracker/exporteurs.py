"""Partie 3 (suite) — héritage, classe abstraite et polymorphisme."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections.abc import Iterable

from .models import Joueur


class Exporteur(ABC):
    """Contrat commun : toute sous-classe sait transformer des joueurs en texte. Non instanciable."""

    @abstractmethod
    def exporter(self, joueurs: Iterable[Joueur]) -> str:
        """Renvoie la représentation textuelle des joueurs, triés par nom."""


class ExporteurTexte(Exporteur):
    """Une ligne par joueur : nom, nombre de matchs, puis points/rebonds/passes moyens (1 décimale)."""

    def exporter(self, joueurs: Iterable[Joueur]) -> str:
        lignes = [
            f"{j.nom:<16} {len(j):>2} matchs | {j.points_moyens:>5.1f} pts"
            f" | {j.rebonds_moyens:>4.1f} reb | {j.passes_moyennes:>4.1f} pas"
            for j in sorted(joueurs, key=lambda j: j.nom)
        ]
        return "\n".join(lignes)


class ExporteurJSON(Exporteur):
    """Liste JSON d'objets {joueur, matchs, points_moyens, rebonds_moyens, passes_moyennes}, indentée."""

    def exporter(self, joueurs: Iterable[Joueur]) -> str:
        donnees = [
            {
                "joueur": j.nom,
                "matchs": len(j),
                "points_moyens": j.points_moyens,
                "rebonds_moyens": j.rebonds_moyens,
                "passes_moyennes": j.passes_moyennes,
            }
            for j in sorted(joueurs, key=lambda j: j.nom)
        ]
        return json.dumps(donnees, ensure_ascii=False, indent=2)  # ensure_ascii=False : garde « é »
