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
        raise NotImplementedError('TODO : à implémenter')

class ExporteurTexte(Exporteur):
    """Une ligne par joueur : nom, nombre de matchs, puis points/rebonds/passes moyens (1 décimale)."""

    def exporter(self, joueurs: Iterable[Joueur]) -> str:
        raise NotImplementedError('TODO : à implémenter')

class ExporteurJSON(Exporteur):
    """Liste JSON d'objets {joueur, matchs, points_moyens, rebonds_moyens, passes_moyennes}, indentée."""

    def exporter(self, joueurs: Iterable[Joueur]) -> str:
        raise NotImplementedError('TODO : à implémenter')
