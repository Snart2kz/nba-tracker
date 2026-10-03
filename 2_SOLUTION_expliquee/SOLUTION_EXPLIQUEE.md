# Solution expliquée — NBA Tracker (Python fondations)

> ⚠️ **À n'ouvrir qu'après avoir tenté l'exercice** (`1_EXERCICE_a_faire/README.md`).
> Ce fichier contient : le **contexte**, le **résultat** (code complet, testé), les **explications** partie par partie,
> puis **d'autres contextes** pour réutiliser ce que tu as appris.
> Le projet complet et exécutable est dans `projet_corrige/` (même dossier) : `pip install -e ".[dev]"` puis `pytest`.

---

## 0. Le contexte en 30 secondes

**Problème** : un CSV de performances de basket (fictif), sale et imparfait, doit être lu, validé, agrégé, classé et exporté ;
le tout lançable en ligne de commande, testé, capable d'appels parallèles, et exposé via une API.

**Architecture** — les flèches indiquent « dépend de » ; elles vont toujours dans le même sens (pas d'import circulaire) :

```
__main__ (CLI) ─┬─► loader ─────► models ─► utils
api (FastAPI) ──┤                   ▲
                ├─► stats ──────────┤        errors (utilisée partout)
                └─► exporteurs ─────┘
async_fetch (indépendant)
```

**Résultat obtenu** (`python -m nba_tracker data/matchs.csv --top 3`) :

```text
Amara Diallo      5 matchs |  29.6 pts |  8.0 reb |  4.6 pas
Bruno Kessler     5 matchs |  17.4 pts |  4.8 reb | 10.0 pas
Chen Wei          5 matchs |  26.6 pts |  9.8 reb |  3.8 pas
Diego Marín       4 matchs |  16.2 pts |  3.5 reb | 11.5 pas

Top 3 (points moyens) :
1. Amara Diallo — 29.6
2. Chen Wei — 26.6
3. Bruno Kessler — 17.4
```

Sur **stderr**, les 6 lignes écartées, chacune avec sa raison :

```text
6 ligne(s) rejetée(s) :
  - ligne 11 : valeur illisible : invalid literal for int() with base 10: ''
  - ligne 12 : points négatif : -4
  - ligne 17 : valeur illisible : month must be in 1..12
  - ligne 18 : valeur illisible : invalid literal for int() with base 10: 'abc'
  - ligne 20 : minutes hors plage (1-60) : 0
  - ligne 26 : doublon (même joueur, même date)
```

Qualité : `pytest` → **80 tests passent** · `mypy nba_tracker` → *no issues found in 10 source files* · les doctests de `utils.py` passent.

---

## 1. Syntaxe avancée & structures de données — `utils.py`

**Ce que tu devais comprendre** : nettoyer du texte, regrouper, trier avec plusieurs critères, produire des données au fil de l'eau (générateur).

**`nba_tracker/utils.py`**

```python
"""Parties 1 et 2 — fonctions utilitaires génériques.

Aucune dépendance vers le reste du projet : ces fonctions se réutilisent telles quelles ailleurs.
"""

from __future__ import annotations

import functools
import logging
import time
from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import TypeVar

T = TypeVar("T")
K = TypeVar("K")

logger = logging.getLogger(__name__)


def normaliser_nom(nom: str) -> str:
    """Nettoie un nom : espaces superflus supprimés, majuscule à chaque mot.

    >>> normaliser_nom("  amara   DIALLO ")
    'Amara Diallo'
    """
    # split() sans argument coupe sur tout blanc ET ignore les blancs multiples ou de bord
    return " ".join(nom.split()).title()


def regrouper_par(elements: Iterable[T], cle: Callable[[T], K]) -> dict[K, list[T]]:
    """Regroupe les éléments dans un dict {cle(element): [éléments...]}, ordre d'apparition conservé.

    >>> regrouper_par(["a", "bb", "c"], len)
    {1: ['a', 'c'], 2: ['bb']}
    """
    # defaultdict(list) crée la liste vide à la première apparition d'une clé
    groupes: defaultdict[K, list[T]] = defaultdict(list)
    for element in elements:
        groupes[cle(element)].append(element)
    return dict(groupes)  # dict « normal » : lire une clé absente lèvera KeyError, sans la créer


def top_n(scores: dict[str, float], n: int) -> list[tuple[str, float]]:
    """Les `n` meilleurs couples (nom, score) : score décroissant, puis nom croissant si égalité."""
    # Clé de tri = tuple : -score trie en décroissant, nom en croissant. [:n] tolère n > len.
    return sorted(scores.items(), key=lambda couple: (-couple[1], couple[0]))[:n]


def par_blocs(sequence: Sequence[T], taille: int) -> Iterator[Sequence[T]]:
    """Générateur : découpe `sequence` en blocs consécutifs de `taille` éléments (le dernier peut être plus court).

    Lève ValueError si `taille` <= 0 (au premier parcours, pas à l'appel : c'est un générateur).
    """
    if taille <= 0:
        raise ValueError(f"taille doit être > 0, reçu {taille}")
    for debut in range(0, len(sequence), taille):
        yield sequence[debut : debut + taille]  # yield = on rend un bloc puis on se met en pause


def moyenne(*valeurs: float, arrondi: int = 2) -> float:
    """Moyenne arrondie de toutes les valeurs passées en arguments ; 0.0 si aucune valeur.

    >>> moyenne(10, 20, 30)
    20.0
    """
    if not valeurs:
        return 0.0
    return round(sum(valeurs) / len(valeurs), arrondi)


def chronometre(fonction: Callable[..., T]) -> Callable[..., T]:
    """Décorateur : journalise (niveau INFO) la durée d'exécution, même si la fonction lève une exception.

    Doit préserver le nom et la docstring de la fonction décorée.
    """

    @functools.wraps(fonction)  # recopie __name__, __doc__... sur le wrapper
    def wrapper(*args: object, **kwargs: object) -> T:
        debut = time.perf_counter()
        try:
            return fonction(*args, **kwargs)
        finally:  # exécuté dans TOUS les cas : retour normal ou exception
            duree = time.perf_counter() - debut
            logger.info("%s a pris %.4f s", fonction.__name__, duree)

    return wrapper
```

*(Cette partie concerne `normaliser_nom`, `regrouper_par`, `top_n`, `par_blocs` ; la partie 2 concerne `moyenne` et `chronometre` — même fichier.)*

**Explications clés**
- `" ".join(nom.split())` : `split()` **sans argument** coupe sur tout blanc et ignore les blancs multiples ou de bord → nettoyage en une ligne.
- `defaultdict(list)` évite le classique `if cle not in d: d[cle] = []`. On renvoie `dict(groupes)` pour qu'un accès à une clé absente lève `KeyError` au lieu de créer la clé silencieusement.
- **Tri multi-critères** : clé = tuple `(-score, nom)` → score décroissant, puis nom croissant. Résultat *déterministe* même en cas d'égalité.
- **Générateur** (`yield`) : la fonction ne s'exécute pas à l'appel mais à chaque `next()`. Conséquences : (1) la `ValueError` de `par_blocs(x, 0)` n'apparaît qu'au premier parcours (le test le montre avec `list(...)`) ; (2) les blocs sont produits un par un → **mémoire constante**, essentiel pour de gros fichiers.

**Pièges**
- `.title()` ne connaît pas les cas particuliers (`"mcdonald"` → `"Mcdonald"`) : suffisant ici, pas universel.
- `sequence[debut : debut + taille]` ne plante jamais en fin de séquence : le slicing est tolérant.

**Ailleurs, même idée** : normaliser des e-mails/adresses, regrouper des commandes par client ou des erreurs par service, lire un fichier de 10 Go par paquets de 1 000 lignes.

---

## 2. Fonctions, décorateurs, modules — `utils.py`

**Ce que tu devais comprendre** : arguments variables, fonctions qui prennent/renvoient des fonctions, organisation en modules.

*(Code : voir le bloc `utils.py` de la partie 1 ci-dessus.)*

**Explications clés**
- `moyenne(*valeurs, arrondi=2)` : `*valeurs` regroupe les arguments positionnels en tuple ; `arrondi`, placé après, devient **obligatoirement nommé** → appel lisible : `moyenne(1, 2, 2, arrondi=1)`. À l'appel, `*(...)` fait l'inverse : il **déballe** un itérable en arguments (`moyenne(*(p.points for p in perfs))`).
- **Décorateur** = fonction qui reçoit une fonction et en renvoie une autre. `wrapper(*args, **kwargs)` accepte *n'importe quelle* signature.
- `@functools.wraps(fonction)` recopie `__name__` et `__doc__` : sans lui, `charger_csv.__name__` vaudrait `"wrapper"` → logs et débogage illisibles.
- `try / finally` : la durée est journalisée **dans tous les cas**, et l'exception, s'il y en a une, continue de remonter (on ne l'avale pas).
- `logging` plutôt que `print` : niveaux, désactivable, visible avec `--verbose`.
- **Modules** : `utils.py` n'importe rien du projet (donc réutilisable tel quel) ; `models` importe `utils` ; `loader` importe `models`… Une responsabilité par fichier, dépendances à sens unique.

**Ailleurs, même idée** : un `@retry(3)` pour appels réseau, un `@cache`, un `@requiert_admin` sur une route, un `@mesure_temps` sur les étapes d'un pipeline.

---

## 3. Programmation orientée objet — `models.py`, `exporteurs.py`

**Ce que tu devais comprendre** : représenter le domaine avec des objets qui **ne peuvent pas être invalides**, encapsuler, et rendre le code extensible.

**`nba_tracker/models.py`**

```python
"""Partie 3 — Programmation orientée objet : les modèles du domaine."""

from __future__ import annotations

import datetime as dt
from collections.abc import Mapping
from dataclasses import dataclass

from .errors import DonneeInvalideError
from .utils import moyenne, normaliser_nom

COLONNES = ("date", "joueur", "equipe", "minutes", "points", "rebonds", "passes")


@dataclass(frozen=True)  # frozen : immuable, comparable (==), hashable
class Performance:
    """Stats d'un joueur sur un match.

    Règles : `joueur` et `equipe` sont normalisés (voir `normaliser_nom`) ; `joueur` non vide ;
    1 <= minutes <= 60 ; points, rebonds et passes >= 0. Sinon : DonneeInvalideError.
    """

    date: dt.date
    joueur: str
    equipe: str
    minutes: int
    points: int
    rebonds: int
    passes: int

    def __post_init__(self) -> None:
        # Instance frozen : self.joueur = ... est interdit, on passe par object.__setattr__
        object.__setattr__(self, "joueur", normaliser_nom(self.joueur))
        object.__setattr__(self, "equipe", normaliser_nom(self.equipe))
        if not self.joueur:
            raise DonneeInvalideError("nom de joueur vide")
        if not 1 <= self.minutes <= 60:  # comparaison chaînée
            raise DonneeInvalideError(f"minutes hors plage (1-60) : {self.minutes}")
        for champ in ("points", "rebonds", "passes"):
            if getattr(self, champ) < 0:
                raise DonneeInvalideError(f"{champ} négatif : {getattr(self, champ)}")

    @property
    def points_par_minute(self) -> float:
        """Points marqués divisés par les minutes jouées."""
        return self.points / self.minutes

    @classmethod
    def depuis_ligne(cls, ligne: Mapping[str, str | None]) -> Performance:
        """Construit une Performance depuis une ligne de CSV (dict de chaînes, comme DictReader).

        Colonne absente -> DonneeInvalideError dont le message contient « colonne manquante » ;
        valeur illisible (date, entier) -> DonneeInvalideError. Les blancs autour des valeurs sont ignorés.
        """
        try:
            # `or ""` : DictReader met None quand une ligne est trop courte
            brut = {cle: (ligne[cle] or "").strip() for cle in COLONNES}
            return cls(
                date=dt.date.fromisoformat(brut["date"]),
                joueur=brut["joueur"],
                equipe=brut["equipe"],
                minutes=int(brut["minutes"]),
                points=int(brut["points"]),
                rebonds=int(brut["rebonds"]),
                passes=int(brut["passes"]),
            )
        except KeyError as exc:
            raise DonneeInvalideError(f"colonne manquante : {exc.args[0]}") from exc
        except ValueError as exc:  # int("abc"), date invalide... (DonneeInvalideError n'en hérite pas)
            raise DonneeInvalideError(f"valeur illisible : {exc}") from exc


class Joueur:
    """Un joueur et l'ensemble de ses performances (encapsulation : la liste reste privée)."""

    def __init__(self, nom: str) -> None:
        self.nom = normaliser_nom(nom)
        self._performances: list[Performance] = []  # « _ » = usage interne par convention

    def ajouter(self, performance: Performance) -> None:
        """Ajoute une performance ; DonneeInvalideError si elle appartient à un autre joueur."""
        if performance.joueur != self.nom:
            raise DonneeInvalideError(f"{performance.joueur} n'est pas {self.nom}")
        self._performances.append(performance)

    @property
    def performances(self) -> tuple[Performance, ...]:
        """Vue en lecture seule (tuple) des performances, sans setter."""
        return tuple(self._performances)

    def __len__(self) -> int:
        return len(self._performances)

    def __repr__(self) -> str:
        return f"Joueur({self.nom!r}, matchs={len(self)})"

    def _moyenne_de(self, champ: str) -> float:
        # expression génératrice : pas de liste intermédiaire ; * la « déballe » en arguments
        return moyenne(*(getattr(p, champ) for p in self._performances))

    @property
    def points_moyens(self) -> float:
        """Moyenne de points par match (0.0 sans match)."""
        return self._moyenne_de("points")

    @property
    def rebonds_moyens(self) -> float:
        """Moyenne de rebonds par match (0.0 sans match)."""
        return self._moyenne_de("rebonds")

    @property
    def passes_moyennes(self) -> float:
        """Moyenne de passes par match (0.0 sans match)."""
        return self._moyenne_de("passes")

    @property
    def meilleur_match(self) -> Performance | None:
        """La performance avec le plus de points, ou None sans match."""
        return max(self._performances, key=lambda p: p.points, default=None)
```

**`nba_tracker/exporteurs.py`**

```python
"""Partie 3 (suite) — héritage, classe abstraite et polymorphisme."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from collections.abc import Iterable

from .models import Joueur


class Exporteur(ABC):
    """Contrat commun : toute sous-classe sait transformer des joueurs en texte. Non instanciable."""

    @abstractmethod
    def exporter(self, joueurs: Iterable[Joueur]) -> str:
        """Renvoie la représentation textuelle des joueurs, triés par nom."""


class ExporteurTexte(Exporteur):
    """Une ligne par joueur : nom, nombre de matchs, puis points/rebonds/passes moyens (1 décimale)."""

    def exporter(self, joueurs: Iterable[Joueur]) -> str:
        lignes = [
            f"{j.nom:<16} {len(j):>2} matchs | {j.points_moyens:>5.1f} pts"
            f" | {j.rebonds_moyens:>4.1f} reb | {j.passes_moyennes:>4.1f} pas"
            for j in sorted(joueurs, key=lambda j: j.nom)
        ]
        return "\n".join(lignes)


class ExporteurJSON(Exporteur):
    """Liste JSON d'objets {joueur, matchs, points_moyens, rebonds_moyens, passes_moyennes}, indentée."""

    def exporter(self, joueurs: Iterable[Joueur]) -> str:
        donnees = [
            {
                "joueur": j.nom,
                "matchs": len(j),
                "points_moyens": j.points_moyens,
                "rebonds_moyens": j.rebonds_moyens,
                "passes_moyennes": j.passes_moyennes,
            }
            for j in sorted(joueurs, key=lambda j: j.nom)
        ]
        return json.dumps(donnees, ensure_ascii=False, indent=2)  # ensure_ascii=False : garde « é »
```

**Explications clés**
- `@dataclass` génère `__init__`, `__repr__`, `__eq__` ; `frozen=True` → **immuable** et hashable. Pour normaliser/valider à la création on utilise `__post_init__` ; sur une instance gelée il faut passer par `object.__setattr__`.
- Principe : **rendre les états invalides impossibles**. Une `Performance` qui existe est forcément valide → le reste du code n'a plus à re-vérifier.
- `@property` = attribut calculé, en lecture seule (pas de setter → `AttributeError` à l'affectation). `performances` renvoie un **tuple** : l'extérieur ne peut pas modifier la liste privée `_performances` (encapsulation).
- `@classmethod depuis_ligne` = **constructeur alternatif** (`cls(...)`) ; il convertit les erreurs *techniques* (`int("")`, date impossible → `ValueError`) en erreur *métier* (`DonneeInvalideError`) avec `raise ... from exc`.
- `__len__` et `__repr__` : les méthodes spéciales font que ton objet se comporte comme un objet Python natif (`len(joueur)`, affichage lisible).
- `ABC` + `@abstractmethod` : `Exporteur()` est **non instanciable** ; toute sous-classe doit implémenter `exporter`. **Polymorphisme** : l'appelant (`__main__`) n'a pas besoin de savoir quelle sous-classe il utilise → ajouter un `ExporteurCSV` demain ne modifie aucun appelant.

**Pièges**
- `f"{16.25:.1f}"` affiche **`16.2`** (et non 16.3) : c'est ce que tu vois pour Diego dans la sortie. La représentation binaire des flottants + arrondi « au pair » : ne jamais s'y fier pour de l'argent → `decimal.Decimal`.
- `except ValueError` n'attrape **pas** `DonneeInvalideError` (elle n'en hérite pas) : c'est voulu, chaque niveau traite « ses » erreurs.

**Ailleurs, même idée** : `Commande` (montant ≥ 0, quantité ≥ 1), `LigneLog` (niveau ∈ {INFO, WARN, ERROR}), `SeanceEtude` (durée > 0) ; `Exporteur` → export CSV/PDF de factures, notifications Slack/e-mail.

---

## 4. Exceptions, chargement de données & typage — `errors.py`, `loader.py`, `stats.py`

**Ce que tu devais comprendre** : gérer les erreurs proprement, ne jamais perdre tout un lot pour une mauvaise ligne, composer de petites fonctions, typer.

**`nba_tracker/errors.py`**

```python
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
```

**`nba_tracker/loader.py`**

```python
"""Partie 4 — Lecture du CSV avec gestion d'erreurs et annotations de types."""

from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass
from pathlib import Path

from .errors import DonneeInvalideError, FichierIntrouvableError
from .models import Performance
from .utils import chronometre


@dataclass(frozen=True)
class LigneRejetee:
    """Une ligne du CSV écartée, avec le numéro de ligne dans le fichier (l'en-tête est la ligne 1)."""

    numero_ligne: int
    raison: str


@chronometre
def charger_csv(chemin: str | Path) -> tuple[list[Performance], list[LigneRejetee]]:
    """Lit le CSV (UTF-8) et renvoie (performances valides, lignes rejetées).

    Une ligne invalide ne fait JAMAIS échouer le chargement : elle est rejetée avec sa raison.
    Une ligne dont le couple (date, joueur) a déjà été vu est rejetée avec une raison contenant « doublon »
    (la première occurrence est conservée). Fichier absent -> FichierIntrouvableError.
    """
    chemin = Path(chemin)  # accepte str ET Path
    performances: list[Performance] = []
    rejets: list[LigneRejetee] = []
    vus: set[tuple[dt.date, str]] = set()  # un set : test d'appartenance en O(1)

    try:
        with chemin.open(encoding="utf-8", newline="") as fichier:  # `with` ferme le fichier quoi qu'il arrive
            lecteur = csv.DictReader(fichier)
            for numero, ligne in enumerate(lecteur, start=2):  # start=2 : la ligne 1 est l'en-tête
                try:
                    performance = Performance.depuis_ligne(ligne)
                except DonneeInvalideError as erreur:
                    rejets.append(LigneRejetee(numero, erreur.raison))
                else:  # else = « si le try a réussi » : garde le try minimal
                    cle = (performance.date, performance.joueur)
                    if cle in vus:
                        rejets.append(LigneRejetee(numero, "doublon (même joueur, même date)"))
                    else:
                        vus.add(cle)
                        performances.append(performance)
    except FileNotFoundError as exc:
        # `from exc` conserve la cause d'origine dans le traceback
        raise FichierIntrouvableError(str(chemin)) from exc

    return performances, rejets
```

**`nba_tracker/stats.py`**

```python
"""Partie 4 (suite) — agrégations : on assemble utils + modèles."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from .models import Joueur, Performance
from .utils import moyenne, regrouper_par, top_n

CRITERES = ("points_moyens", "rebonds_moyens", "passes_moyennes")


def construire_joueurs(performances: Iterable[Performance]) -> dict[str, Joueur]:
    """Regroupe les performances par joueur : {nom normalisé: Joueur}. Réutilise `regrouper_par`."""
    joueurs: dict[str, Joueur] = {}
    for nom, perfs in regrouper_par(performances, lambda p: p.joueur).items():
        joueur = Joueur(nom)
        for perf in perfs:
            joueur.ajouter(perf)
        joueurs[nom] = joueur
    return joueurs


def classement(
    joueurs: Mapping[str, Joueur], critere: str = "points_moyens", n: int = 3
) -> list[tuple[str, float]]:
    """Les `n` meilleurs joueurs selon `critere` (l'un de CRITERES) : liste de (nom, valeur).

    Critère inconnu -> ValueError. Réutilise `top_n`.
    """
    if critere not in CRITERES:
        raise ValueError(f"critère inconnu : {critere!r} (attendu : {', '.join(CRITERES)})")
    scores = {nom: getattr(joueur, critere) for nom, joueur in joueurs.items()}  # getattr : attribut choisi par son nom
    return top_n(scores, n)


def stats_par_equipe(performances: Iterable[Performance]) -> dict[str, dict[str, float]]:
    """{equipe: {"performances": nombre de lignes, "points_moyens": moyenne des points}}."""
    groupes = regrouper_par(performances, lambda p: p.equipe)
    return {
        equipe: {"performances": len(perfs), "points_moyens": moyenne(*(p.points for p in perfs))}
        for equipe, perfs in groupes.items()
    }


def forme_recente(joueur: Joueur, fenetre: int = 3) -> float:
    """Moyenne des points sur les `fenetre` matchs les plus récents (par date). ValueError si fenetre <= 0."""
    if fenetre <= 0:
        # piège : liste[-0:] renvoie TOUTE la liste, pas une liste vide !
        raise ValueError(f"fenetre doit être > 0, reçu {fenetre}")
    recents = sorted(joueur.performances, key=lambda p: p.date)[-fenetre:]
    return moyenne(*(p.points for p in recents))
```

**Explications clés**
- **Hiérarchie d'exceptions** : `TrackerError` en racine → `except TrackerError` attrape toutes *tes* erreurs sans masquer les vrais bugs (`TypeError`, `KeyError`…).
- `raise X from exc` **conserve la cause** dans le traceback ; `from None` la masque (utilisé dans l'API pour ne pas exposer un `KeyError`).
- `try / except / else` : `else` ne s'exécute que si aucune exception n'a eu lieu → le `try` ne contient **que** la ligne qui peut échouer. On n'attrape pas par erreur une exception venue d'ailleurs.
- `with` : fermeture du fichier **garantie**, même en cas d'erreur. `enumerate(..., start=2)` : numéros de ligne cohérents avec l'éditeur (l'en-tête est la ligne 1).
- **`set` pour les doublons** : test `in` en O(1). La clé `(date, joueur)` utilise le nom **normalisé** → « amara diallo » et « Amara Diallo » sont bien le même joueur.
- **Les rejets sont de la donnée, pas des exceptions** : `charger_csv` *retourne* `(valides, rejets)`. C'est le réflexe d'un pipeline ETL robuste : on ne perd pas 1 million de lignes pour une seule mauvaise.
- `stats.py` réutilise `regrouper_par`, `top_n`, `moyenne` : **petites fonctions composables**. `getattr(joueur, critere)` choisit l'attribut à l'exécution, d'où la validation `critere in CRITERES`.
- **Typage** : `list[Performance]`, `dict[str, Joueur]`, `str | Path`, `X | None`, `TypeVar` (génériques : `regrouper_par` marche pour n'importe quel type et `mypy` conserve le type de sortie). Les annotations **ne sont pas vérifiées à l'exécution** : c'est `mypy` qui le fait.

**Pièges**
- `liste[-fenetre:]` avec `fenetre=0` renvoie **toute** la liste (car `-0 == 0`) → validation explicite dans `forme_recente`.
- Attraper `Exception` « pour être tranquille » cache les bugs : toujours l'exception la plus précise possible.

**Ailleurs, même idée** : c'est le **E et le T de ETL** — Extract (lecture), Transform (validation/normalisation), avec une table de rejets ; le **L** (Load vers PostgreSQL) arrive avec tes cartes SQL et *ETL / ELT & pipelines Python*.

---

## 5. Environnements & packaging — `__main__.py`, `pyproject.toml`

**Ce que tu devais comprendre** : rendre un projet installable, lançable et reproductible.

**`nba_tracker/__main__.py`**

```python
"""Partie 5 — Point d'entrée : `python -m nba_tracker data/matchs.csv`."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from .errors import FichierIntrouvableError
from .exporteurs import ExporteurJSON, ExporteurTexte
from .loader import charger_csv
from .stats import classement, construire_joueurs


def main(argv: Sequence[str] | None = None) -> int:
    """Interface en ligne de commande. Renvoie le code de sortie (0 = succès, 1 = fichier introuvable).

    Options : `fichier` (positionnel), `--top N` (défaut 3), `--format {texte,json}` (défaut texte),
    `--verbose` (affiche les durées journalisées par @chronometre).
    Les lignes rejetées sont listées sur stderr ("N ligne(s) rejetée(s)") ; stdout ne contient que le résultat
    (format json : uniquement le JSON).
    """
    parseur = argparse.ArgumentParser(prog="nba_tracker", description="Statistiques basket depuis un CSV.")
    parseur.add_argument("fichier", type=Path, help="chemin du CSV de matchs")
    parseur.add_argument("--top", type=int, default=3, help="taille du classement (défaut : 3)")
    parseur.add_argument("--format", choices=("texte", "json"), default="texte")
    parseur.add_argument("--verbose", action="store_true", help="affiche les durées d'exécution")
    args = parseur.parse_args(argv)  # argv=None -> lit sys.argv ; une liste -> pratique pour les tests

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    try:
        performances, rejets = charger_csv(args.fichier)
    except FichierIntrouvableError as erreur:
        print(f"Erreur : {erreur}", file=sys.stderr)
        return 1

    if rejets:
        print(f"{len(rejets)} ligne(s) rejetée(s) :", file=sys.stderr)
        for rejet in rejets:
            print(f"  - ligne {rejet.numero_ligne} : {rejet.raison}", file=sys.stderr)

    joueurs = construire_joueurs(performances)
    if args.format == "json":
        print(ExporteurJSON().exporter(joueurs.values()))
    else:
        print(ExporteurTexte().exporter(joueurs.values()))
        print(f"\nTop {args.top} (points moyens) :")
        for rang, (nom, score) in enumerate(classement(joueurs, n=args.top), start=1):
            print(f"{rang}. {nom} — {score:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Explications clés**
- `python -m nba_tracker` exécute `nba_tracker/__main__.py` **comme un programme, avec le package importable** → les imports relatifs (`from .loader import ...`) fonctionnent (ce n'est pas le cas de `python nba_tracker/__main__.py`).
- `main(argv=None) -> int` **retourne un code de sortie**, transmis à l'OS par `raise SystemExit(main())` : 0 = OK, ≠ 0 = erreur. Indispensable pour scripts, CI, cron, Airflow (ils lisent ce code).
- **stdout = résultat, stderr = diagnostics** : on peut chaîner `python -m nba_tracker data/matchs.csv --format json | jq` sans polluer le JSON.
- `main` accepte une liste `argv` → **testable sans sous-processus** (voir `test_p5_cli.py`).
- `pyproject.toml` décrit le package et ses dépendances ; `pip install -e .` = installation **éditable** : Python utilise directement ton code source, pas une copie.
- `.venv` isole les dépendances du projet (jamais commité : `.gitignore`) ; `pip freeze > requirements-lock.txt` fige les versions exactes pour reproduire l'environnement.

**Ailleurs, même idée** : tout script de data engineering (`python -m pipeline --date 2026-01-05`), un outil interne, une tâche planifiée.

---

## 6. Tests avec pytest — `tests/`

**Ce que tu devais comprendre** : prouver que le code marche et le rester lors des modifications.

Exemples des tests de la partie 6 (corrigés) :

**`tests/test_p6_mes_tests.py`**

```python
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
```

Et la fixture partagée :

**`tests/conftest.py`**

```python
"""Fixtures partagées par tous les fichiers de tests (pytest les découvre automatiquement)."""

import datetime as dt
from pathlib import Path

import pytest

from nba_tracker.models import Performance

RACINE = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def chemin_csv() -> Path:
    """Chemin du CSV d'exemple (calculé une seule fois pour toute la session de tests)."""
    return RACINE / "data" / "matchs.csv"


@pytest.fixture()
def fabrique_perf():
    """« Fabrique » : renvoie une fonction qui crée des Performance valides, modifiables par mot-clé."""

    def _creer(joueur="Amara Diallo", equipe="Lions", jour="2026-01-05",
               minutes=30, points=20, rebonds=5, passes=4):
        return Performance(date=dt.date.fromisoformat(jour), joueur=joueur, equipe=equipe,
                           minutes=minutes, points=points, rebonds=rebonds, passes=passes)

    return _creer
```

**Explications clés**
- `parametrize` : **un test, N cas** (ajouter un cas = 1 ligne). `pytest.approx` compare des flottants sans piège d'arrondi (`1/3`).
- **Fixtures** : préparation réutilisable, injectée par le **nom du paramètre**. `scope` (`function` par défaut, `module`, `session`) : ce qui coûte cher se partage.
- **Fixture « fabrique »** (`fabrique_perf`) : elle renvoie une *fonction* ; chaque test crée sa variante avec des valeurs par défaut sensées → tests courts et lisibles.
- `tmp_path` : dossier temporaire isolé → aucun fichier de test qui traîne. `capsys` / `caplog` : capturent stdout/stderr et logs.
- `pytest.raises(Type, match="...")` vérifie le **type et le message**.
- Teste le **comportement** (entrées → sorties), pas l'implémentation. Un bon test échoue pour **une seule raison**.

**Ailleurs, même idée** : avant de toucher à un pipeline en production, un jeu de tests sur un mini CSV protège contre les régressions.

---

## 7. Asynchrone — `async_fetch.py`

**Ce que tu devais comprendre** : attendre plusieurs opérations d'I/O **en même temps**.

**`nba_tracker/async_fetch.py`**

```python
"""Partie 7 — Programmation asynchrone (asyncio) : attendre plusieurs I/O en parallèle."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence


async def recuperer_stats(nom: str, delai: float = 0.2) -> dict[str, str]:
    """Simule un appel réseau de `delai` secondes (asyncio.sleep) et renvoie
    {"joueur": nom, "source": "api-simulee"}.
    """
    await asyncio.sleep(delai)  # await : « pendant que j'attends, l'event loop peut faire autre chose »
    return {"joueur": nom, "source": "api-simulee"}


async def recuperer_tous(noms: Sequence[str], delai: float = 0.2) -> list[dict[str, str]]:
    """Récupère les stats de tous les `noms` CONCURREMMENT (durée ≈ un seul délai, pas la somme).

    Les résultats sont renvoyés dans le même ordre que `noms`.
    """
    # gather lance toutes les coroutines « en même temps » et conserve l'ordre des résultats
    return list(await asyncio.gather(*(recuperer_stats(nom, delai) for nom in noms)))


async def recuperer_avec_timeout(nom: str, delai: float, timeout: float) -> dict[str, str] | None:
    """Comme `recuperer_stats`, mais renvoie None si l'appel dépasse `timeout` secondes."""
    try:
        return await asyncio.wait_for(recuperer_stats(nom, delai), timeout=timeout)
    except asyncio.TimeoutError:  # alias de TimeoutError depuis Python 3.11
        return None
```

**Explications clés**
- `async def` définit une **coroutine** : l'appeler ne l'exécute pas, ça la *crée*. `await` la lance et **rend la main à la boucle d'événements** pendant l'attente.
- `asyncio.run(...)` = point d'entrée unique qui démarre la boucle.
- `asyncio.gather(*coros)` lance tout, attend tout, et renvoie les résultats **dans l'ordre des arguments** : 5 × 0,2 s → ≈ 0,2 s (le test vérifie `< 0,6 s`). Trois `await` à la suite, eux, s'additionnent (séquentiel).
- `wait_for` annule la tâche au timeout et lève `TimeoutError`, qu'on convertit ici en `None`.

**Pièges**
- L'async accélère l'**I/O** (réseau, disque, base). Pour du calcul CPU pur, il n'aide pas (→ `multiprocessing`, Spark plus tard).
- Appeler du code **bloquant** dans une coroutine (`time.sleep`, `requests.get`) bloque **toute** la boucle : utilise `asyncio.sleep`, `httpx.AsyncClient`…

**Ailleurs, même idée** : interroger 20 API de stats en parallèle dans ta *NBA Data Platform*, appeler plusieurs services avant de répondre, télécharger 100 fichiers.

---

## 8. API FastAPI — `api.py`

**Ce que tu devais comprendre** : exposer ton domaine en HTTP avec validation automatique.

**`nba_tracker/api.py`**

```python
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
```

**Explications clés**
- **Pydantic** : le modèle est à la fois schéma **et** validation. Un mauvais JSON → réponse **422 détaillée** sans une seule ligne de `if` (`Field(ge=1, le=60, min_length=1)`).
- `response_model` filtre/valide la sortie ; `status_code=201` (création) et `204` (suppression, sans corps).
- `HTTPException(404)` pour les ressources absentes ; `from None` masque le `KeyError` interne.
- **Deux représentations** : `PerformanceIn/Out` (Pydantic) = la **frontière HTTP** ; `Performance`/`Joueur` = le **domaine**. `stats_joueur` convertit avec `Performance(**p.model_dump(exclude={"id"}))` pour réutiliser la logique métier → **aucune duplication** du calcul des moyennes.
- `_depot` (dict en mémoire) simule une base : avec tes cartes *Docker & FastAPI* et *PostgreSQL*, il sera remplacé par de vraies tables. `reinitialiser()` isole les tests.
- Documentation **auto-générée** sur `/docs` ; les tests utilisent `TestClient` (aucun serveur à lancer).

**Ailleurs, même idée** : `/commandes`, `/evenements`, `/seances` — même squelette : modèle d'entrée, modèle de sortie, dépôt, routes CRUD, 404 propres.

---

## 9. Le même schéma dans d'autres contextes

| Ce que tu as appris | NBA (l'exercice) | E-commerce | Logs serveur | Suivi de ton apprentissage |
|---|---|---|---|---|
| Nettoyer / normaliser | noms de joueurs | e-mails, noms de produits | niveaux de log, IP | titres de cartes/sujets |
| `regrouper_par` | par joueur / équipe | commandes par client | erreurs par service | minutes par sujet |
| Dataclass frozen + validation | `Performance` | `Commande` (montant ≥ 0) | `LigneLog` (niveau valide) | `SeanceEtude` (durée > 0) |
| Loader avec rejets | CSV de matchs | import d'un catalogue | parsing d'un `access.log` | export de ton Trello |
| `Exporteur` polymorphe | texte / JSON | CSV / PDF de facture | alerte Slack / e-mail | Markdown / JSON |
| `chronometre` | temps de chargement | temps d'un paiement | temps d'une requête | temps d'une étape |
| `async` + `gather` | N appels d'API stats | stock + paiement + livraison | N services à sonder | N sources de veille |
| API CRUD FastAPI | `/performances` | `/commandes` | `/evenements` | `/seances` |

**Trois mini-défis pour t'exercer (mêmes règles : sans IA, tests d'abord, un commit)**
1. **Commandes** — `commandes.csv` : `date, client, produit, quantite, prix_unitaire`. Règles : quantité ≥ 1, prix > 0, doublon = même (date, client, produit). Sorties : chiffre d'affaires par client, top 3 produits.
2. **Logs** — `access.log` : `2026-01-05T10:02:11 GET /api/joueurs 200 35ms`. Rejette les lignes mal formées avec leur numéro ; calcule le taux d'erreurs 5xx par route et la latence moyenne (avec `@chronometre` sur le parsing).
3. **Journal d'étude** — `seances.csv` : `date, sujet, minutes, type` (cours/exercice/projet). Temps par sujet, « forme récente » sur 7 jours, export Markdown pour ton Trello.

---

## 10. Grille de relecture — compare ta solution à celle-ci

- [ ] Aucune fonction ne modifie ses arguments par surprise ; pas de variable globale modifiée
- [ ] Toute erreur attendue est une **exception précise** (jamais un `except:` nu ni `except Exception` sans raison)
- [ ] Une mauvaise ligne de CSV **ne fait jamais planter** le chargement
- [ ] Les objets du domaine sont **valides dès leur création**
- [ ] Le code appelant ne dépend **que du contrat** (`Exporteur`), pas des sous-classes
- [ ] Chaque fonction publique est **typée** et a une docstring d'une ligne utile
- [ ] Tests : cas normaux, **cas limites** (vide, 0, égalité), cas d'erreur
- [ ] `stdout` = résultat, `stderr` = diagnostics ; code de sortie correct
- [ ] Un commit par partie, message clair

**Et après ?** Dans ton Trello, la carte suivante de *01 — FONDATIONS* est **🗄️ SQL & PostgreSQL** : la partie « Load » de ce mini-ETL (charger `Performance` dans une vraie table) sera un excellent premier exercice.
