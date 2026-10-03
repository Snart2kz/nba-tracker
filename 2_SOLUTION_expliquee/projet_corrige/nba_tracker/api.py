"""Partie 8 — Mini API CRUD avec FastAPI (stockage en mémoire)."""

from __future__ import annotations

import datetime as dt

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from .errors import JoueurInconnuError
from .models import Joueur, Performance
from .utils import normaliser_nom

app = FastAPI(title="NBA Tracker API")


class PerformanceIn(BaseModel):
    """Corps des requêtes POST/PUT. Pydantic valide types ET contraintes : erreur -> 422 automatique."""

    date: dt.date
    joueur: str = Field(min_length=1)
    equipe: str = Field(min_length=1)
    minutes: int = Field(ge=1, le=60)
    points: int = Field(ge=0)
    rebonds: int = Field(ge=0)
    passes: int = Field(ge=0)


class PerformanceOut(PerformanceIn):
    """Ce que l'API renvoie : les mêmes champs + l'identifiant."""

    id: int


_depot: dict[int, PerformanceOut] = {}  # « base de données » en mémoire


def reinitialiser() -> None:
    """Vide le stockage (utile pour isoler les tests)."""
    _depot.clear()


def _prochain_id() -> int:
    """Plus grand identifiant existant + 1 (1 si le dépôt est vide)."""
    return max(_depot, default=0) + 1


def _ou_404(perf_id: int) -> PerformanceOut:
    """Renvoie la performance ou lève HTTPException 404."""
    try:
        return _depot[perf_id]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"performance {perf_id} introuvable") from None


@app.post("/performances", response_model=PerformanceOut, status_code=status.HTTP_201_CREATED)
def creer(donnees: PerformanceIn) -> PerformanceOut:
    """Crée une performance (id automatique) et la renvoie avec le code 201."""
    performance = PerformanceOut(id=_prochain_id(), **donnees.model_dump())
    _depot[performance.id] = performance
    return performance


@app.get("/performances", response_model=list[PerformanceOut])
def lister(joueur: str | None = None) -> list[PerformanceOut]:
    """Liste toutes les performances ; `?joueur=` filtre sur le nom (insensible à la casse/aux espaces)."""
    performances = list(_depot.values())
    if joueur is not None:
        cible = normaliser_nom(joueur)
        performances = [p for p in performances if normaliser_nom(p.joueur) == cible]
    return performances


@app.get("/performances/{perf_id}", response_model=PerformanceOut)
def lire(perf_id: int) -> PerformanceOut:
    """Renvoie une performance, ou 404."""
    return _ou_404(perf_id)


@app.put("/performances/{perf_id}", response_model=PerformanceOut)
def remplacer(perf_id: int, donnees: PerformanceIn) -> PerformanceOut:
    """Remplace entièrement une performance existante (même id), ou 404."""
    _ou_404(perf_id)
    performance = PerformanceOut(id=perf_id, **donnees.model_dump())
    _depot[perf_id] = performance
    return performance


@app.delete("/performances/{perf_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer(perf_id: int) -> None:
    """Supprime une performance (204 sans corps), ou 404 si elle n'existe pas."""
    _ou_404(perf_id)
    del _depot[perf_id]


@app.get("/joueurs/{nom}/stats")
def stats_joueur(nom: str) -> dict[str, object]:
    """Stats agrégées d'un joueur via la classe `Joueur` :
    {"joueur", "matchs", "points_moyens", "rebonds_moyens", "passes_moyennes"}. 404 si aucune donnée.
    """
    cible = normaliser_nom(nom)
    joueur = Joueur(cible)
    for p in _depot.values():
        if normaliser_nom(p.joueur) == cible:
            joueur.ajouter(Performance(**p.model_dump(exclude={"id"})))  # ** : dict -> arguments nommés
    if len(joueur) == 0:
        raise HTTPException(status_code=404, detail=str(JoueurInconnuError(cible)))
    return {
        "joueur": joueur.nom,
        "matchs": len(joueur),
        "points_moyens": joueur.points_moyens,
        "rebonds_moyens": joueur.rebonds_moyens,
        "passes_moyennes": joueur.passes_moyennes,
    }
