"""Partie 6 — Exemples d'écriture de tests : fixtures, parametrize, approx, tmp_path, raises."""

import pytest

from nba_tracker.loader import charger_csv
from nba_tracker.stats import classement, construire_joueurs

ENTETE = "date,joueur,equipe,minutes,points,rebonds,passes\n"


@pytest.mark.parametrize(
    "minutes, points, attendu",
    [(20, 30, 1.5), (30, 10, 1 / 3), (48, 0, 0.0), (1, 5, 5.0)],
)
def test_points_par_minute_parametre(fabrique_perf, minutes, points, attendu):
    # approx : compare des flottants sans piège d'arrondi (1/3 n'est pas exact en binaire)
    assert fabrique_perf(minutes=minutes, points=points).points_par_minute == pytest.approx(attendu)


def test_charger_csv_entete_seul(tmp_path):
    fichier = tmp_path / "vide.csv"
    fichier.write_text(ENTETE, encoding="utf-8")
    assert charger_csv(fichier) == ([], [])


def test_charger_csv_doublon_minimal(tmp_path):
    fichier = tmp_path / "doublon.csv"
    fichier.write_text(
        ENTETE + "2026-02-01,Test Joueur,Lions,20,10,2,1\n2026-02-01,test joueur,Lions,25,12,3,2\n",
        encoding="utf-8",
    )
    performances, rejets = charger_csv(fichier)
    assert len(performances) == 1 and performances[0].points == 10  # la première occurrence est gardée
    assert len(rejets) == 1 and rejets[0].numero_ligne == 3 and "doublon" in rejets[0].raison


def test_classement_egalite_ordre_alphabetique(fabrique_perf):
    performances = [
        fabrique_perf(joueur="Zoé Martin", points=20),
        fabrique_perf(joueur="Adam Roy", points=20),
    ]
    resultat = classement(construire_joueurs(performances), n=2)
    assert [nom for nom, _ in resultat] == ["Adam Roy", "Zoé Martin"]
