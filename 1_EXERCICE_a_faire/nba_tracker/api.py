"""Partie 8 — Mini API CRUD avec FastAPI (stockage en mémoire)."""
from __future__ import annotations
import datetime as dt
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from .errors import JoueurInconnuError
from .models import Joueur, Performance
from .utils import normaliser_nom
app = FastAPI(title='NBA Tracker API')

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
_depot: dict[int, PerformanceOut] = {}

def reinitialiser() -> None:
    """Vide le stockage (utile pour isoler les tests)."""
    raise NotImplementedError('TODO : à implémenter')

def _prochain_id() -> int:
    """Plus grand identifiant existant + 1 (1 si le dépôt est vide)."""
    raise NotImplementedError('TODO : à implémenter')

def _ou_404(perf_id: int) -> PerformanceOut:
    """Renvoie la performance ou lève HTTPException 404."""
    raise NotImplementedError('TODO : à implémenter')

@app.post('/performances', response_model=PerformanceOut, status_code=status.HTTP_201_CREATED)
def creer(donnees: PerformanceIn) -> PerformanceOut:
    """Crée une performance (id automatique) et la renvoie avec le code 201."""
    raise NotImplementedError('TODO : à implémenter')

@app.get('/performances', response_model=list[PerformanceOut])
def lister(joueur: str | None=None) -> list[PerformanceOut]:
    """Liste toutes les performances ; `?joueur=` filtre sur le nom (insensible à la casse/aux espaces)."""
    raise NotImplementedError('TODO : à implémenter')

@app.get('/performances/{perf_id}', response_model=PerformanceOut)
def lire(perf_id: int) -> PerformanceOut:
    """Renvoie une performance, ou 404."""
    raise NotImplementedError('TODO : à implémenter')

@app.put('/performances/{perf_id}', response_model=PerformanceOut)
def remplacer(perf_id: int, donnees: PerformanceIn) -> PerformanceOut:
    """Remplace entièrement une performance existante (même id), ou 404."""
    raise NotImplementedError('TODO : à implémenter')

@app.delete('/performances/{perf_id}', status_code=status.HTTP_204_NO_CONTENT)
def supprimer(perf_id: int) -> None:
    """Supprime une performance (204 sans corps), ou 404 si elle n'existe pas."""
    raise NotImplementedError('TODO : à implémenter')

@app.get('/joueurs/{nom}/stats')
def stats_joueur(nom: str) -> dict[str, object]:
    """Stats agrégées d'un joueur via la classe `Joueur` :
    {"joueur", "matchs", "points_moyens", "rebonds_moyens", "passes_moyennes"}. 404 si aucune donnée.
    """
    raise NotImplementedError('TODO : à implémenter')
