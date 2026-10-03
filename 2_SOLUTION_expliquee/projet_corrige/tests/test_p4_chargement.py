"""Partie 4 — errors.py et loader.py"""

import pytest

from nba_tracker.errors import DonneeInvalideError, FichierIntrouvableError, JoueurInconnuError, TrackerError
from nba_tracker.loader import charger_csv
from nba_tracker.models import Performance


def test_hierarchie_des_erreurs():
    for classe in (DonneeInvalideError, FichierIntrouvableError, JoueurInconnuError):
        assert issubclass(classe, TrackerError)


def test_donnee_invalide_expose_ses_attributs():
    erreur = DonneeInvalideError("minutes illisibles", numero_ligne=7)
    assert erreur.raison == "minutes illisibles"
    assert erreur.numero_ligne == 7
    assert "7" in str(erreur) and "minutes illisibles" in str(erreur)


def test_donnee_invalide_sans_numero_de_ligne():
    erreur = DonneeInvalideError("vide")
    assert erreur.numero_ligne is None
    assert "vide" in str(erreur)


def test_charger_csv_complet(chemin_csv):
    performances, rejets = charger_csv(chemin_csv)
    assert len(performances) == 19
    assert len(rejets) == 6
    assert all(isinstance(p, Performance) for p in performances)


def test_charger_csv_numeros_de_ligne_des_rejets(chemin_csv):
    _, rejets = charger_csv(chemin_csv)
    assert [r.numero_ligne for r in rejets] == [11, 12, 17, 18, 20, 26]


def test_charger_csv_detecte_le_doublon(chemin_csv):
    _, rejets = charger_csv(chemin_csv)
    assert "doublon" in rejets[-1].raison


def test_charger_csv_accepte_str_et_path(chemin_csv):
    assert charger_csv(chemin_csv) == charger_csv(str(chemin_csv))


def test_charger_csv_fichier_introuvable(tmp_path):
    with pytest.raises(FichierIntrouvableError):
        charger_csv(tmp_path / "absent.csv")


def test_charger_csv_minimal(tmp_path):
    fichier = tmp_path / "mini.csv"  # tmp_path : dossier temporaire fourni par pytest
    fichier.write_text(
        "date,joueur,equipe,minutes,points,rebonds,passes\n2026-02-01,test joueur,Lions,20,10,2,1\n",
        encoding="utf-8",
    )
    performances, rejets = charger_csv(fichier)
    assert rejets == []
    assert performances[0].joueur == "Test Joueur"
