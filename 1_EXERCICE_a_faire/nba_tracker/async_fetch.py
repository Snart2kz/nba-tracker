"""Partie 7 — Programmation asynchrone (asyncio) : attendre plusieurs I/O en parallèle."""
from __future__ import annotations
import asyncio
from collections.abc import Sequence

async def recuperer_stats(nom: str, delai: float=0.2) -> dict[str, str]:
    """Simule un appel réseau de `delai` secondes (asyncio.sleep) et renvoie
    {"joueur": nom, "source": "api-simulee"}.
    """
    raise NotImplementedError('TODO : à implémenter')

async def recuperer_tous(noms: Sequence[str], delai: float=0.2) -> list[dict[str, str]]:
    """Récupère les stats de tous les `noms` CONCURREMMENT (durée ≈ un seul délai, pas la somme).

    Les résultats sont renvoyés dans le même ordre que `noms`.
    """
    raise NotImplementedError('TODO : à implémenter')

async def recuperer_avec_timeout(nom: str, delai: float, timeout: float) -> dict[str, str] | None:
    """Comme `recuperer_stats`, mais renvoie None si l'appel dépasse `timeout` secondes."""
    raise NotImplementedError('TODO : à implémenter')
