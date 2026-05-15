# Explication ULTRA détaillée du projet — pour vraiment tout comprendre

> Ce document part du principe que tu connais Python de base (fonctions,
> classes, dicts, listes) mais que certains concepts plus avancés
> (décorateurs, dataclasses, AST, regex, numpy, pydantic, lazy import,
> RRF, BM25...) sont flous. On va décortiquer **chaque ligne** et
> **chaque concept** au fur et à mesure qu'ils apparaissent.

---

## Table des matières

0. [Le big picture en 30 secondes](#0-big-picture)
1. [Concepts transversaux à connaître AVANT de lire le code](#1-concepts)
2. [Point d'entrée : `__main__.py`](#2-entry)
3. [`cli.py` — l'orchestrateur](#3-cli)
4. [`models.py` — les contrats de données (Pydantic)](#4-models)
5. [`ingest.py` — parcourir le repo et lire les fichiers](#5-ingest)
6. [`chunking.py` — découper les fichiers en morceaux](#6-chunking)
7. [`tokenizer.py` — transformer le texte en mots](#7-tokenizer)
8. [`index.py` — construire et interroger l'index](#8-index)
9. [`generator.py` — faire répondre un LLM](#9-generator)
10. [`evaluate.py` — calculer le score recall@k](#10-evaluate)
11. [Les 3 flots d'exécution complets](#11-flows)
12. [Pourquoi ce design ?](#12-design)

---

<a id="0-big-picture"></a>
## 0. Le big picture en 30 secondes

Le projet est un **RAG** (Retrieval-Augmented Generation). En clair :

1. On a une grosse base de code (le repo `vllm-0.10.1`).
2. On veut poser des questions style « comment vllm gère les requêtes
   OpenAI ? » et obtenir une réponse + les bouts de fichiers qui
   prouvent la réponse.
3. Pour ça on fait deux étapes :
   - **Indexation** (offline, une fois) : on découpe tous les fichiers
     en petits morceaux (chunks), et on construit un index qui permet
     de retrouver vite les chunks pertinents pour une requête.
   - **Recherche + génération** (online, à chaque question) : on
     récupère les top-k chunks, on les colle dans un prompt, et on
     demande à un LLM de répondre.

L'évaluation mesure si on retrouve les **bons** chunks (ceux annotés
comme contenant la réponse).

---

<a id="1-concepts"></a>
## 1. Concepts transversaux à connaître AVANT de lire le code

### 1.1 `from __future__ import annotations`

Tu vas voir cette ligne en haut de presque tous les fichiers. Elle dit
à Python : « ne **résous pas** les annotations de type tout de suite,
garde-les comme des strings, on les évaluera plus tard si besoin ».

Avantages :

- Tu peux écrire `def f(x: list[int]) -> dict[str, int]:` même sur
  Python 3.8 (sinon il faut `from typing import List, Dict`).
- Tu peux référencer une classe qui n'est **pas encore définie** (forward
  reference) sans guillemets.

C'est purement cosmétique pour nous : ça ne change pas le
fonctionnement.

### 1.2 Les *type hints* (annotations)

Quand tu écris :

```python
def add(a: int, b: int) -> int:
    return a + b
```

Les `: int` et `-> int` ne sont **pas vérifiés à l'exécution**. C'est
juste de la documentation lisible par des outils comme `mypy`. Python
s'en moque, mais ton IDE et ton linter t'aident grâce à ça.

### 1.3 Les `@dataclass`

```python
from dataclasses import dataclass

@dataclass
class Chunk:
    file_path: str
    first_character_index: int
    last_character_index: int
    text: str
```

Le décorateur `@dataclass` génère automatiquement :

- `__init__(file_path, first_character_index, ...)`
- `__repr__` (le `print()` affichera tous les champs)
- `__eq__`

Bref, c'est une classe « porte-données » sans boilerplate.

### 1.4 Pydantic — comme dataclass mais avec validation

```python
from pydantic import BaseModel

class MinimalSource(BaseModel):
    file_path: str
    first_character_index: int
    last_character_index: int
```

Différences avec `@dataclass` :

- Si tu fais `MinimalSource(file_path="x", first_character_index="abc", ...)`
  → **exception** immédiate parce que `"abc"` n'est pas un `int`.
- Tu as `.model_dump_json(indent=2)` pour sérialiser en JSON.
- Tu as `.model_validate_json(raw_json)` pour parser depuis un JSON
  avec validation.

C'est exactement ce qu'il nous faut pour parler avec les fichiers JSON
imposés par le sujet : si le JSON est cassé → erreur claire au bon
endroit.

### 1.5 Les *imports relatifs*

```python
from .cli import main
from .evaluate import evaluate as _evaluate
```

Le `.` veut dire « **dans le même package** ». Comme on a un package
`student/` (un dossier avec un `__init__.py`), tous ses fichiers se
parlent avec `.`. Le `as _evaluate` est un renommage local pour éviter
qu'une méthode `self.evaluate()` n'écrase la fonction importée.

### 1.6 Les imports *lazy* (paresseux)

Tu vas voir des `import torch` ou `import fire` **à l'intérieur** d'une
fonction, pas en haut du fichier. C'est volontaire :

- `torch` met ~1-2 secondes à s'importer.
- Si tu lances juste `python -m student search ...`, tu n'as pas besoin
  de `torch`. Pourquoi le charger ?
- Solution : on ne l'importe que dans la fonction qui en a besoin.

Côté Python, un `import X` qui a déjà été fait dans le processus est
quasi-gratuit la deuxième fois (c'est mis en cache dans `sys.modules`).

### 1.7 Les *generators* / `yield`

```python
def iter_files(root):
    for ... :
        yield path
```

Une fonction avec `yield` ne s'exécute pas tout de suite. Elle renvoie
un **itérateur** : à chaque appel de `next()`, elle reprend là où elle
s'était arrêtée, retourne la prochaine valeur, et se met en pause.

Avantage : on n'a pas à construire la liste complète en mémoire avant
de pouvoir en lire le premier élément.

### 1.8 Le *dispatcher* Fire

```python
import fire
fire.Fire(CLI)
```

`fire` regarde la classe `CLI`, expose chaque méthode comme une
sous-commande, et mappe `--toto 5` sur l'argument `toto=5`. Donc :

```bash
python -m student index --max_chunk_size 2000 --use_embeddings True
```

devient automatiquement :

```python
CLI().index(max_chunk_size=2000, use_embeddings=True)
```

C'est notre `argparse` mais sans le boilerplate.

### 1.9 BM25 en 3 phrases

BM25 est un algorithme de **recherche par mots-clés**. Pour un mot, il
récompense :

- Sa fréquence dans le document (TF, mais avec saturation).
- Sa rareté dans tout le corpus (IDF — un mot rare est plus
  discriminant).
- Pénalise les documents très longs.

Score final d'un document pour une requête = somme des contributions
de chaque mot de la requête. Pas de sémantique, juste des matches
exacts (après tokenisation/lowercase).

### 1.10 Les *embeddings denses* et la similarité cosinus

Un embedding, c'est un vecteur (genre 384 nombres flottants) qui
**représente le sens** d'un texte. Deux textes au sens proche →
vecteurs proches.

« Proche » se mesure par la **similarité cosinus** : `cos(θ) = (A·B) /
(|A| × |B|)`. Si on a déjà **normalisé** les vecteurs (|A|=|B|=1), il
ne reste qu'à calculer le produit scalaire `A·B`. D'où le `@` numpy
dans le code.

### 1.11 RRF (Reciprocal Rank Fusion)

Quand tu as deux listes de résultats (BM25 + dense), comment les
fusionner ? Les scores BM25 vont de 0 à +∞, les scores cosinus de -1 à
1. Pas comparables.

RRF dit : oublie les scores, regarde juste le **rang**. Chaque
document gagne `1 / (60 + rang)` dans chaque liste où il apparaît. On
somme. On trie par cette somme. C'est très simple et très efficace.

---

<a id="2-entry"></a>
## 2. Point d'entrée — `src/student/__main__.py`

Quand tu tapes `python -m student ...`, Python fait :

1. Cherche le **package** `student`. Ici c'est `src/student/`
   (le `src/` est dans `pyproject.toml`).
2. Exécute le fichier spécial `__main__.py` du package.

Le fichier complet :

```python
"""Module entry point: ``python -m student``."""

from .cli import main

if __name__ == "__main__":
    main()
```

**Ligne par ligne :**

- `"""..."""` : c'est une docstring de module. Pure documentation.
- `from .cli import main` : import relatif (cf §1.5) — on importe la
  fonction `main()` qui vit dans `cli.py`.
- `if __name__ == "__main__":` : ce test est vrai **seulement** quand le
  fichier est lancé directement (par `python -m`), pas quand il est
  importé par un autre fichier. Convention universelle Python.
- `main()` : on appelle la fonction.

C'est tout. Ce fichier est minimaliste exprès : le boulot est dans
`cli.py`.

---

<a id="3-cli"></a>
## 3. `src/student/cli.py` — l'orchestrateur

### 3.1 L'en-tête (lignes 1-30)

```python
from __future__ import annotations

import json
import os
from typing import Optional

from tqdm import tqdm

from .evaluate import evaluate as _evaluate
from .generator import get_generator
from .index import KnowledgeBase
from .models import (
    MinimalAnswer,
    MinimalSearchResults,
    MinimalSource,
    RagDataset,
    StudentSearchResults,
    StudentSearchResultsAndAnswer,
)
```

- `json` : lib standard, gère les fichiers `.json`.
- `os` : lib standard, gère les chemins (`os.path.join`,
  `os.makedirs`, `os.listdir`, `os.path.isdir`...).
- `Optional` : type hint, `Optional[X]` = `X | None` (importé même si
  non utilisé partout — vestige de refactor).
- `tqdm` : la lib qui dessine `[=====>    ] 50%` dans le terminal.
- Les `from .X import Y` : on tire de nos propres sous-modules.

**Pourquoi `as _evaluate` ?** Parce que la classe `CLI` a une méthode
`evaluate()`. Si on importait `evaluate` tout court, le nom serait
masqué par `self.evaluate`. Renommer évite l'ambiguïté.

### 3.2 Constantes

```python
DEFAULT_RAW_DIR = "data/raw/vllm-0.10.1"
DEFAULT_INDEX_DIR = "data/processed"
DEFAULT_OUTPUT_DIR = "data/output"
```

Pure config. Ces strings sont utilisées comme valeurs par défaut des
paramètres CLI plus bas.

### 3.3 La fonction `_resolve_repo(raw_dir)`

But : être tolérant aux différentes manières dont l'utilisateur peut
avoir dézippé le repo. Si tu pointes vers `data/raw/` qui ne contient
qu'un sous-dossier `vllm-0.10.1/`, on descend automatiquement
dedans.

```python
def _resolve_repo(raw_dir: str) -> str:
    if os.path.isdir(raw_dir):
        entries = [e for e in os.listdir(raw_dir) if not e.startswith(".")]
        subdirs = [
            os.path.join(raw_dir, e)
            for e in entries
            if os.path.isdir(os.path.join(raw_dir, e))
        ]
        if len(subdirs) == 1 and not any(
            f.endswith(".py") or f.endswith(".md")
            for f in entries
            if os.path.isfile(os.path.join(raw_dir, f))
        ):
            return subdirs[0]
    return raw_dir
```

Décortiqué :

- `os.path.isdir(raw_dir)` : est-ce un dossier qui existe ?
- `os.listdir(raw_dir)` : liste les noms (pas les chemins complets).
- `if not e.startswith(".")` : on ignore les fichiers cachés
  (`.DS_Store` sur Mac, `.git`...).
- `subdirs` : on garde uniquement les entrées qui sont des dossiers.
  Le `os.path.join(raw_dir, e)` reconstruit le chemin complet pour
  pouvoir tester `isdir`.
- La condition finale : **un seul sous-dossier** ET **aucun fichier
  Python/Markdown à la racine** → c'est un dossier wrapper, on descend
  dedans.
- Sinon, on renvoie tel quel.

Le `_` devant le nom est une convention Python : « fonction interne,
ne l'utilise pas ailleurs ».

### 3.4 La classe `CLI`

Cette classe ne fait **rien** de spécial à part regrouper des méthodes.
Quand Fire reçoit `fire.Fire(CLI)`, il instancie `CLI()` (donc `self`
existe mais ne sert pas) et expose chaque méthode publique
(`index`, `search`, ...) comme une sous-commande.

#### 3.4.1 `CLI.index(...)`

Signature :

```python
def index(
    self,
    repo_path: str = DEFAULT_RAW_DIR,
    save_directory: str = DEFAULT_INDEX_DIR,
    max_chunk_size: int = 2000,
    use_embeddings: bool = False,
    embedder_name: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> str:
```

- Chaque paramètre a une valeur par défaut → tous optionnels en CLI.
- `max_chunk_size=2000` : taille max d'un chunk en caractères.
- `use_embeddings=False` : par défaut on fait du BM25 pur. Mettre
  `True` active la branche **bonus** (sentence-transformers).
- `embedder_name` : le modèle HuggingFace à charger pour les
  embeddings.

Corps :

```python
repo = _resolve_repo(repo_path)
if not os.path.isdir(repo):
    raise FileNotFoundError(f"repo not found: {repo}")
kb = KnowledgeBase.build(
    repo_root=repo,
    max_chunk_size=max_chunk_size,
    use_embeddings=use_embeddings,
    embedder_name=embedder_name,
)
kb.save(save_directory)
msg = f"Ingestion complete! Indices saved under {save_directory}/"
print(msg)
return msg
```

Étape par étape :

1. On résout le chemin réel du repo (cf §3.3).
2. Si le dossier n'existe pas → on lève une exception **explicite**.
3. `KnowledgeBase.build(...)` — c'est ici qu'on plonge dans `index.py`
   (cf §8). `build` est une **méthode de classe** (constructeur
   alternatif).
4. `kb.save(save_directory)` : on persiste sur disque.
5. On imprime un message ET on le retourne. Fire affiche
   automatiquement la valeur de retour, donc tu vois le message à
   l'écran.

#### 3.4.2 `CLI.search(query, ...)`

```python
def search(self, query: str, index_directory: str = DEFAULT_INDEX_DIR,
           k: int = 10, mode: str = "auto") -> str:
    kb = KnowledgeBase.load(index_directory)
    chunks = kb.search(query, k=k, mode=mode)
    sources = [
        MinimalSource(
            file_path=c.file_path,
            first_character_index=c.first_character_index,
            last_character_index=c.last_character_index,
        )
        for c in chunks
    ]
    out = json.dumps([s.model_dump() for s in sources], indent=2)
    print(out)
    return out
```

- `KnowledgeBase.load(...)` : on **recharge** l'index depuis le disque
  (on ne le reconstruit pas — gain énorme).
- `kb.search(...)` retourne une liste de `Chunk` (objets internes).
- La *list comprehension* construit la liste des sources au format
  imposé par le sujet : on **drop** le texte, on ne garde que les
  coordonnées (file_path + offsets).
- `s.model_dump()` (Pydantic) → un dict Python.
- `json.dumps([...], indent=2)` → chaîne JSON joliment formatée.

**Pourquoi `MinimalSource` ?** Parce que le sujet impose ce format
exact en sortie. Le `Chunk` interne contient plus de choses (le texte)
qu'on ne doit pas exposer.

#### 3.4.3 `CLI.search_dataset(dataset_path, ...)`

C'est la commande utilisée pour l'évaluation : on a un fichier
`dataset.json` avec N questions, on lance une recherche pour chacune.

```python
with open(dataset_path, "r", encoding="utf-8") as fh:
    dataset = RagDataset.model_validate_json(fh.read())
kb = KnowledgeBase.load(index_directory)

results: list[MinimalSearchResults] = []
for q in tqdm(dataset.rag_questions, desc="Searching", unit="q"):
    chunks = kb.search(q.question, k=k, mode=mode)
    retrieved = [MinimalSource(...) for c in chunks]
    results.append(
        MinimalSearchResults(
            question_id=q.question_id,
            question=q.question,
            retrieved_sources=retrieved,
        )
    )

payload = StudentSearchResults(search_results=results, k=k)
os.makedirs(save_directory, exist_ok=True)
out_path = os.path.join(save_directory, os.path.basename(dataset_path))
with open(out_path, "w", encoding="utf-8") as fh:
    fh.write(payload.model_dump_json(indent=2))
```

Décortiqué :

- `with open(...) as fh:` : context manager. Le fichier sera **fermé
  automatiquement** même si une exception arrive.
- `RagDataset.model_validate_json(...)` : pydantic parse + valide le
  JSON. Si le format est faux → exception claire.
- `tqdm(dataset.rag_questions, desc="...", unit="q")` : on enveloppe
  l'itérable pour avoir une barre de progression. `desc` et `unit` ne
  changent que l'affichage.
- Pour chaque question on appelle `kb.search` et on construit un
  `MinimalSearchResults`.
- À la fin, `payload.model_dump_json(indent=2)` sérialise en JSON.
- `os.makedirs(..., exist_ok=True)` crée le dossier s'il n'existe pas
  (et ne crashe pas s'il existe déjà).
- `os.path.basename(dataset_path)` extrait juste le nom du fichier (ex:
  `dataset.json` à partir de `data/raw/dataset.json`).

#### 3.4.4 `CLI.answer(question, ...)`

```python
kb = KnowledgeBase.load(index_directory)
chunks = kb.search(question, k=k, mode=mode)
gen = get_generator(max_context_length=max_context_length)
text = gen.generate(question, chunks)
print(text)
```

Très simple : retrieve + generate. `get_generator` est un **singleton**
(cf §9) — la première fois ça charge le modèle, les fois suivantes c'est
gratuit.

#### 3.4.5 `CLI.answer_dataset(...)`

Variante batch. Subtilité importante :

```python
chunks_by_offset = {
    (c.file_path, c.first_character_index, c.last_character_index): c
    for c in kb.chunks
}
```

C'est un **dict comprehension** dont la **clé est un tuple à 3
éléments** (le file_path et les deux offsets). Pourquoi ? Parce que les
fichiers JSON de search ne contiennent que des `MinimalSource` (pas le
texte). Pour donner du contexte au LLM il faut **retrouver** le `Chunk`
complet (avec son `.text`). Ce dict permet une lookup O(1).

```python
for s in sr.retrieved_sources:
    key = (s.file_path, s.first_character_index, s.last_character_index)
    chunk = chunks_by_offset.get(key)
    if chunk is not None:
        ctx.append(chunk)
```

Pour chaque source du JSON, on reconstruit la clé et on retrouve le
Chunk avec son texte.

#### 3.4.6 `CLI.evaluate(...)`

Wrapper : appelle `evaluate.evaluate(...)` (notre fonction renommée en
`_evaluate` à l'import) et affiche `report.pretty()`.

Le `_ = (k, max_context_length)` est une astuce pour **marquer**
explicitement que ces arguments existent dans la signature mais qu'on
ne les utilise pas. Évite un warning du linter.

### 3.5 La fonction `main()`

```python
def main() -> None:
    import fire  # type: ignore
    fire.Fire(CLI)
```

- L'import de `fire` est dans la fonction → on ne le charge que si on
  appelle vraiment `main()`. Si quelqu'un importe `cli.py` depuis un
  test unitaire, on évite l'import de Fire.
- `# type: ignore` : commentaire pour mypy (« je sais que ce module n'a
  pas de stubs, ne te plains pas »).
- `fire.Fire(CLI)` : c'est la magie. Fire lit `sys.argv`, instancie
  `CLI()`, appelle la méthode demandée avec les bons arguments.

---

<a id="4-models"></a>
## 4. `src/student/models.py` — les contrats de données

Tous les JSON qui entrent / sortent du programme sont validés ici.

### 4.1 `MinimalSource`

```python
class MinimalSource(BaseModel):
    file_path: str
    first_character_index: int
    last_character_index: int
```

Une source = un emplacement dans un fichier (chemin + intervalle de
caractères `[first, last)`). Format imposé par le sujet.

### 4.2 `UnansweredQuestion`

```python
class UnansweredQuestion(BaseModel):
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
```

- `Field(default_factory=...)` : si `question_id` n'est pas fourni,
  Pydantic appelle la fonction (ici un lambda) pour générer une valeur.
- **Pourquoi `default_factory` et pas `default=str(uuid.uuid4())` ?**
  Parce que `str(uuid.uuid4())` serait évalué **une seule fois** (au
  moment du `class` statement). Toutes les instances partageraient le
  même UUID — bug catastrophique. `default_factory` est rappelé pour
  chaque instance.

### 4.3 `AnsweredQuestion(UnansweredQuestion)`

Héritage. Cette classe a **tous** les champs d'`UnansweredQuestion`
(`question_id`, `question`) PLUS :

- `sources: List[MinimalSource]` — la vérité terrain (les chunks qui
  contiennent la réponse).
- `answer: str` — la réponse attendue.

### 4.4 `RagDataset`

```python
class RagDataset(BaseModel):
    rag_questions: List[Union[AnsweredQuestion, UnansweredQuestion]]
```

`Union[A, B]` = soit A, soit B. Pydantic essaie **A d'abord** puis B
en fallback. Donc une question qui a `sources` et `answer` → parsée
comme `AnsweredQuestion`. Sinon → `UnansweredQuestion`.

### 4.5 Les enveloppes de sortie

```python
class MinimalSearchResults(BaseModel):
    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]

class MinimalAnswer(MinimalSearchResults):
    answer: str

class StudentSearchResults(BaseModel):
    search_results: List[MinimalSearchResults]
    k: int

class StudentSearchResultsAndAnswer(StudentSearchResults):
    search_results: List[MinimalAnswer]  # override
```

C'est un système de types « par couches » :

- `MinimalSearchResults` = ce qu'on retourne pour **une** question.
- `MinimalAnswer` = pareil + la réponse générée.
- `StudentSearchResults` = la liste **complète** + le `k` utilisé
  (c'est ce qu'on sauvegarde dans le fichier de sortie).
- `StudentSearchResultsAndAnswer` = idem mais avec les réponses.

Le `# type: ignore[assignment]` muet mypy qui n'aime pas qu'on
réécrase un type dans une sous-classe.

---

<a id="5-ingest"></a>
## 5. `src/student/ingest.py` — parcourir le repo

### 5.1 Constantes

```python
ALLOWED_EXTENSIONS = (".py", ".md", ".markdown", ".rst", ".txt")
SKIP_DIRS = {".git", "__pycache__", ".mypy_cache", ".pytest_cache",
             "node_modules", ".venv", "venv", "build", "dist", ".tox"}
```

- `ALLOWED_EXTENSIONS` est un **tuple** (parenthèses) parce qu'on
  l'utilise avec `.endswith(tuple)` qui accepte plusieurs suffixes.
- `SKIP_DIRS` est un **set** (accolades) parce qu'on fait des `in
  SKIP_DIRS` — c'est O(1) sur un set, O(n) sur une liste.

### 5.2 `iter_files(root)` — un générateur

```python
def iter_files(root: str) -> Iterator[str]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.lower().endswith(ALLOWED_EXTENSIONS):
                yield os.path.join(dirpath, name)
```

`os.walk(root)` est un générateur qui yield un tuple `(dirpath,
dirnames, filenames)` pour chaque dossier qu'il visite, récursivement :

- `dirpath` : chemin du dossier actuel (string).
- `dirnames` : liste des sous-dossiers immédiats.
- `filenames` : liste des fichiers immédiats.

**Le piège** : `dirnames[:] = ...`. Cette syntaxe modifie la liste **en
place** (pas une nouvelle liste). C'est crucial parce que `os.walk`
relit `dirnames` après l'avoir yieldé. Si tu modifies `dirnames` en
place pour enlever `.git`, **il n'y descendra pas**. Si tu faisais
juste `dirnames = [...]`, tu créerais une nouvelle variable locale
sans affecter `os.walk`.

Pour chaque fichier, si l'extension est dans la liste, on `yield` le
chemin absolu (`os.path.join(dirpath, name)`).

### 5.3 `read_file_safely(path)`

```python
try:
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        return fh.read()
except OSError:
    return ""
```

- `errors="ignore"` : si un octet n'est pas du UTF-8 valide (rare), on
  l'ignore au lieu de crasher.
- `OSError` couvre : permission refusée, fichier disparu entre `walk`
  et `open`, etc.
- En cas d'erreur on retourne une string vide, qui sera filtrée plus
  haut.

### 5.4 `collect_files(root, relative_to=None)`

```python
def collect_files(root, relative_to=None):
    base = relative_to or root
    files = []
    paths = list(iter_files(root))
    for abs_path in tqdm(paths, desc="Reading files", unit="file"):
        text = read_file_safely(abs_path)
        if not text.strip():
            continue
        rel = os.path.relpath(abs_path, base)
        files.append((rel, text))
    return files
```

- `list(iter_files(root))` : on consomme le générateur en une liste,
  parce qu'on veut connaître la taille totale pour la progress bar.
- `text.strip()` : si le fichier est vide ou ne contient que des
  espaces → on saute.
- `os.path.relpath(abs_path, base)` : transforme un chemin absolu en
  chemin relatif à `base`. Crucial parce que les ground truth utilisent
  des chemins relatifs (`vllm/foo.py`, pas `/home/user/.../vllm/foo.py`).

Retour : `[(rel_path, text), ...]`.

---

<a id="6-chunking"></a>
## 6. `src/student/chunking.py` — découper en morceaux

C'est le module le plus subtil. Pourquoi découper ? Parce qu'on ne peut
pas balancer un fichier de 5000 lignes dans BM25 ou dans un LLM. On veut
des morceaux de ~2000 caractères qui ont du sens.

### 6.1 La dataclass `Chunk`

```python
@dataclass
class Chunk:
    file_path: str
    first_character_index: int
    last_character_index: int
    text: str

    def char_len(self) -> int:
        return self.last_character_index - self.first_character_index
```

Note : on stocke **à la fois** le texte ET les offsets. Les offsets
servent à l'évaluation (overlap avec la ground truth), le texte sert au
LLM et à la tokenization.

### 6.2 `_split_oversized` — fenêtre glissante avec recouvrement

Cas d'usage : on a un bloc (par exemple une grosse classe Python) qui
dépasse `max_chunk_size`. On le coupe en sous-morceaux qui se
recouvrent un peu pour ne pas couper en plein milieu d'un concept.

```python
def _split_oversized(file_path, text, start, end, max_chunk_size):
    chunks = []
    size = end - start
    if size <= max_chunk_size:
        return [Chunk(file_path, start, end, text[start:end])]

    overlap = max_chunk_size // 10        # 10% de recouvrement
    step = max_chunk_size - overlap        # on avance de 90%
    pos = start
    while pos < end:
        sub_end = min(pos + max_chunk_size, end)
        chunks.append(Chunk(file_path, pos, sub_end, text[pos:sub_end]))
        if sub_end >= end:
            break
        pos += step
    return chunks
```

Imagine `max=2000`, donc `overlap=200`, `step=1800`. Si la zone fait
5000 caractères :

- Chunk 1 : [0, 2000]
- Chunk 2 : [1800, 3800]  ← chevauchement avec chunk 1 sur 200 chars
- Chunk 3 : [3600, 5000]

Le chevauchement évite que la phrase à la frontière soit invisible dans
les deux chunks.

### 6.3 `chunk_python` — parsing AST

L'idée : pour un fichier Python, plutôt que de couper aveuglément à
2000 caractères, on coupe **aux frontières naturelles** (fonctions,
classes).

```python
try:
    tree = ast.parse(text)
except SyntaxError:
    return chunk_text(file_path, text, max_chunk_size)
```

- `ast.parse` lit le code Python et retourne un arbre syntaxique.
- Si la syntaxe est cassée (ex. fichier corrompu) → fallback texte.

```python
lines = text.split("\n")
line_offsets = [0]
for line in lines:
    line_offsets.append(line_offsets[-1] + len(line) + 1)
```

On précalcule un tableau `line_offsets` tel que `line_offsets[i]` =
nombre de caractères avant le début de la ligne `i+1`. Le `+1` du
`\n`.

Exemple : `"foo\nbar\nbaz"`
- ligne 0 : "foo" → commence à 0
- ligne 1 : "bar" → commence à 4 (3 chars + \n)
- ligne 2 : "baz" → commence à 8
- fin     : 11

`line_offsets = [0, 4, 8, 11]`.

```python
def lc_to_offset(lineno: int, col: int) -> int:
    idx = max(0, min(lineno - 1, len(line_offsets) - 1))
    return min(line_offsets[idx] + col, len(text))
```

Convertit un couple `(lineno, col)` (donné par l'AST, **1-based**) en
offset caractère absolu. Le `max(0, min(...))` est une garde pour ne
pas sortir des bornes.

```python
top_level = [
    node for node in tree.body
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
]
```

`tree.body` est la liste des nœuds de premier niveau du module. On ne
garde que les fonctions (sync et async) et les classes. Les `import`,
constantes etc. sont **traités séparément** comme « préambule ».

```python
cursor = 0
for node in top_level:
    start = lc_to_offset(node.lineno, node.col_offset)
    end_lineno = getattr(node, "end_lineno", node.lineno) or node.lineno
    end_col = getattr(node, "end_col_offset", 0) or 0
    end = lc_to_offset(end_lineno, end_col)

    if start > cursor:
        pre = text[cursor:start].strip()
        if pre:
            chunks.extend(
                _split_oversized(file_path, text, cursor, start, max_chunk_size)
            )
    chunks.extend(
        _split_oversized(file_path, text, start, end, max_chunk_size)
    )
    cursor = end
```

C'est une boucle qui balaie le fichier dans l'ordre :

1. `cursor` = position où on est rendu (initialement 0).
2. Pour chaque fonction/classe `node` :
   - `start, end` = offsets dans le fichier.
   - Si `start > cursor` → il y a du texte entre la fin du dernier
     bloc et le début de celui-ci (typiquement des imports ou des
     constantes). On l'ajoute comme « préambule ».
   - Puis on ajoute le bloc lui-même (potentiellement sub-splitté).
   - On avance `cursor` à `end`.

`getattr(node, "end_lineno", node.lineno)` : sur des très vieux Python
les nœuds AST n'ont pas `end_lineno`. C'est une garde défensive. Le
`or node.lineno` couvre le cas où c'est 0/None.

```python
if cursor < len(text):
    tail = text[cursor:].strip()
    if tail:
        chunks.extend(
            _split_oversized(file_path, text, cursor, len(text), max_chunk_size)
        )
```

Après la boucle : s'il y a encore du texte (post-ambule, ex: `if
__name__ == "__main__":` après les classes) → on l'ajoute.

```python
if not chunks:
    chunks = _split_oversized(file_path, text, 0, len(text), max_chunk_size)
return [c for c in chunks if c.text.strip()]
```

Sécurité : si le fichier n'avait aucune fonction/classe (cas d'un
script flat), `chunks` serait vide → on fallback au split brut. Et on
filtre les chunks qui ne contiennent que des espaces.

### 6.4 `chunk_markdown` — par sections

```python
section_starts = []
for i, line in enumerate(lines):
    if line.lstrip().startswith("#"):
        section_starts.append(line_offsets[i])
if not section_starts or section_starts[0] != 0:
    section_starts.insert(0, 0)
```

On parcourt ligne par ligne. Si une ligne commence par `#` (après
strip à gauche) → c'est un header → on note l'offset de cette ligne.
Si aucun header au début, on insère un 0 (le tout début du fichier).

```python
boundaries = section_starts + [len(text)]
for i in range(len(boundaries) - 1):
    start, end = boundaries[i], boundaries[i + 1]
    if text[start:end].strip():
        chunks.extend(_split_oversized(file_path, text, start, end, max_chunk_size))
```

Avec `boundaries = [0, 50, 200, 1000, len(text)]`, on extrait chaque
section.

### 6.5 `chunk_text` et `chunk_file`

`chunk_text` : sliding window pur (`_split_oversized` sur tout le
fichier).

`chunk_file` : dispatcher.

```python
lower = file_path.lower()
if lower.endswith(".py"):
    return chunk_python(...)
if lower.endswith((".md", ".markdown", ".rst")):
    return chunk_markdown(...)
return chunk_text(...)
```

---

<a id="7-tokenizer"></a>
## 7. `src/student/tokenizer.py` — texte → mots

BM25 a besoin de **mots** (tokens), pas de texte brut. Et nos « mots »
doivent être adaptés au code : `getUserName` doit donner `["get",
"user", "name"]` pour que la requête `"get user name"` matche.

### 7.1 Les regex

```python
_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_SPLIT_RE = re.compile(r"[^A-Za-z0-9]+")
```

`_SPLIT_RE` : tout ce qui n'est pas alphanumérique sert de séparateur
(espaces, ponctuation, underscores, slashes...).

`_CAMEL_RE` est plus subtil. C'est une regex de **frontière** (sans
consommer de caractère) basée sur des *lookbehind* `(?<=...)` et des
*lookahead* `(?=...)`.

Deux alternatives séparées par `|` :

1. `(?<=[a-z0-9])(?=[A-Z])` : entre une lettre minuscule/chiffre et
   une majuscule. Match dans `getName` entre `t` et `N`.
2. `(?<=[A-Z])(?=[A-Z][a-z])` : entre une majuscule et une majuscule
   suivie d'une minuscule. Match dans `HTTPServer` entre `P` et `S`.
   Permet de séparer l'acronyme du mot.

Donc `re.split(_CAMEL_RE, "HTTPServerName")` → `["HTTP", "Server",
"Name"]`. Magique.

### 7.2 La fonction `tokenize`

```python
def tokenize(text: str) -> List[str]:
    if not text:
        return []
    parts = _SPLIT_RE.split(text)
    tokens = []
    for part in parts:
        if not part:
            continue
        for sub in _CAMEL_RE.split(part):
            sub_lower = sub.lower()
            if len(sub_lower) < 2:
                continue
            if sub_lower in _STOPWORDS:
                continue
            tokens.append(sub_lower)
    return tokens
```

1. Premier split sur non-alphanum → `["the", "getUserName", "is",
   "cool"]`.
2. Pour chaque morceau, on re-split sur camelCase → `["get", "User",
   "Name"]` pour `getUserName`.
3. Lowercase, filtre les tokens trop courts (1 char), filtre les
   stopwords (« the », « a », « is »...).

`tokenize_batch` applique `tokenize` à une liste.

---

<a id="8-index"></a>
## 8. `src/student/index.py` — le cœur du retrieval

### 8.1 Setup

```python
try:
    import bm25s
except ImportError as exc:
    raise RuntimeError(
        "bm25s is required. Install it via `uv sync`."
    ) from exc
```

`bm25s` est la lib BM25 ultrarapide. Si l'import rate → message clair.
Le `from exc` chaîne l'exception originale pour le debug.

```python
CHUNKS_FILENAME = "chunks.json"
BM25_DIRNAME = "bm25_index"
DENSE_DIRNAME = "dense_index"
META_FILENAME = "meta.json"
```

Noms des fichiers/dossiers sur disque. Centraliser ces strings évite
les fautes de frappe entre `save` et `load`.

### 8.2 La classe `KnowledgeBase`

```python
def __init__(
    self,
    chunks: List[Chunk],
    bm25: "bm25s.BM25",
    dense_embeddings: Optional[np.ndarray] = None,
    embedder_name: Optional[str] = None,
) -> None:
    self.chunks = chunks
    self.bm25 = bm25
    self.dense_embeddings = dense_embeddings
    self.embedder_name = embedder_name
    self._embedder = None  # lazy
```

Note : `bm25s.BM25` est entre guillemets pour le typage parce que
`bm25s` est importé conditionnellement. Le `_embedder = None` permet
de ne charger le modèle qu'à la première recherche dense (cf §8.5).

### 8.3 `KnowledgeBase.build` — la pipeline d'indexation

```python
@classmethod
def build(cls, repo_root, max_chunk_size=2000, use_embeddings=False,
          embedder_name="sentence-transformers/all-MiniLM-L6-v2"):
    print(f"[index] scanning {repo_root}")
    files = collect_files(repo_root, relative_to=repo_root)
    print(f"[index] {len(files)} files to chunk")

    chunks: List[Chunk] = []
    for rel_path, text in tqdm(files, desc="Chunking", unit="file"):
        chunks.extend(chunk_file(rel_path, text, max_chunk_size))
    print(f"[index] {len(chunks)} chunks created")

    corpus_tokens = tokenize_batch([c.text for c in chunks])
    bm25 = bm25s.BM25()
    bm25.index(corpus_tokens, show_progress=True)

    dense: Optional[np.ndarray] = None
    if use_embeddings:
        dense = _encode_corpus(chunks, embedder_name)

    return cls(chunks, bm25, dense, embedder_name if use_embeddings else None)
```

`@classmethod` : c'est une méthode qui reçoit la **classe** comme
premier argument (`cls`) au lieu d'une instance. Pratique pour faire
des constructeurs alternatifs : `KnowledgeBase.build(...)` →
`KnowledgeBase(chunks, bm25, ...)`.

Étapes :

1. `collect_files` retourne `[(rel_path, text), ...]` (cf §5).
2. Pour chaque fichier, `chunk_file` retourne une liste de `Chunk`.
   `chunks.extend(...)` les ajoute à la liste globale (`extend` ≠
   `append` : extend déplie l'itérable).
3. `tokenize_batch([c.text for c in chunks])` → liste de listes de
   tokens.
4. `bm25s.BM25()` crée un objet vide. `.index(...)` construit l'index
   (calcule TF, IDF, longueurs moyennes).
5. Si `use_embeddings=True` → on encode tous les chunks (bonus).
6. On retourne une instance via `cls(...)` (équivalent à
   `KnowledgeBase(...)`).

### 8.4 Persistance — `save` et `load`

```python
def save(self, directory):
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, CHUNKS_FILENAME), "w", encoding="utf-8") as fh:
        json.dump([asdict(c) for c in self.chunks], fh)

    bm25_dir = os.path.join(directory, BM25_DIRNAME)
    os.makedirs(bm25_dir, exist_ok=True)
    self.bm25.save(bm25_dir)

    meta = {"embedder_name": self.embedder_name,
            "n_chunks": str(len(self.chunks))}
    with open(os.path.join(directory, META_FILENAME), "w", encoding="utf-8") as fh:
        json.dump(meta, fh)

    if self.dense_embeddings is not None:
        os.makedirs(os.path.join(directory, DENSE_DIRNAME), exist_ok=True)
        np.save(os.path.join(directory, DENSE_DIRNAME, "embeddings.npy"),
                self.dense_embeddings)
```

- `asdict(c)` (de `dataclasses`) convertit un `Chunk` en dict.
- `bm25s.BM25.save(dir)` est fourni par la lib — elle écrit ses fichiers
  binaires.
- `np.save(...)` écrit la matrice numpy en format `.npy` (binaire
  compact, rechargement instantané).

```python
@classmethod
def load(cls, directory):
    with open(os.path.join(directory, CHUNKS_FILENAME), "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    chunks = [Chunk(**c) for c in raw]

    bm25_dir = os.path.join(directory, BM25_DIRNAME)
    bm25 = bm25s.BM25.load(bm25_dir, load_corpus=False)

    meta_path = os.path.join(directory, META_FILENAME)
    embedder_name = None
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as fh:
            meta = json.load(fh)
            embedder_name = meta.get("embedder_name")

    dense = None
    dense_path = os.path.join(directory, DENSE_DIRNAME, "embeddings.npy")
    if os.path.exists(dense_path):
        dense = np.load(dense_path)

    return cls(chunks, bm25, dense, embedder_name)
```

Symétrique. À noter :

- `Chunk(**c)` : *unpacking* du dict en arguments nommés. Si `c =
  {"file_path": "x", "first_character_index": 0, ...}` alors
  `Chunk(**c)` ≡ `Chunk(file_path="x", first_character_index=0, ...)`.
- `meta.get("embedder_name")` : `.get()` ne crashe pas si la clé
  manque, renvoie `None`.

### 8.5 `search_bm25`

```python
def search_bm25(self, query: str, k: int = 10):
    if not query.strip():
        return []
    tokens = tokenize(query)
    if not tokens:
        return []
    docs, scores = self.bm25.retrieve(
        [tokens],
        k=min(k, len(self.chunks)),
        show_progress=False,
    )
    out = []
    for idx, score in zip(docs[0], scores[0]):
        out.append((int(idx), float(score)))
    return out
```

- `[tokens]` : on emballe dans une liste parce que `bm25s.retrieve`
  accepte un **batch** de requêtes (utile pour traiter 100 questions en
  une fois). Comme on n'en a qu'une, on prend `docs[0]` et
  `scores[0]`.
- `min(k, len(...))` : ne demande pas plus de résultats qu'il n'y a de
  chunks (sinon bm25s peut crash).
- Conversion explicite `int()` / `float()` parce que `bm25s` renvoie
  des types numpy (numpy.int64, numpy.float32) qui peuvent surprendre
  en aval (JSON ne sait pas sérialiser numpy.int64).

### 8.6 `_get_embedder` (lazy)

```python
def _get_embedder(self):
    if self._embedder is None:
        from sentence_transformers import SentenceTransformer
        assert self.embedder_name is not None
        self._embedder = SentenceTransformer(self.embedder_name)
    return self._embedder
```

Premier appel → on charge le modèle (lent, qq secondes). Appels
suivants → on retourne l'instance cachée. `assert` rejette le cas où
on demande dense sans avoir d'embedder configuré.

### 8.7 `search_dense`

```python
def search_dense(self, query, k=10):
    if self.dense_embeddings is None or self.embedder_name is None:
        return []
    embedder = self._get_embedder()
    q_vec = embedder.encode([query], normalize_embeddings=True)
    sims = self.dense_embeddings @ q_vec[0]
    top_n = min(k, len(self.chunks))
    idxs = np.argpartition(-sims, top_n - 1)[:top_n]
    idxs = idxs[np.argsort(-sims[idxs])]
    return [(int(i), float(sims[i])) for i in idxs]
```

Décortiqué :

- `embedder.encode([query], normalize_embeddings=True)` : retourne une
  matrice `(1, dim)`. Le `normalize=True` force `|v|=1` → cosine =
  produit scalaire.
- `q_vec[0]` : on prend le seul vecteur (dim `(dim,)`).
- `self.dense_embeddings` est `(N, dim)`. `dense @ q_vec[0]` est un
  produit matrice × vecteur → résultat de taille `(N,)` (un score par
  chunk).
- `np.argpartition(-sims, top_n - 1)` : trouve les `top_n` indices qui
  ont les scores les plus **petits** dans `-sims`, donc les **plus
  grands** dans `sims`. **Pas trié** entre eux. Complexité O(N) (au
  lieu de O(N log N) pour un tri complet).
- `[:top_n]` : on garde ces indices.
- `np.argsort(-sims[idxs])` : trie maintenant **uniquement** ces top_n
  par score décroissant. O(top_n log top_n) — négligeable.
- `idxs[np.argsort(-sims[idxs])]` : applique la permutation aux
  indices.

C'est l'idiome canonique pour « trouver les k plus grands dans une
liste » en numpy.

### 8.8 `search_hybrid` — Reciprocal Rank Fusion

```python
def search_hybrid(self, query, k=10, rrf_k=60):
    pool = max(k * 4, 20)
    bm25_hits = self.search_bm25(query, k=pool)
    dense_hits = self.search_dense(query, k=pool) if self.dense_embeddings is not None else []

    scores = {}
    for rank, (idx, _) in enumerate(bm25_hits):
        scores[idx] = scores.get(idx, 0.0) + 1.0 / (rrf_k + rank + 1)
    for rank, (idx, _) in enumerate(dense_hits):
        scores[idx] = scores.get(idx, 0.0) + 1.0 / (rrf_k + rank + 1)

    if not scores:
        return []
    ranked = sorted(scores.items(), key=lambda x: -x[1])[:k]
    return ranked
```

- `pool = max(k*4, 20)` : on demande plus de candidats par méthode
  qu'on n'en retournera, parce que les deux listes peuvent recommander
  des chunks différents.
- `enumerate(bm25_hits)` : retourne `(0, premier), (1, deuxième), ...`
- La formule RRF : `score += 1 / (60 + rang + 1)`. Le `+1` est parce
  que rang commence à 0 ; on veut diviser par 61, 62, 63... (jamais
  zéro).
- Si un chunk est en première position dans les deux listes, il gagne
  `1/61 + 1/61 ≈ 0.033`. Si juste BM25, `1/61 ≈ 0.016`. Donc présents
  dans les deux → boost.
- `scores.items()` → liste de paires `(idx, score)`. `sorted(...,
  key=lambda x: -x[1])` trie par score décroissant (moins-score
  croissant). `[:k]` garde les top-k.

### 8.9 `search` — le dispatcher

```python
def search(self, query, k=10, mode="auto"):
    if mode == "auto":
        mode = "hybrid" if self.dense_embeddings is not None else "bm25"
    if mode == "bm25":
        hits = self.search_bm25(query, k)
    elif mode == "dense":
        hits = self.search_dense(query, k)
    else:
        hits = self.search_hybrid(query, k)
    return [self.chunks[idx] for idx, _ in hits]
```

- Mode `auto` : on prend hybrid si on a des embeddings, sinon bm25.
- À la fin on transforme `[(idx, score), ...]` en `[Chunk, ...]` via
  `self.chunks[idx]`. On jette les scores parce que le sujet ne les
  demande pas.

### 8.10 `_encode_corpus`

```python
def _encode_corpus(chunks, model_name):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)
    texts = [c.text for c in chunks]
    vectors = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return np.asarray(vectors, dtype=np.float32)
```

- `batch_size=64` : on encode 64 textes à la fois (compromis
  RAM/vitesse).
- `convert_to_numpy=True` : pas de tensor PyTorch, on veut du numpy.
- `dtype=np.float32` : compact (4 octets/nombre vs 8 pour float64).
  Économise 50% de mémoire/disque.

---

<a id="9-generator"></a>
## 9. `src/student/generator.py` — faire répondre un LLM

### 9.1 Le prompt système

```python
SYSTEM_PROMPT = (
    "You are a precise technical assistant. Answer the user's question using "
    "ONLY the provided context snippets. Be concise, source-grounded, and "
    "self-contained. If the answer is not present in the context, say so."
)
```

Une string multi-ligne via concaténation implicite (Python colle deux
strings adjacentes en une seule). Pas de `\n` au milieu — c'est une
phrase fluide.

L'objectif : forcer le modèle à **se baser sur le contexte** (réduire
les hallucinations) et à reconnaître l'absence d'info.

### 9.2 La classe `AnswerGenerator`

```python
def __init__(self, model_name=DEFAULT_MODEL, max_new_tokens=256,
             max_context_length=2000):
    self.model_name = model_name
    self.max_new_tokens = max_new_tokens
    self.max_context_length = max_context_length
    self._tokenizer = None
    self._model = None
```

Pareil : `_tokenizer = None` et `_model = None` pour le **lazy
loading**. Le constructeur est ultra-léger, ne charge rien.

### 9.3 `_load`

```python
def _load(self):
    if self._model is not None:
        return
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    self._model = AutoModelForCausalLM.from_pretrained(
        self.model_name,
        torch_dtype=dtype,
        device_map="auto" if torch.cuda.is_available() else None,
    )
    if not torch.cuda.is_available():
        self._model.to("cpu")
```

- Premier appel : on charge. Appels suivants : ré-entrée et `return`.
- `AutoTokenizer.from_pretrained` télécharge (si pas en cache) le
  tokenizer correspondant au modèle.
- `torch.float16` vs `torch.float32` : sur GPU, FP16 prend 2× moins de
  RAM. Sur CPU, FP16 est lent (pas supporté hardware) → on garde FP32.
- `device_map="auto"` : Hugging Face place automatiquement les poids
  sur les GPU disponibles.

### 9.4 `_format_context`

```python
def _format_context(self, chunks):
    parts = []
    for i, c in enumerate(chunks, 1):
        text = c.text
        if len(text) > self.max_context_length:
            text = text[: self.max_context_length]
        parts.append(
            f"[Source {i}] {c.file_path}"
            f" ({c.first_character_index}-{c.last_character_index}):\n{text}"
        )
    return "\n\n".join(parts)
```

- `enumerate(chunks, 1)` : énumère à partir de 1 (au lieu de 0).
- On tronque le texte à `max_context_length` (évite de remplir tout le
  contexte du LLM avec un seul chunk).
- Format final :

```
[Source 1] vllm/foo.py (123-456):
def foo(): ...

[Source 2] docs/bar.md (0-200):
# Bar
...
```

Le préfixe `[Source N]` aide le modèle à citer ses sources.

### 9.5 `generate`

```python
def generate(self, question, chunks):
    self._load()
    assert self._tokenizer is not None and self._model is not None

    context = self._format_context(chunks) if chunks else "(no context)"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Context:\n{context}\n\n"
                f"Question: {question}\n\n"
                "Answer the question using only the context above."
            ),
        },
    ]
    prompt = self._tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
    import torch

    with torch.no_grad():
        output = self._model.generate(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            do_sample=False,
            temperature=0.0,
            pad_token_id=self._tokenizer.eos_token_id,
        )
    generated = output[0][inputs["input_ids"].shape[-1]:]
    text = self._tokenizer.decode(generated, skip_special_tokens=True).strip()
    return text
```

Décortiqué :

- `messages = [...]` : format chat standard (rôle + contenu) attendu
  par les modèles instruct modernes.
- `apply_chat_template` : transforme cette liste en string brute avec
  les balises spéciales du modèle (`<|im_start|>system\n...`,
  `<|im_end|>`...). Sans ça, le modèle ne sait pas où s'arrête le
  prompt et où il doit commencer à répondre.
- `tokenize=False` : on garde le résultat en string (on tokenisera
  juste après).
- `add_generation_prompt=True` : ajoute le « préfixe » qui dit au
  modèle « à toi de jouer maintenant ».
- `enable_thinking=False` : Qwen3 peut faire du *chain-of-thought*
  interne. Pour notre cas (réponses courtes, déterministes) on désactive.
- `return_tensors="pt"` : retourne des tensors PyTorch.
- `.to(self._model.device)` : déplace les tensors sur le bon device
  (GPU si dispo).
- `torch.no_grad()` : on ne va pas entraîner → pas besoin de calculer
  les gradients → grosse économie de RAM.
- `do_sample=False, temperature=0.0` : génération **gloutonne**,
  déterministe (à chaque pas on prend le token le plus probable).
- `pad_token_id=eos_token_id` : pour éviter un warning quand le tokenizer
  n'a pas de pad token défini.

```python
generated = output[0][inputs["input_ids"].shape[-1]:]
```

- `output` est de taille `(batch_size=1, total_tokens)`.
- `output[0]` → vecteur de tokens.
- `inputs["input_ids"].shape[-1]` → la longueur du prompt.
- `output[0][longueur_prompt:]` → uniquement les tokens **générés** (on
  drop le prompt).

- `decode(..., skip_special_tokens=True)` : transforme les IDs en
  string, sans les `<|im_end|>` et compagnie.

### 9.6 Le singleton

```python
_singleton: Optional[AnswerGenerator] = None

def get_generator(model_name=DEFAULT_MODEL, max_context_length=2000):
    global _singleton
    if _singleton is None or _singleton.model_name != model_name:
        _singleton = AnswerGenerator(
            model_name=model_name,
            max_context_length=max_context_length,
        )
    return _singleton
```

- `_singleton` est une variable globale module-level.
- `global _singleton` dans la fonction permet de la **réaffecter**
  (sinon Python créerait une variable locale).
- Premier appel : on crée. Appels suivants : on renvoie l'instance
  existante.
- Si on change de modèle (rare) : on recrée.

Note : le modèle lui-même n'est chargé qu'au premier `generate()` via
`_load()`. Donc `get_generator()` reste très rapide.

---

<a id="10-evaluate"></a>
## 10. `src/student/evaluate.py` — la métrique recall@k

### 10.1 Le seuil

```python
OVERLAP_THRESHOLD = 0.05
```

Un chunk retrouvé compte comme « match » s'il couvre **au moins 5%**
de la longueur de la ground-truth.

### 10.2 `overlap_ratio`

```python
def overlap_ratio(retrieved: MinimalSource, truth: MinimalSource) -> float:
    if retrieved.file_path != truth.file_path:
        return 0.0
    truth_len = max(1, truth.last_character_index - truth.first_character_index)
    lo = max(retrieved.first_character_index, truth.first_character_index)
    hi = min(retrieved.last_character_index, truth.last_character_index)
    inter = max(0, hi - lo)
    return inter / truth_len
```

Calcule l'intersection de deux intervalles `[a, b]` et `[c, d]` :
- début de l'intersection : `max(a, c)`
- fin de l'intersection : `min(b, d)`
- longueur : `max(0, fin - début)` (le `max(0, ...)` parce que si fin
  < début, il n'y a pas d'intersection).

Ratio = longueur de l'intersection / longueur de la truth. Le
`max(1, ...)` évite la division par zéro.

### 10.3 `question_recall`

```python
def question_recall(retrieved, truth, k):
    if not truth:
        return 0.0
    top = retrieved[:k]
    found = 0
    for t in truth:
        for r in top:
            if overlap_ratio(r, t) >= OVERLAP_THRESHOLD:
                found += 1
                break
    return found / len(truth)
```

Pour chaque truth, on cherche au moins **un** retrieved qui la couvre
à ≥ 5%. `break` quitte la boucle interne dès qu'on en a trouvé un.

Recall = fraction des truths qui ont été retrouvées.

### 10.4 `evaluate`

```python
def evaluate(student_results_path, dataset_path, ks=(1, 3, 5, 10)):
    with open(student_results_path) as fh:
        student = StudentSearchResults.model_validate_json(fh.read())
    with open(dataset_path) as fh:
        dataset = RagDataset.model_validate_json(fh.read())

    truth_by_id = {}
    for q in dataset.rag_questions:
        if isinstance(q, AnsweredQuestion):
            truth_by_id[q.question_id] = q.sources

    sums = {k: 0.0 for k in ks}
    n = 0
    for sr in student.search_results:
        truth = truth_by_id.get(sr.question_id)
        if not truth:
            continue
        n += 1
        for k in ks:
            sums[k] += question_recall(sr.retrieved_sources, truth, k)
    avg = {k: (sums[k] / n if n else 0.0) for k in ks}
    return EvalReport(n_questions=n, recall_at=avg)
```

- On charge les deux fichiers JSON via pydantic.
- `truth_by_id` : dict `question_id → list[MinimalSource]`. On indexe
  par ID parce que les questions peuvent être dans un ordre différent
  entre les fichiers.
- `isinstance(q, AnsweredQuestion)` : on ignore les questions sans
  ground truth (on ne peut pas évaluer).
- On accumule le recall pour chaque k. À la fin, moyenne.
- `n if n else 0.0` : évite division par zéro si aucune question
  evaluable.

### 10.5 `EvalReport.pretty()`

Formate la sortie texte attendue par le sujet :

```
Evaluation Results
========================================
Questions evaluated: 100
Recall@ 1: 0.450
Recall@ 3: 0.590
Recall@ 5: 0.650
Recall@10: 0.720
```

Le `f"Recall@{k:>2}:"` aligne `k` à droite sur 2 caractères → `" 1"`
au lieu de `"1"`. Cosmétique mais propre.

---

<a id="11-flows"></a>
## 11. Les 3 flots d'exécution complets

### Flot 1 : `python -m student index --use_embeddings True`

```
__main__.py
  └─> cli.main()
        └─> fire.Fire(CLI)
              └─> CLI.index(repo_path=..., use_embeddings=True)
                    ├─> _resolve_repo(...)            # descend dans le subfolder si besoin
                    ├─> KnowledgeBase.build(...)
                    │     ├─> collect_files(...)      # lit tous les .py/.md
                    │     │     ├─> iter_files(...)   # os.walk + filtre
                    │     │     └─> read_file_safely(...)
                    │     ├─> chunk_file(...) × N
                    │     │     ├─> chunk_python (AST)
                    │     │     ├─> chunk_markdown (#)
                    │     │     └─> _split_oversized
                    │     ├─> tokenize_batch          # camelCase + lowercase
                    │     ├─> bm25s.BM25().index(...)
                    │     └─> _encode_corpus(...)     # bonus dense
                    └─> kb.save(...)                  # chunks.json + bm25_index/ + dense_index/
```

### Flot 2 : `python -m student search "openai server"`

```
__main__.py → cli.main() → fire.Fire(CLI)
  └─> CLI.search(query="openai server", k=10)
        ├─> KnowledgeBase.load(...)
        ├─> kb.search(query, k=10, mode="auto")
        │     ├─> mode = "hybrid" (embeddings présents) ou "bm25"
        │     └─> search_hybrid:
        │           ├─> search_bm25(query, k=40)
        │           │     ├─> tokenize(query)
        │           │     └─> bm25.retrieve(...)
        │           ├─> search_dense(query, k=40)
        │           │     ├─> _get_embedder() (lazy)
        │           │     ├─> encode(query)
        │           │     ├─> dense @ q_vec        # produit scalaire
        │           │     └─> np.argpartition + argsort
        │           └─> RRF fusion
        ├─> [Chunk → MinimalSource]
        └─> json.dumps + print
```

### Flot 3 : `python -m student evaluate ...`

```
CLI.evaluate(student_results_path, dataset_path)
  └─> evaluate.evaluate(...)
        ├─> StudentSearchResults.model_validate_json(...)
        ├─> RagDataset.model_validate_json(...)
        ├─> construit truth_by_id (dict)
        └─> pour chaque question:
              └─> question_recall(retrieved, truth, k)
                    └─> overlap_ratio(r, t) pour chaque paire
  └─> print(report.pretty())
```

---

<a id="12-design"></a>
## 12. Pourquoi ce design ?

| Principe                | Application concrète                                        |
|-------------------------|-------------------------------------------------------------|
| Une responsabilité par fichier | `ingest` lit, `chunking` découpe, `tokenizer` tokenise, `index` cherche, `generator` génère, `evaluate` note. |
| Lazy imports            | `torch`, `transformers`, `sentence-transformers` ne sont importés QUE si on en a besoin. La CLI démarre en < 1s. |
| Persistance / caching   | `KnowledgeBase.save/load` → on indexe une fois, on cherche autant qu'on veut. |
| Validation pydantic     | Tous les JSON entrants/sortants passent par les modèles. Un fichier corrompu → erreur claire AU BON ENDROIT. |
| Fire au lieu d'argparse | Les méthodes Python deviennent des sous-commandes shell automatiquement. Pas de boilerplate. |
| Type hints              | mypy passe sans erreur (exigence du sujet). |
| Singleton du LLM        | Charger Qwen3 prend qq secondes. On le fait UNE fois par processus. |
| BM25 + dense + RRF      | BM25 attrape les matches exacts (noms de fonctions...), dense attrape la sémantique (paraphrases). RRF les fusionne sans avoir à normaliser les scores. |

---

## Bonus — Pour aller plus loin

- **Reranker** : ajouter un cross-encoder qui prend (requête, chunk) et
  retourne un score. Plus précis mais plus lent. À mettre après le
  retrieve, sur les top-30, pour ne garder que les top-10.
- **Query rewriting** : faire générer par un LLM 2-3 reformulations de
  la question, lancer le retrieve sur chacune, fusionner.
- **Overlap plus généreux** : passer `overlap = max // 5` au lieu de
  `// 10` peut améliorer le recall (mais grossit l'index).
- **Tokenizer plus fin** : ajouter des stems anglais (« running » →
  « run ») via `nltk` ou `snowballstemmer`.

Bonne lecture !
