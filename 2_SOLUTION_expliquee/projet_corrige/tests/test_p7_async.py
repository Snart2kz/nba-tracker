"""Partie 7 — async_fetch.py"""

import asyncio
import time

from nba_tracker.async_fetch import recuperer_avec_timeout, recuperer_stats, recuperer_tous


def test_recuperer_stats():
    assert asyncio.run(recuperer_stats("Chen Wei", delai=0)) == {"joueur": "Chen Wei", "source": "api-simulee"}


def test_recuperer_tous_est_concurrent_et_ordonne():
    noms = ["A", "B", "C", "D", "E"]
    debut = time.perf_counter()
    resultats = asyncio.run(recuperer_tous(noms, delai=0.2))
    duree = time.perf_counter() - debut
    assert [r["joueur"] for r in resultats] == noms
    assert duree < 0.6  # en séquentiel : 5 x 0.2 s = 1 s


def test_recuperer_avec_timeout():
    assert asyncio.run(recuperer_avec_timeout("A", delai=0.5, timeout=0.05)) is None
    assert asyncio.run(recuperer_avec_timeout("A", delai=0.01, timeout=1))["joueur"] == "A"
