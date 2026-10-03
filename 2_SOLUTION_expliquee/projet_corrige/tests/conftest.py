"""Fixtures partagées par tous les fichiers de tests (pytest les découvre automatiquement)."""

import datetime as dt
from pathlib import Path

import pytest

from nba_tracker.models import Performance

RACINE = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def chemin_csv() -> Path:
    """Chemin du CSV d'exemple (calculé une seule fois pour toute la session de tests)."""
    return RACINE / "data" / "matchs.csv"


@pytest.fixture()
def fabrique_perf():
    """« Fabrique » : renvoie une fonction qui crée des Performance valides, modifiables par mot-clé."""

    def _creer(joueur="Amara Diallo", equipe="Lions", jour="2026-01-05",
               minutes=30, points=20, rebonds=5, passes=4):
        return Performance(date=dt.date.fromisoformat(jour), joueur=joueur, equipe=equipe,
                           minutes=minutes, points=points, rebonds=rebonds, passes=passes)

    return _creer
