"""Partie 3 — Programmation orientée objet : les modèles du domaine."""
from __future__ import annotations
import datetime as dt
from collections.abc import Mapping
from dataclasses import dataclass
from .errors import DonneeInvalideError
from .utils import moyenne, normaliser_nom
COLONNES = ('date', 'joueur', 'equipe', 'minutes', 'points', 'rebonds', 'passes')

@dataclass(frozen=True)
class Performance:
    """Stats d'un joueur sur un match.

    Règles : `joueur` et `equipe` sont normalisés (voir `normaliser_nom`) ; `joueur` non vide ;
    1 <= minutes <= 60 ; points, rebonds et passes >= 0. Sinon : DonneeInvalideError.
    """
    date: dt.date
    joueur: str
    equipe: str
    minutes: int
    points: int
    rebonds: int
    passes: int

    def __post_init__(self) -> None:
        raise NotImplementedError('TODO : à implémenter')

    @property
    def points_par_minute(self) -> float:
        """Points marqués divisés par les minutes jouées."""
        raise NotImplementedError('TODO : à implémenter')

    @classmethod
    def depuis_ligne(cls, ligne: Mapping[str, str | None]) -> Performance:
        """Construit une Performance depuis une ligne de CSV (dict de chaînes, comme DictReader).

        Colonne absente -> DonneeInvalideError dont le message contient « colonne manquante » ;
        valeur illisible (date, entier) -> DonneeInvalideError. Les blancs autour des valeurs sont ignorés.
        """
        raise NotImplementedError('TODO : à implémenter')

class Joueur:
    """Un joueur et l'ensemble de ses performances (encapsulation : la liste reste privée)."""

    def __init__(self, nom: str) -> None:
        raise NotImplementedError('TODO : à implémenter')

    def ajouter(self, performance: Performance) -> None:
        """Ajoute une performance ; DonneeInvalideError si elle appartient à un autre joueur."""
        raise NotImplementedError('TODO : à implémenter')

    @property
    def performances(self) -> tuple[Performance, ...]:
        """Vue en lecture seule (tuple) des performances, sans setter."""
        raise NotImplementedError('TODO : à implémenter')

    def __len__(self) -> int:
        raise NotImplementedError('TODO : à implémenter')

    def __repr__(self) -> str:
        raise NotImplementedError('TODO : à implémenter')

    def _moyenne_de(self, champ: str) -> float:
        raise NotImplementedError('TODO : à implémenter')

    @property
    def points_moyens(self) -> float:
        """Moyenne de points par match (0.0 sans match)."""
        raise NotImplementedError('TODO : à implémenter')

    @property
    def rebonds_moyens(self) -> float:
        """Moyenne de rebonds par match (0.0 sans match)."""
        raise NotImplementedError('TODO : à implémenter')

    @property
    def passes_moyennes(self) -> float:
        """Moyenne de passes par match (0.0 sans match)."""
        raise NotImplementedError('TODO : à implémenter')

    @property
    def meilleur_match(self) -> Performance | None:
        """La performance avec le plus de points, ou None sans match."""
        raise NotImplementedError('TODO : à implémenter')
