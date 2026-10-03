"""Partie 6 — À TOI D'ÉCRIRE ces tests.

Pour chacun : retire le décorateur @pytest.mark.skip, écris le test, lance `pytest tests/test_p6_mes_tests.py`.
Inspire-toi des tests des autres fichiers (fixtures, parametrize, raises, tmp_path...).
"""

import pytest

ENTETE = "date,joueur,equipe,minutes,points,rebonds,passes\n"


@pytest.mark.skip(reason="TODO 6.1")
def test_points_par_minute_parametre(fabrique_perf):
    """6.1 — @pytest.mark.parametrize avec AU MOINS 4 cas sur `Performance.points_par_minute`,
    dont un cas où le résultat n'est pas exact (10 pts en 30 min = 0.333...) -> utilise pytest.approx."""


@pytest.mark.skip(reason="TODO 6.2")
def test_charger_csv_entete_seul(tmp_path):
    """6.2a — Un CSV qui ne contient que l'en-tête donne ([], []) : écris-le avec tmp_path.
    6.2b — (ajoute un 2e test) Deux lignes, même joueur/même date -> 1 performance (la première) + 1 rejet « doublon »,
    numéro de ligne 3."""


@pytest.mark.skip(reason="TODO 6.3")
def test_classement_egalite_ordre_alphabetique(fabrique_perf):
    """6.3 — Deux joueurs ayant exactement la même moyenne de points doivent être classés par ordre alphabétique.
    Construis les données avec la fixture `fabrique_perf` + `construire_joueurs`, puis appelle `classement`."""
