"""Partie 8 — api.py (FastAPI)"""

import pytest
from fastapi.testclient import TestClient

from nba_tracker import api

CORPS = {"date": "2026-01-05", "joueur": "Amara Diallo", "equipe": "Lions",
         "minutes": 34, "points": 28, "rebonds": 7, "passes": 5}


@pytest.fixture()
def client():
    api.reinitialiser()  # base vide avant CHAQUE test : les tests restent indépendants
    return TestClient(api.app)


def test_creer_puis_lire(client):
    reponse = client.post("/performances", json=CORPS)
    assert reponse.status_code == 201
    cree = reponse.json()
    assert cree["id"] == 1 and cree["points"] == 28
    lecture = client.get(f"/performances/{cree['id']}")
    assert lecture.status_code == 200 and lecture.json() == cree


def test_lire_inexistant(client):
    assert client.get("/performances/999").status_code == 404


def test_lister_et_filtrer(client):
    client.post("/performances", json=CORPS)
    client.post("/performances", json=CORPS | {"joueur": "Chen Wei", "equipe": "Tigres"})
    assert len(client.get("/performances").json()) == 2
    filtre = client.get("/performances", params={"joueur": "chen wei"}).json()
    assert [p["joueur"] for p in filtre] == ["Chen Wei"]


@pytest.mark.parametrize("champ, valeur", [("minutes", 0), ("points", -1), ("date", "pas-une-date"), ("joueur", "")])
def test_validation_renvoie_422(client, champ, valeur):
    assert client.post("/performances", json=CORPS | {champ: valeur}).status_code == 422


def test_modifier(client):
    identifiant = client.post("/performances", json=CORPS).json()["id"]
    reponse = client.put(f"/performances/{identifiant}", json=CORPS | {"points": 40})
    assert reponse.status_code == 200
    assert reponse.json()["points"] == 40 and reponse.json()["id"] == identifiant
    assert client.put("/performances/999", json=CORPS).status_code == 404


def test_supprimer(client):
    identifiant = client.post("/performances", json=CORPS).json()["id"]
    assert client.delete(f"/performances/{identifiant}").status_code == 204
    assert client.get(f"/performances/{identifiant}").status_code == 404
    assert client.delete(f"/performances/{identifiant}").status_code == 404


def test_stats_joueur(client):
    client.post("/performances", json=CORPS | {"points": 20})
    client.post("/performances", json=CORPS | {"points": 30, "date": "2026-01-08"})
    reponse = client.get("/joueurs/amara diallo/stats")
    assert reponse.status_code == 200
    assert reponse.json() == {"joueur": "Amara Diallo", "matchs": 2, "points_moyens": 25.0,
                              "rebonds_moyens": 7.0, "passes_moyennes": 5.0}
    assert client.get("/joueurs/inconnu/stats").status_code == 404
