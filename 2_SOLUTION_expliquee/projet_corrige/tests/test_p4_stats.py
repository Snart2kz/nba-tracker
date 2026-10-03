"""Partie 4 (suite) — stats.py"""

import pytest

from nba_tracker.loader import charger_csv
from nba_tracker.stats import classement, construire_joueurs, forme_recente, stats_par_equipe


@pytest.fixture(scope="module")
def performances(chemin_csv):
    return charger_csv(chemin_csv)[0]


@pytest.fixture(scope="module")
def joueurs(performances):
    return construire_joueurs(performances)


def test_construire_joueurs(joueurs):
    assert sorted(joueurs) == ["Amara Diallo", "Bruno Kessler", "Chen Wei", "Diego Marín"]
    assert len(joueurs["Amara Diallo"]) == 5
    assert len(joueurs["Diego Marín"]) == 4


def test_moyennes(joueurs):
    assert joueurs["Amara Diallo"].points_moyens == 29.6
    assert joueurs["Bruno Kessler"].points_moyens == 17.4
    assert joueurs["Diego Marín"].points_moyens == 16.25


def test_classement_par_defaut(joueurs):
    assert classement(joueurs) == [("Amara Diallo", 29.6), ("Chen Wei", 26.6), ("Bruno Kessler", 17.4)]


@pytest.mark.parametrize(
    "critere, premier",
    [("points_moyens", "Amara Diallo"), ("rebonds_moyens", "Chen Wei"), ("passes_moyennes", "Diego Marín")],
)
def test_classement_selon_le_critere(joueurs, critere, premier):
    assert classement(joueurs, critere, n=1)[0][0] == premier


def test_classement_critere_inconnu(joueurs):
    with pytest.raises(ValueError):
        classement(joueurs, "vitesse")


def test_stats_par_equipe(performances):
    assert stats_par_equipe(performances) == {
        "Lions": {"performances": 10, "points_moyens": 23.5},
        "Tigres": {"performances": 9, "points_moyens": 22.0},
    }


def test_forme_recente(joueurs):
    assert forme_recente(joueurs["Amara Diallo"], fenetre=3) == 28.33  # 22, 30, 33
    assert forme_recente(joueurs["Amara Diallo"], fenetre=100) == 29.6  # fenêtre > nb de matchs


def test_forme_recente_fenetre_invalide(joueurs):
    with pytest.raises(ValueError):
        forme_recente(joueurs["Amara Diallo"], fenetre=0)
