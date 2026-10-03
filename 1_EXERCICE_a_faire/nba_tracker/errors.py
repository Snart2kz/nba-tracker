"""Partie 4 — Exceptions personnalisées. À TOI de les écrire.

Cahier des charges (les tests de test_p4_chargement.py le vérifient) :

* TrackerError(Exception)          : erreur de base de l'application.
* DonneeInvalideError(TrackerError): __init__(self, raison: str, numero_ligne: int | None = None).
                                     Expose .raison et .numero_ligne ; str(erreur) contient la raison
                                     et, si connu, le numéro de ligne (ex. « ligne 7 : minutes illisibles »).
* FichierIntrouvableError(TrackerError): __init__(self, chemin: str) ; expose .chemin ; message « fichier introuvable : ... ».
* JoueurInconnuError(TrackerError) : __init__(self, nom: str) ; expose .nom ; message « joueur inconnu : ... ».

Le reste du projet importe ces quatre noms : tant qu'ils n'existent pas, presque tout échouera à l'import.
"""

from __future__ import annotations


class TrackerError(Exception):
    """TODO"""


class DonneeInvalideError(TrackerError):
    """TODO : ajouter __init__, .raison, .numero_ligne"""


class FichierIntrouvableError(TrackerError):
    """TODO : ajouter __init__ et .chemin"""


class JoueurInconnuError(TrackerError):
    """TODO : ajouter __init__ et .nom"""
