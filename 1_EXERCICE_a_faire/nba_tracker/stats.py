"""Partie 4 (suite) — agrégations : on assemble utils + modèles."""
from __future__ import annotations
from collections.abc import Iterable, Mapping
from .models import Joueur, Performance
from .utils import moyenne, regrouper_par, top_n
CRITERES = ('points_moyens', 'rebonds_moyens', 'passes_moyennes')

def construire_joueurs(performances: Iterable[Performance]) -> dict[str, Joueur]:
    """Regroupe les performances par joueur : {nom normalisé: Joueur}. Réutilise `regrouper_par`."""
    raise NotImplementedError('TODO : à implémenter')

def classement(joueurs: Mapping[str, Joueur], critere: str='points_moyens', n: int=3) -> list[tuple[str, float]]:
    """Les `n` meilleurs joueurs selon `critere` (l'un de CRITERES) : liste de (nom, valeur).

    Critère inconnu -> ValueError. Réutilise `top_n`.
    """
    raise NotImplementedError('TODO : à implémenter')

def stats_par_equipe(performances: Iterable[Performance]) -> dict[str, dict[str, float]]:
    """{equipe: {"performances": nombre de lignes, "points_moyens": moyenne des points}}."""
    raise NotImplementedError('TODO : à implémenter')

def forme_recente(joueur: Joueur, fenetre: int=3) -> float:
    """Moyenne des points sur les `fenetre` matchs les plus récents (par date). ValueError si fenetre <= 0."""
    raise NotImplementedError('TODO : à implémenter')
