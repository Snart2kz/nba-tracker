"""Partie 3 — models.py et exporteurs.py"""

import dataclasses
import datetime as dt
import json

import pytest

from nba_tracker.errors import DonneeInvalideError
from nba_tracker.exporteurs import Exporteur, ExporteurJSON, ExporteurTexte
from nba_tracker.models import Joueur, Performance

LIGNE = {"date": "2026-01-05", "joueur": " amara diallo ", "equipe": "Lions",
         "minutes": "34", "points": "28", "rebonds": "7", "passes": "5"}


def test_performance_normalise_les_noms(fabrique_perf):
    p = fabrique_perf(joueur="  amara diallo ", equipe="lions")
    assert (p.joueur, p.equipe) == ("Amara Diallo", "Lions")


def test_performance_est_immuable(fabrique_perf):
    p = fabrique_perf()
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.points = 99


@pytest.mark.parametrize(
    "champ, valeur",
    [("minutes", 0), ("minutes", 61), ("points", -1), ("rebonds", -3), ("passes", -1), ("joueur", "   ")],
)
def test_performance_refuse_les_valeurs_invalides(fabrique_perf, champ, valeur):
    with pytest.raises(DonneeInvalideError):
        fabrique_perf(**{champ: valeur})


def test_points_par_minute(fabrique_perf):
    assert fabrique_perf(minutes=20, points=30).points_par_minute == 1.5


def test_depuis_ligne_ok():
    p = Performance.depuis_ligne(LIGNE)
    assert p.date == dt.date(2026, 1, 5)
    assert p.joueur == "Amara Diallo"
    assert (p.minutes, p.points, p.rebonds, p.passes) == (34, 28, 7, 5)


@pytest.mark.parametrize(
    "modif",
    [{"minutes": ""}, {"minutes": "abc"}, {"date": "2026-13-40"}, {"points": "-4"}, {"minutes": None}],
)
def test_depuis_ligne_valeurs_invalides(modif):
    with pytest.raises(DonneeInvalideError):
        Performance.depuis_ligne(LIGNE | modif)


def test_depuis_ligne_colonne_manquante():
    with pytest.raises(DonneeInvalideError, match="colonne manquante"):
        Performance.depuis_ligne({"date": "2026-01-05"})


def test_joueur_agrege_ses_performances(fabrique_perf):
    j = Joueur("amara diallo")
    j.ajouter(fabrique_perf(points=20, rebonds=4, passes=2, jour="2026-01-05"))
    j.ajouter(fabrique_perf(points=30, rebonds=8, passes=6, jour="2026-01-08"))
    assert j.nom == "Amara Diallo"
    assert len(j) == 2
    assert (j.points_moyens, j.rebonds_moyens, j.passes_moyennes) == (25.0, 6.0, 4.0)
    assert j.meilleur_match.points == 30
    assert repr(j) == "Joueur('Amara Diallo', matchs=2)"


def test_joueur_sans_match():
    j = Joueur("Nouveau Joueur")
    assert j.points_moyens == 0.0
    assert j.meilleur_match is None


def test_joueur_refuse_la_performance_d_un_autre(fabrique_perf):
    with pytest.raises(DonneeInvalideError):
        Joueur("Amara Diallo").ajouter(fabrique_perf(joueur="Chen Wei"))


def test_joueur_encapsulation(fabrique_perf):
    j = Joueur("Amara Diallo")
    j.ajouter(fabrique_perf())
    assert isinstance(j.performances, tuple)
    with pytest.raises(AttributeError):  # propriété sans setter
        j.performances = ()


@pytest.fixture()
def joueurs(fabrique_perf):
    a = Joueur("Amara Diallo")
    a.ajouter(fabrique_perf(points=30))
    c = Joueur("Chen Wei")
    c.ajouter(fabrique_perf(joueur="Chen Wei", equipe="Tigres", points=20))
    return [c, a]  # volontairement dans le désordre


def test_exporteur_est_abstrait():
    with pytest.raises(TypeError):
        Exporteur()


def test_exporteur_texte(joueurs):
    lignes = ExporteurTexte().exporter(joueurs).splitlines()
    assert len(lignes) == 2
    assert lignes[0].startswith("Amara Diallo")  # trié par nom
    assert "30.0" in lignes[0]


def test_exporteur_json(joueurs):
    donnees = json.loads(ExporteurJSON().exporter(joueurs))
    assert [d["joueur"] for d in donnees] == ["Amara Diallo", "Chen Wei"]
    assert donnees[0]["points_moyens"] == 30.0
    assert donnees[0]["matchs"] == 1


@pytest.mark.parametrize("classe", [ExporteurTexte, ExporteurJSON])
def test_polymorphisme(classe, joueurs):
    exporteur = classe()
    assert isinstance(exporteur, Exporteur)
    assert isinstance(exporteur.exporter(joueurs), str)
