# Exercice d'application — Python fondations : « NBA Tracker »

> Carte Trello : **01 — FONDATIONS → 🐍 Python professionnel** (tableau *Data +*).
> Ordre de la carte : syntaxe avancée → fonctions/modules → OOP → exceptions/typing → venv/packages → pytest → async → FastAPI.
> Cet exercice les couvre **toutes**, sur un seul fil rouge.

## 1. Le contexte

Tu construis le noyau Python d'un mini « tracker » de statistiques de basket (le futur cœur de ton projet *NBA Data Platform*).

Chaque jour arrive un fichier CSV de performances de joueurs (`data/matchs.csv`, données **fictives**). Il est réaliste, donc **sale** :
noms mal écrits (`"  amara diallo "`), valeurs manquantes, nombres négatifs, date impossible, texte à la place d'un nombre, doublon…

Ton programme doit :

1. **lire** le CSV sans jamais planter sur une mauvaise ligne (la rejeter *avec sa raison* et son numéro de ligne) ;
2. **modéliser** les données avec des objets validés (`Performance`, `Joueur`) ;
3. **calculer** des moyennes, un classement, des stats par équipe, la « forme récente » ;
4. **exporter** en texte ou en JSON (même interface, deux implémentations) ;
5. se **lancer en ligne de commande** : `python -m nba_tracker data/matchs.csv` ;
6. être **testé** avec pytest ;
7. **récupérer des données en parallèle** (asyncio) ;
8. exposer les données via une **API FastAPI** (CRUD).

## 2. Règles du jeu (celles de ta carte)

- **Sans IA pour écrire le code.** Tu peux lire la doc officielle (docs.python.org, FastAPI Tutorial) ; l'IA n'intervient qu'*après*, pour relire.
- Pour chaque partie : **cours → exercices → mini-script → correction → commit**.
- **Les tests sont ton juge.** Au départ presque tout échoue : c'est normal, c'est le but.
- **Un commit Git par partie** (`git commit -m "Partie 1 : utils"`).
- N'ouvre `2_SOLUTION_expliquee/` qu'après avoir *vraiment* essayé chaque partie.

