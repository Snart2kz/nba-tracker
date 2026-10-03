"""Partie 3 — Programmation orientée objet : les modèles du domaine."""

from __future__ import annotations

import datetime as dt
from collections.abc import Mapping
from dataclasses import dataclass

from .errors import DonneeInvalideError
from .utils import moyenne, normaliser_nom

COLONNES = ("date", "joueur", "equipe", "minutes", "points", "rebonds", "passes")


@dataclass(frozen=True)  # frozen : immuable, comparable (==), hashable
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
        # Instance frozen : self.joueur = ... est interdit, on passe par object.__setattr__
        object.__setattr__(self, "joueur", normaliser_nom(self.joueur))
        object.__setattr__(self, "equipe", normaliser_nom(self.equipe))
        if not self.joueur:
            raise DonneeInvalideError("nom de joueur vide")
        if not 1 <= self.minutes <= 60:  # comparaison chaînée
            raise DonneeInvalideError(f"minutes hors plage (1-60) : {self.minutes}")
        for champ in ("points", "rebonds", "passes"):
            if getattr(self, champ) < 0:
                raise DonneeInvalideError(f"{champ} négatif : {getattr(self, champ)}")

    @property
    def points_par_minute(self) -> float:
        """Points marqués divisés par les minutes jouées."""
        return self.points / self.minutes

    @classmethod
    def depuis_ligne(cls, ligne: Mapping[str, str | None]) -> Performance:
        """Construit une Performance depuis une ligne de CSV (dict de chaînes, comme DictReader).

        Colonne absente -> DonneeInvalideError dont le message contient « colonne manquante » ;
        valeur illisible (date, entier) -> DonneeInvalideError. Les blancs autour des valeurs sont ignorés.
        """
        try:
            # `or ""` : DictReader met None quand une ligne est trop courte
            brut = {cle: (ligne[cle] or "").strip() for cle in COLONNES}
            return cls(
                date=dt.date.fromisoformat(brut["date"]),
                joueur=brut["joueur"],
                equipe=brut["equipe"],
                minutes=int(brut["minutes"]),
                points=int(brut["points"]),
                rebonds=int(brut["rebonds"]),
                passes=int(brut["passes"]),
            )
        except KeyError as exc:
            raise DonneeInvalideError(f"colonne manquante : {exc.args[0]}") from exc
        except ValueError as exc:  # int("abc"), date invalide... (DonneeInvalideError n'en hérite pas)
            raise DonneeInvalideError(f"valeur illisible : {exc}") from exc


class Joueur:
    """Un joueur et l'ensemble de ses performances (encapsulation : la liste reste privée)."""

    def __init__(self, nom: str) -> None:
        self.nom = normaliser_nom(nom)
        self._performances: list[Performance] = []  # « _ » = usage interne par convention

    def ajouter(self, performance: Performance) -> None:
        """Ajoute une performance ; DonneeInvalideError si elle appartient à un autre joueur."""
        if performance.joueur != self.nom:
            raise DonneeInvalideError(f"{performance.joueur} n'est pas {self.nom}")
        self._performances.append(performance)

    @property
    def performances(self) -> tuple[Performance, ...]:
        """Vue en lecture seule (tuple) des performances, sans setter."""
        return tuple(self._performances)

    def __len__(self) -> int:
        return len(self._performances)

    def __repr__(self) -> str:
        return f"Joueur({self.nom!r}, matchs={len(self)})"

    def _moyenne_de(self, champ: str) -> float:
        # expression génératrice : pas de liste intermédiaire ; * la « déballe » en arguments
        return moyenne(*(getattr(p, champ) for p in self._performances))

    @property
    def points_moyens(self) -> float:
        """Moyenne de points par match (0.0 sans match)."""
        return self._moyenne_de("points")

    @property
    def rebonds_moyens(self) -> float:
        """Moyenne de rebonds par match (0.0 sans match)."""
        return self._moyenne_de("rebonds")

    @property
    def passes_moyennes(self) -> float:
        """Moyenne de passes par match (0.0 sans match)."""
        return self._moyenne_de("passes")

    @property
    def meilleur_match(self) -> Performance | None:
        """La performance avec le plus de points, ou None sans match."""
        return max(self._performances, key=lambda p: p.points, default=None)
