"""Partie 4 (suite) — agrégations : on assemble utils + modèles."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from .models import Joueur, Performance
from .utils import moyenne, regrouper_par, top_n

CRITERES = ("points_moyens", "rebonds_moyens", "passes_moyennes")


def construire_joueurs(performances: Iterable[Performance]) -> dict[str, Joueur]:
    """Regroupe les performances par joueur : {nom normalisé: Joueur}. Réutilise `regrouper_par`."""
    joueurs: dict[str, Joueur] = {}
    for nom, perfs in regrouper_par(performances, lambda p: p.joueur).items():
        joueur = Joueur(nom)
        for perf in perfs:
            joueur.ajouter(perf)
        joueurs[nom] = joueur
    return joueurs


def classement(
    joueurs: Mapping[str, Joueur], critere: str = "points_moyens", n: int = 3
) -> list[tuple[str, float]]:
    """Les `n` meilleurs joueurs selon `critere` (l'un de CRITERES) : liste de (nom, valeur).

    Critère inconnu -> ValueError. Réutilise `top_n`.
    """
    if critere not in CRITERES:
        raise ValueError(f"critère inconnu : {critere!r} (attendu : {', '.join(CRITERES)})")
    scores = {nom: getattr(joueur, critere) for nom, joueur in joueurs.items()}  # getattr : attribut choisi par son nom
    return top_n(scores, n)


def stats_par_equipe(performances: Iterable[Performance]) -> dict[str, dict[str, float]]:
    """{equipe: {"performances": nombre de lignes, "points_moyens": moyenne des points}}."""
    groupes = regrouper_par(performances, lambda p: p.equipe)
    return {
        equipe: {"performances": len(perfs), "points_moyens": moyenne(*(p.points for p in perfs))}
        for equipe, perfs in groupes.items()
    }


def forme_recente(joueur: Joueur, fenetre: int = 3) -> float:
    """Moyenne des points sur les `fenetre` matchs les plus récents (par date). ValueError si fenetre <= 0."""
    if fenetre <= 0:
        # piège : liste[-0:] renvoie TOUTE la liste, pas une liste vide !
        raise ValueError(f"fenetre doit être > 0, reçu {fenetre}")
    recents = sorted(joueur.performances, key=lambda p: p.date)[-fenetre:]
    return moyenne(*(p.points for p in recents))