## 3. Mise en place (Partie 5 — à faire en premier)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q                          # ~47 échecs, 24 erreurs : normal !
git init && git add . && git commit -m "Départ : squelette de l'exercice"
```

## 4. Carte du projet

| Fichier à compléter | Partie | Tests qui le vérifient |
|---|---|---|
| `nba_tracker/utils.py` | 1 et 2 | `tests/test_p1_p2_utils.py` |
| `nba_tracker/errors.py` ⚠️ *à écrire en premier, 4 petites classes* | 4 | `tests/test_p4_chargement.py` |
| `nba_tracker/models.py`, `exporteurs.py` | 3 | `tests/test_p3_poo.py` |
| `nba_tracker/loader.py`, `stats.py` | 4 | `tests/test_p4_chargement.py`, `test_p4_stats.py` |
| `nba_tracker/__main__.py` | 5 | `tests/test_p5_cli.py` |
| `tests/test_p6_mes_tests.py` | 6 | (c'est toi qui écris les tests) |
| `nba_tracker/async_fetch.py` | 7 | `tests/test_p7_async.py` |
| `nba_tracker/api.py` | 8 | `tests/test_p8_api.py` |

**Chaque fonction a une docstring = son cahier des charges.** Lis-la, puis remplace `raise NotImplementedError` par ton code.

## 5. Les parties 
### Partie 1 — Syntaxe avancée & structures de données (`utils.py`)
- [ ] `normaliser_nom` · [ ] `regrouper_par` · [ ] `top_n` · [ ] `par_blocs` (**générateur**, avec `yield`)

Notions : méthodes de `str`, `dict`/`set`/`tuple`, `defaultdict`, `sorted` + `key` + `lambda`, slicing, compréhensions, générateurs.
Test : `pytest tests/test_p1_p2_utils.py -k "normaliser or regrouper or top_n or blocs"`

### Partie 2 — Fonctions, décorateurs, modules (`utils.py`)
- [ ] `moyenne(*valeurs, arrondi=2)` (arguments variables + argument nommé par défaut)
- [ ] `chronometre` : un **décorateur** qui journalise la durée (`logging`), **même en cas d'exception**, et préserve le nom/la doc de la fonction.

Notions : `*args`/`**kwargs`, fonctions d'ordre supérieur, closures, `functools.wraps`, `try/finally`, imports relatifs (`from .utils import ...`), un module = une responsabilité.
Test : `pytest tests/test_p1_p2_utils.py -k "moyenne or chronometre"`

### Partie 3 — Programmation orientée objet (`models.py`, `exporteurs.py`)
- [ ] `Performance` : `@dataclass(frozen=True)`, validation dans `__post_init__`, propriété `points_par_minute`, constructeur alternatif `depuis_ligne` (`@classmethod`)
- [ ] `Joueur` : encapsulation (`_performances`), `__len__`, `__repr__`, propriétés de moyennes, `meilleur_match`
- [ ] `Exporteur` (classe **abstraite**) + `ExporteurTexte` + `ExporteurJSON` (**polymorphisme**)

Notions : classes, `dataclass`, immuabilité, `@property`, `@classmethod`, méthodes spéciales, `ABC`/`@abstractmethod`, héritage.
Test : `pytest tests/test_p3_poo.py`  *(nécessite `errors.py` : écris-le d'abord)*

### Partie 4 — Exceptions & typage (`errors.py`, `loader.py`, `stats.py`)
- [ ] `errors.py` : hiérarchie d'exceptions (cahier des charges dans le fichier)
- [ ] `charger_csv` : `with open`, `csv.DictReader`, `try / except / else`, rejet des lignes invalides **sans planter**, détection des doublons avec un `set`, `FichierIntrouvableError` si le fichier n'existe pas
- [ ] `construire_joueurs`, `classement`, `stats_par_equipe`, `forme_recente`
- [ ] **Type hints partout**, puis `mypy nba_tracker` → **0 erreur**

Notions : `raise ... from ...`, exceptions personnalisées, `Path`, context managers, `getattr`, `list[...]`/`dict[...]`/`X | None`, `TypeVar`.
Tests : `pytest tests/test_p4_chargement.py tests/test_p4_stats.py`

### Partie 5 — Environnements & packaging (`__main__.py`, `pyproject.toml`)
- [ ] Environnement virtuel + `pip install -e ".[dev]"` (déjà fait en §3 : **comprends** ce que ça a changé, lis `pyproject.toml`)
- [ ] `pip freeze > requirements-lock.txt` : à quoi ça sert, quand l'utiliser ?
- [ ] `main()` avec **argparse** : `fichier`, `--top N`, `--format {texte,json}`, `--verbose` ; les diagnostics sur **stderr**, le résultat sur **stdout**
- [ ] `python -m nba_tracker data/matchs.csv --top 3` fonctionne

Notions : `venv`, dépendances, package installable, `python -m`, `__main__.py`, `if __name__ == "__main__"`, `argparse`, `sys.stderr`, codes de sortie.
Test : `pytest tests/test_p5_cli.py`

### Partie 6 — Tests avec pytest (`tests/test_p6_mes_tests.py`)
- [ ] Écris les **3 tests** décrits dans le fichier (`parametrize` + `approx`, `tmp_path`, fixture `fabrique_perf`)
- [ ] **Lis** les autres fichiers de tests et repère : `fixture`, `parametrize`, `pytest.raises(match=...)`, `tmp_path`, `capsys`, `caplog`, fixture « fabrique », `scope="module"`.
- [ ] Bonus : casse volontairement une fonction de `utils.py` et vérifie qu'un test devient rouge, puis répare.

### Partie 7 — Asynchrone (`async_fetch.py`)
- [ ] `recuperer_stats` (simule un appel réseau avec `asyncio.sleep`)
- [ ] `recuperer_tous` : **concurrent** avec `asyncio.gather`, ordre conservé
- [ ] `recuperer_avec_timeout` : `asyncio.wait_for` + gestion du timeout
- [ ] Bonus : écris un mini-script qui mesure « séquentiel vs gather » sur 10 joueurs.

Notions : `async`/`await`, boucle d'événements, `asyncio.run`, concurrence I/O ≠ parallélisme CPU.
Test : `pytest tests/test_p7_async.py`

### Partie 8 — API FastAPI (`api.py`)
- [ ] CRUD sur `/performances` (POST 201, GET liste + filtre `?joueur=`, GET/PUT/DELETE par id, 404 propres, 204 au DELETE)
- [ ] `GET /joueurs/{nom}/stats` réutilise `Joueur` (tes classes de la Partie 3)
- [ ] `reinitialiser()` vide le stockage (pour les tests)
- [ ] Lance le serveur : `uvicorn nba_tracker.api:app --reload` puis ouvre <http://127.0.0.1:8000/docs> et teste à la main.

Notions : routes, modèles Pydantic (validation → 422 automatique), codes HTTP, `HTTPException`, `TestClient`.
Test : `pytest tests/test_p8_api.py`

## 6. Critères de réussite finale

- `pytest` → **tout vert** (un avertissement de dépréciation httpx/Starlette peut s'afficher : sans conséquence)
- `mypy nba_tracker` → **0 erreur**
- `python -m nba_tracker data/matchs.csv` affiche le classement (le CSV contient **19 lignes valides et 6 rejetées**)
- l'API répond correctement dans `/docs`
- **8 commits** propres, un par partie

## 7. Auto-évaluation (réponds à l'oral, sans regarder le code)

1. Pourquoi l'erreur de `par_blocs(x, 0)` n'apparaît-elle qu'au parcours ?
2. Pourquoi `object.__setattr__` dans `__post_init__` d'une dataclass `frozen` ?
3. Que se passerait-il sans `functools.wraps` ? Sans `finally` dans `chronometre` ?
4. Pourquoi `DonneeInvalideError` n'hérite-t-elle pas de `ValueError` ?
5. Quelle différence entre `await recuperer_stats(...)` trois fois de suite et `asyncio.gather` ?
6. Pourquoi deux représentations (`Performance` dataclass / `PerformanceIn` Pydantic) ?

Bon courage — et rappelle-toi : **compétence + projet démontré > certificat**.
