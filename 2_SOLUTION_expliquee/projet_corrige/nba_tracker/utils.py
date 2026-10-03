"""Parties 1 et 2 — fonctions utilitaires génériques.

Aucune dépendance vers le reste du projet : ces fonctions se réutilisent telles quelles ailleurs.
"""

from __future__ import annotations

import functools
import logging
import time
from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import TypeVar

T = TypeVar("T")
K = TypeVar("K")

logger = logging.getLogger(__name__)


def normaliser_nom(nom: str) -> str:
    """Nettoie un nom : espaces superflus supprimés, majuscule à chaque mot.

    >>> normaliser_nom("  amara   DIALLO ")
    'Amara Diallo'
    """
    # split() sans argument coupe sur tout blanc ET ignore les blancs multiples ou de bord
    return " ".join(nom.split()).title()


def regrouper_par(elements: Iterable[T], cle: Callable[[T], K]) -> dict[K, list[T]]:
    """Regroupe les éléments dans un dict {cle(element): [éléments...]}, ordre d'apparition conservé.

    >>> regrouper_par(["a", "bb", "c"], len)
    {1: ['a', 'c'], 2: ['bb']}
    """
    # defaultdict(list) crée la liste vide à la première apparition d'une clé
    groupes: defaultdict[K, list[T]] = defaultdict(list)
    for element in elements:
        groupes[cle(element)].append(element)
    return dict(groupes)  # dict « normal » : lire une clé absente lèvera KeyError, sans la créer


def top_n(scores: dict[str, float], n: int) -> list[tuple[str, float]]:
    """Les `n` meilleurs couples (nom, score) : score décroissant, puis nom croissant si égalité."""
    # Clé de tri = tuple : -score trie en décroissant, nom en croissant. [:n] tolère n > len.
    return sorted(scores.items(), key=lambda couple: (-couple[1], couple[0]))[:n]


def par_blocs(sequence: Sequence[T], taille: int) -> Iterator[Sequence[T]]:
    """Générateur : découpe `sequence` en blocs consécutifs de `taille` éléments (le dernier peut être plus court).

    Lève ValueError si `taille` <= 0 (au premier parcours, pas à l'appel : c'est un générateur).
    """
    if taille <= 0:
        raise ValueError(f"taille doit être > 0, reçu {taille}")
    for debut in range(0, len(sequence), taille):
        yield sequence[debut : debut + taille]  # yield = on rend un bloc puis on se met en pause


def moyenne(*valeurs: float, arrondi: int = 2) -> float:
    """Moyenne arrondie de toutes les valeurs passées en arguments ; 0.0 si aucune valeur.

    >>> moyenne(10, 20, 30)
    20.0
    """
    if not valeurs:
        return 0.0
    return round(sum(valeurs) / len(valeurs), arrondi)


def chronometre(fonction: Callable[..., T]) -> Callable[..., T]:
    """Décorateur : journalise (niveau INFO) la durée d'exécution, même si la fonction lève une exception.

    Doit préserver le nom et la docstring de la fonction décorée.
    """

    @functools.wraps(fonction)  # recopie __name__, __doc__... sur le wrapper
    def wrapper(*args: object, **kwargs: object) -> T:
        debut = time.perf_counter()
        try:
            return fonction(*args, **kwargs)
        finally:  # exécuté dans TOUS les cas : retour normal ou exception
            duree = time.perf_counter() - debut
            logger.info("%s a pris %.4f s", fonction.__name__, duree)

    return wrapper
