"""Partie 5 — __main__.py (point d'entrée en ligne de commande)"""

import json

from nba_tracker.__main__ import main


def test_cli_format_texte(chemin_csv, capsys):
    code = main([str(chemin_csv), "--top", "2"])
    sortie = capsys.readouterr()  # capsys capture ce qui est imprimé
    assert code == 0
    assert "Amara Diallo" in sortie.out
    assert "Top 2" in sortie.out
    assert "6 ligne(s) rejetée(s)" in sortie.err  # les diagnostics vont sur stderr


def test_cli_format_json_est_du_json_pur(chemin_csv, capsys):
    assert main([str(chemin_csv), "--format", "json"]) == 0
    donnees = json.loads(capsys.readouterr().out)
    assert len(donnees) == 4


def test_cli_fichier_introuvable(tmp_path, capsys):
    assert main([str(tmp_path / "absent.csv")]) == 1
    assert "introuvable" in capsys.readouterr().err
