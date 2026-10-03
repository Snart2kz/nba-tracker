"""Parties 1 et 2 — utils.py"""

import logging

import pytest

from nba_tracker.utils import chronometre, moyenne, normaliser_nom, par_blocs, regrouper_par, top_n


@pytest.mark.parametrize(
    "brut, attendu",
    [
        ("  amara   DIALLO ", "Amara Diallo"),
        ("chen wei", "Chen Wei"),
        ("diego marín", "Diego Marín"),
        ("", ""),
    ],
)
def test_normaliser_nom(brut, attendu):
    assert normaliser_nom(brut) == attendu


def test_regrouper_par():
    assert regrouper_par(["a", "bb", "c", "dd", "eee"], len) == {1: ["a", "c"], 2: ["bb", "dd"], 3: ["eee"]}


def test_regrouper_par_vide():
    assert regrouper_par([], len) == {}


def test_top_n_ordre_et_egalites():
    scores = {"b": 10, "a": 10, "c": 5, "d": 20}
    assert top_n(scores, 3) == [("d", 20), ("a", 10), ("b", 10)]


def test_top_n_plus_grand_que_les_donnees():
    assert top_n({"a": 1}, 5) == [("a", 1)]


def test_par_blocs_est_un_generateur():
    blocs = par_blocs([1, 2, 3, 4, 5], 2)
    assert iter(blocs) is blocs  # un générateur est son propre itérateur (une liste ne l'est pas)
    assert list(blocs) == [[1, 2], [3, 4], [5]]


def test_par_blocs_taille_invalide():
    with pytest.raises(ValueError):
        list(par_blocs([1, 2], 0))  # l'erreur n'apparaît qu'au parcours : le corps d'un générateur est paresseux


def test_moyenne():
    assert moyenne(10, 20, 30) == 20.0
    assert moyenne() == 0.0
    assert moyenne(1, 2, 2, arrondi=1) == 1.7


def test_chronometre_conserve_nom_doc_et_resultat(caplog):
    @chronometre
    def additionner(a, b):
        """Additionne."""
        return a + b

    with caplog.at_level(logging.INFO):
        assert additionner(2, b=3) == 5
    assert additionner.__name__ == "additionner"
    assert additionner.__doc__ == "Additionne."
    assert "additionner" in caplog.text


def test_chronometre_journalise_meme_en_cas_d_erreur(caplog):
    @chronometre
    def echoue():
        raise RuntimeError("boom")

    with caplog.at_level(logging.INFO):
        with pytest.raises(RuntimeError):
            echoue()
    assert "echoue" in caplog.text
