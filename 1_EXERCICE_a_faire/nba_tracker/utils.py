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
T = TypeVar('T')
K = TypeVar('K')
logger = logging.getLogger(__name__)

def normaliser_nom(nom: str) -> str:
    """Nettoie un nom : espaces superflus supprimés, majuscule à chaque mot.

    >>> normaliser_nom("  amara   DIALLO ")
    'Amara Diallo'
    """
    mots = nom.strip().split()
    mots_cleared = [n.capitalize() for n in mots]
    return " ".join(mots_cleared)

def regrouper_par(elements: Iterable[T], cle: Callable[[T], K]) -> dict[K, list[T]]:
    """Regroupe les éléments dans un dict {cle(element): [éléments...]}, ordre d'apparition conservé.

    >>> regrouper_par(["a", "bb", "c"], len)
    {1: ['a', 'c'], 2: ['bb']}
    """

def top_n(scores: dict[str, float], n: int) -> list[tuple[str, float]]:
    """Les `n` meilleurs couples (nom, score) : score décroissant, puis nom croissant si égalité."""
    raise NotImplementedError('TODO : à implémenter')

def par_blocs(sequence: Sequence[T], taille: int) -> Iterator[Sequence[T]]:
    """Générateur : découpe `sequence` en blocs consécutifs de `taille` éléments (le dernier peut être plus court).

    Lève ValueError si `taille` <= 0 (au premier parcours, pas à l'appel : c'est un générateur).
    """
    raise NotImplementedError('TODO : à implémenter')

def moyenne(*valeurs: float, arrondi: int=2) -> float:
    """Moyenne arrondie de toutes les valeurs passées en arguments ; 0.0 si aucune valeur.

    >>> moyenne(10, 20, 30)
    20.0
    """
    raise NotImplementedError('TODO : à implémenter')

def chronometre(fonction: Callable[..., T]) -> Callable[..., T]:
    """Décorateur : journalise (niveau INFO) la durée d'exécution, même si la fonction lève une exception.

    Doit préserver le nom et la docstring de la fonction décorée.
    """
    raise NotImplementedError('TODO : à implémenter')
