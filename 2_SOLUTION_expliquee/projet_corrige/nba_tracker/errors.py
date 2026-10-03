"""Partie 4 — Exceptions personnalisées.

Une hiérarchie d'erreurs propre au projet permet de distinguer « mes » erreurs
(données invalides, fichier absent...) des bugs imprévus (TypeError, KeyError...).
"""

from __future__ import annotations


class TrackerError(Exception):
    """Erreur de base de l'application : `except TrackerError` attrape toutes les erreurs métier."""


class DonneeInvalideError(TrackerError):
    """Une donnée ne respecte pas les règles métier.

    Attributs : `raison` (str) et `numero_ligne` (int | None).
    `str(erreur)` doit contenir la raison, et le numéro de ligne s'il est connu.
    """

    def __init__(self, raison: str, numero_ligne: int | None = None) -> None:
        self.raison = raison
        self.numero_ligne = numero_ligne
        prefixe = f"ligne {numero_ligne} : " if numero_ligne is not None else ""
        super().__init__(f"{prefixe}{raison}")  # super().__init__ fixe le message affiché par str()


class FichierIntrouvableError(TrackerError):
    """Le fichier demandé n'existe pas. Attribut : `chemin` (str)."""

    def __init__(self, chemin: str) -> None:
        self.chemin = chemin
        super().__init__(f"fichier introuvable : {chemin}")


class JoueurInconnuError(TrackerError):
    """Aucune donnée pour ce joueur. Attribut : `nom` (str)."""

    def __init__(self, nom: str) -> None:
        self.nom = nom
        super().__init__(f"joueur inconnu : {nom}")
