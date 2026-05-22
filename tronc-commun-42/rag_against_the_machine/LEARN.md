# LEARN.md — RAG against the machine

> Document de référence exhaustif pour apprendre **tout** ce qu'il y a à savoir
> sur ce projet : architecture, code ligne par ligne, concepts théoriques,
> dépendances, tests, critique et pistes pour aller plus loin.

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Installation et exécution](#2-installation-et-exécution)
3. [Architecture détaillée](#3-architecture-détaillée)
4. [Parcours fichier par fichier](#4-parcours-fichier-par-fichier)
   - 4.1 [`pyproject.toml`](#41-pyprojecttoml)
   - 4.2 [`Makefile`](#42-makefile)
   - 4.3 [`.flake8`](#43-flake8)
   - 4.4 [`.gitignore`](#44-gitignore)
   - 4.5 [`README.md`](#45-readmemd)
   - 4.6 [`PREREQUIS.md` et `CODE_EXPLAINED.md`](#46-prerequismd-et-code_explainedmd)
   - 4.7 [`src/student/__init__.py`](#47-srcstudent__init__py)
   - 4.8 [`src/student/__main__.py`](#48-srcstudent__main__py)
   - 4.9 [`src/student/models.py`](#49-srcstudentmodelspy)
   - 4.10 [`src/student/ingest.py`](#410-srcstudentingestpy)
   - 4.11 [`src/student/tokenizer.py`](#411-srcstudenttokenizerpy)
   - 4.12 [`src/student/chunking.py`](#412-srcstudentchunkingpy)
   - 4.13 [`src/student/index.py`](#413-srcstudentindexpy)
   - 4.14 [`src/student/generator.py`](#414-srcstudentgeneratorpy)
   - 4.15 [`src/student/evaluate.py`](#415-srcstudentevaluatepy)
   - 4.16 [`src/student/cli.py`](#416-srcstudentclipy)
5. [Concepts techniques exhaustifs](#5-concepts-techniques-exhaustifs)
6. [Dépendances externes](#6-dépendances-externes)
7. [Flux de données](#7-flux-de-données)
8. [Tests](#8-tests)
9. [Critique du code](#9-critique-du-code)
10. [Glossaire](#10-glossaire)
11. [Cheatsheet](#11-cheatsheet)
12. [Pour aller plus loin](#12-pour-aller-plus-loin)
13. [Préparation à la défense 42](#13-préparation-à-la-défense-42)

---

## 1. Vue d'ensemble

### 1.1 But du projet

Le projet **RAG against the machine** (cursus 42, version 1.6) consiste à
construire un système de **Retrieval-Augmented Generation** (RAG) qui répond à
des questions sur le code source de [vLLM](https://github.com/vllm-project/vllm),
une bibliothèque open-source d'inférence pour grands modèles de langage.

L'utilisateur tape une question en langage naturel (« Comment vLLM expose-t-il
une API compatible OpenAI ? »), le système :

1. **Cherche** les passages les plus pertinents dans le dépôt vLLM indexé.
2. **Passe** ces passages comme contexte à un petit LLM local (Qwen3-0.6B).
3. **Génère** une réponse rédigée et ancrée dans le code/la doc retrouvée.

Le système est évalué par un *Recall@k* : pour un dataset de questions à
réponses connues, on vérifie que les passages retournés chevauchent
suffisamment les passages attendus (≥ 5 % de caractères communs).

### 1.2 Contexte d'utilisation

- **42 cursus tronc commun** — projet noté en defense par un pair et une
  *moulinette* (binaire exécutable fourni).
- **Hors-ligne après installation** : aucune requête réseau au moment d'une
  question. Tout est local (modèle Qwen téléchargé une fois depuis HuggingFace,
  index BM25 persisté sur disque).
- **Apprentissage** des notions modernes d'IA : indexation lexicale + dense,
  fusion hybride, prompting d'un LLM, évaluation rigoureuse.

### 1.3 Stack technique et justification

| Brique | Choix | Pourquoi |
|---|---|---|
| Langage | **Python 3.10** | Imposé par le sujet (`Python 3.10 or later`, < 3.11 fixé par `pyproject.toml`). |
| Package manager | **uv** | Imposé. Plus rapide que pip, lockfile reproductible (`uv.lock`). |
| CLI | **Python Fire** | Imposé. Transforme une classe en CLI sans boilerplate (`fire.Fire(CLI)`). |
| Validation | **Pydantic v2** | Imposé. Modèles de données type-safe + (de)sérialisation JSON. |
| Barres de progression | **tqdm** | Imposé pour les opérations longues. |
| Index lexical | **bm25s** | 10–100× plus rapide que `rank_bm25`, tient le budget de 5 min. |
| Embeddings (bonus) | **sentence-transformers/all-MiniLM-L6-v2** | Petit (90 Mo), rapide, qualité raisonnable. |
| LLM | **Qwen/Qwen3-0.6B** | Imposé. Modèle de 600 M de paramètres, ~1.2 Go en float16. |
| Backend tenseurs | **PyTorch** | Requis par transformers. |
| Tests | **pytest** | Recommandé (non bloquant). |
| Lint | **flake8 + mypy** | Imposé : doivent passer sans erreur. |
| Build backend | **hatchling** | Simple, conforme PEP 517. |

### 1.4 Architecture globale

```
                              ┌─────────────────────┐
   vllm-0.10.1/  ───────────▶│  ingest + chunking  │
   (~1900 fichiers)           └──────────┬──────────┘
                                         │ 21 530 chunks
                                         ▼
                              ┌─────────────────────┐
                              │  tokenizer (code)   │
                              └──────────┬──────────┘
                                         ▼
                              ┌─────────────────────┐
                              │  BM25 index (bm25s) │ ◀── ./data/processed/
                              └──────────┬──────────┘
                              ┌─────────────────────┐
                       bonus  │  Dense embeddings   │
                              │  MiniLM-L6-v2       │
                              └──────────┬──────────┘
                                         │
                              ┌──────────▼──────────┐
                   query ───▶ │  RRF fusion (k=60)  │ ──▶ top-k chunks
                              └──────────┬──────────┘
                                         │
                              ┌──────────▼──────────┐
                              │  Qwen3-0.6B chat    │
                              │  + system prompt    │
                              └──────────┬──────────┘
                                         ▼
                                 grounded answer
```

### 1.5 Arborescence

```
rag_against_the_machine/
├── README.md                  ⟵ doc publique (description, instructions, archi, etc.)
├── PREREQUIS.md               ⟵ doc d'apprentissage (préalable à la lecture du code)
├── CODE_EXPLAINED.md          ⟵ doc d'apprentissage (lecture pas-à-pas du code)
├── LEARN.md                   ⟵ ce fichier (référence exhaustive)
├── Makefile                   ⟵ cibles install / run / lint / clean / index / test
├── pyproject.toml             ⟵ métadonnées + dépendances (PEP 621)
├── uv.lock                    ⟵ lockfile uv pour reproductibilité
├── .flake8                    ⟵ configuration flake8 (max-line-length=100)
├── .gitignore                 ⟵ exclut .venv, data/, caches
└── src/
    └── student/               ⟵ package Python (paquet importable)
        ├── __init__.py        ⟵ marqueur de package + version
        ├── __main__.py        ⟵ point d'entrée pour `python -m student`
        ├── cli.py             ⟵ classe CLI (Fire) — 6 sous-commandes
        ├── models.py          ⟵ modèles Pydantic (MinimalSource, etc.)
        ├── ingest.py          ⟵ parcours du dépôt vLLM, lecture fichiers
        ├── chunking.py        ⟵ découpage AST (Python) / headers (Markdown)
        ├── tokenizer.py       ⟵ tokenizer identifier-aware
        ├── index.py           ⟵ KnowledgeBase (BM25 + dense + hybrid)
        ├── generator.py       ⟵ AnswerGenerator (Qwen3-0.6B)
        └── evaluate.py        ⟵ Recall@k local (mirror de la moulinette)
```

Dossiers générés (non versionnés, ignorés via `.gitignore`) :

```
data/
├── raw/vllm-0.10.1/           ⟵ dépôt vLLM dézippé (ingestion source)
├── datasets/                  ⟵ datasets publics (questions ground-truth)
│   ├── AnsweredQuestions/
│   └── UnansweredQuestions/
├── processed/                 ⟵ index persisté (produit par `student index`)
│   ├── chunks.json
│   ├── bm25_index/
│   ├── dense_index/ (bonus)
│   └── meta.json
└── output/                    ⟵ résultats des commandes search_dataset / answer_dataset
    ├── search_results/
    └── search_results_and_answer/
```

---

## 2. Installation et exécution

### 2.1 Prérequis système

- **OS** : Linux (Ubuntu/Fedora supportés par la moulinette officielle ; macOS
  fonctionne aussi mais non testé contre la moulinette).
- **Python 3.10.x** exactement (le `pyproject.toml` fixe `>=3.10,<3.11`).
- **uv** installé : <https://github.com/astral-sh/uv>.
- **GPU optionnel** : la génération tourne sur CPU (lent : ~30 s par réponse)
  ou GPU (~5 s par réponse). 4 GB de VRAM suffisent en float16 si on limite
  le contexte.
- **Disque** : ~3 Go pour `.venv` (torch + transformers) + ~150 Mo pour le
  modèle Qwen3-0.6B + ~50 Mo pour l'index BM25 du dépôt vLLM complet.
- **vLLM** : récupérer `vllm-0.10.1.zip` (fourni avec le sujet), le dézipper
  dans `data/raw/`.
- **Datasets** : récupérer `datasets_public.zip` (fourni), dézipper dans
  `data/`.

### 2.2 Installation

```bash
# 1. Créer le venv et installer les dépendances
make install
# équivalent : uv venv && uv sync

# 2. Activer le venvuv run python -m student index --max_chunk_size 2000
source .venv/bin/activate

# 3. Mettre le code vLLM en place
mkdir -p data/raw
unzip vllm-0.10.1.zip -d data/raw          # → data/raw/vllm-0.10.1/

# 4. Mettre les datasets en place
unzip datasets_public.zip -d data/         # → data/datasets/{Answered,Unanswered}Questions/
```

### 2.3 Pipeline complet (ce qu'on fait à la défense)

```bash
# 1. Indexer (~ 7 s pour 1900 fichiers / 21 500 chunks)
uv run python -m student index --max_chunk_size 2000

# 1-bis. Indexer avec embeddings denses (bonus, +1 à 2 min)
uv run python -m student index --max_chunk_size 2000 --use_embeddings True

# 2. Question unique (recherche)
uv run python -m student search "How to configure OpenAI server?" --k 10

# 3. Question unique (recherche + génération)
uv run python -m student answer "How to configure OpenAI server?" --k 5

# 4. Tout un dataset → fichier JSON de résultats de recherche
uv run python -m student search_dataset \
    --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json \
    --k 10 \
    --save_directory data/output/search_results

# 5. Évaluer (Recall@1/3/5/10)
uv run python -m student evaluate \
    --student_results_path data/output/search_results/dataset_docs_public.json \
    --dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json

# 6. Générer toutes les réponses (lent : ~5–30 s par question selon GPU)
uv run python -m student answer_dataset \
    --student_search_results_path data/output/search_results/dataset_docs_public.json \
    --save_directory data/output/search_results_and_answer
```

### 2.4 Cibles `make`

```bash
make install        # uv venv && uv sync
make run            # python -m student --help
make debug          # python -m pdb -m student   (debugger interactif)
make clean          # supprime __pycache__, .mypy_cache, .pytest_cache, *.pyc
make lint           # flake8 . + mypy (avec les flags exacts du sujet)
make lint-strict    # flake8 . + mypy --strict (optionnel, plus sévère)
make index          # raccourci pour `python -m student index`
make test           # pytest -q || true (pas de tests fournis, ne bloque pas)
```

### 2.5 Variables d'environnement utiles

| Variable | Effet |
|---|---|
| `UV_CACHE_DIR` | Déplace le cache uv (utile si `/home` est plein). |
| `UV_PROJECT_ENVIRONMENT` | Déplace `.venv/` ailleurs. |
| `HF_HOME` | Cache HuggingFace (poids du modèle Qwen, embedder MiniLM). |
| `TRANSFORMERS_CACHE` | Idem (legacy, redirigé vers `HF_HOME`). |
| `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` | Réduit la fragmentation VRAM. |

### 2.6 Configs lint

- **`.flake8`** (fichier à part — flake8 ne lit pas `pyproject.toml`) :
  ```ini
  [flake8]
  max-line-length = 100
  extend-ignore = E203, W503
  exclude = .venv, build, dist, data
  ```
- **`pyproject.toml`** section `[tool.mypy]` (lue par mypy) :
  ```toml
  python_version = "3.10"
  ignore_missing_imports = true
  warn_return_any = true
  warn_unused_ignores = true
  disallow_untyped_defs = true
  check_untyped_defs = true
  ```
  Les mêmes flags se retrouvent en argument de la cible `make lint` :
  `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports
  --disallow-untyped-defs --check-untyped-defs`.

---

## 3. Architecture détaillée

### 3.1 Flux d'exécution global

L'utilisateur tape `python -m student <cmd> ...`. Le flux ressemble à :

```
shell                          ← appel utilisateur
  │
  ▼
python -m student              ← Python charge le package `student`
  │
  ▼
student/__main__.py            ← Python exécute __main__.py
  │ from .cli import main; main()
  ▼
student/cli.py:main()
  │ import fire; fire.Fire(CLI)
  ▼
fire dispatche vers la méthode correspondante (index | search | ...)
  │
  ▼
CLI.<method>(args)             ← logique métier
  │ utilise: KnowledgeBase (index.py), AnswerGenerator (generator.py),
  │          Pydantic models (models.py), evaluate (evaluate.py)
  ▼
print(...)                     ← affichage utilisateur
return msg                     ← Fire affiche aussi le retour
```

### 3.2 Couches logiques

Le projet suit un découpage clair en 5 couches :

| Couche | Modules | Responsabilité |
|---|---|---|
| **Présentation / CLI** | `__main__.py`, `cli.py` | Parsing arguments, dispatching, formatting output. |
| **Modèles** | `models.py` | Schémas Pydantic validés (boundary contracts). |
| **Ingestion** | `ingest.py`, `chunking.py`, `tokenizer.py` | Du dépôt brut → liste de chunks tokenisés. |
| **Index / retrieval** | `index.py` | Construit/charge l'index, exécute BM25 / dense / hybrid. |
| **Génération** | `generator.py` | Charge le LLM, formate le prompt, génère la réponse. |
| **Évaluation** | `evaluate.py` | Calcule Recall@k local (mirror de la moulinette). |

### 3.3 Patterns architecturaux identifiés

- **Layered architecture** — les modules dépendent de bas en haut (cli → index
  → chunking → tokenizer ; jamais l'inverse). Pas d'import circulaire.
- **Singleton (lazy)** — `get_generator()` dans `generator.py` garde une
  instance unique d'`AnswerGenerator` pour éviter de recharger Qwen3 à chaque
  question.
- **Strategy** — `KnowledgeBase.search(mode=...)` choisit entre BM25, dense,
  ou hybride au runtime. `chunk_file()` dispatche vers `chunk_python` /
  `chunk_markdown` / `chunk_text` selon l'extension.
- **Builder + persistence** — `KnowledgeBase.build()` construit l'objet,
  `save()` persiste, `load()` reconstruit. Le classmethod sert de constructeur
  alternatif (`@classmethod build`, `load`).
- **Lazy loading** — `KnowledgeBase._embedder` n'est chargé qu'au premier
  `search_dense()` ; `AnswerGenerator._model` au premier `generate()`.
  Conséquence : le path BM25 pur n'importe jamais `torch` ni `transformers`.
- **Dispatch par dictionnaire / type** — `chunk_file()` regarde l'extension
  pour choisir le chunker. Plus de polymorphisme classique (extension de
  classe).
- **Data Transfer Objects** — `MinimalSource`, `MinimalSearchResults`, etc.
  sont des DTOs Pydantic qui définissent le contrat I/O JSON.

### 3.4 Interactions entre modules (graph d'imports)

```
                  cli.py
        ┌───────────┼───────────────────────────────┐
        │           │             │                 │
        ▼           ▼             ▼                 ▼
 evaluate.py   generator.py   index.py        models.py
        │           │             │                 │
        │           ▼             ▼                 │
        │      chunking.py   ingest.py              │
        │           │             │                 │
        │           │             ▼                 │
        │           │       (stdlib os, re)         │
        │           │                               │
        │           ▼                               │
        │      tokenizer.py                         │
        │           │                               │
        ▼           ▼                               │
    models.py ◀────┴────── (importé partout) ──────┘
```

Lecture : `cli.py` importe (et dépend de) tous les autres modules. `models.py`
ne dépend de rien (sauf de pydantic). `tokenizer.py` ne dépend que de la
stdlib (`re`). `chunking.py` ne dépend que de `ast`. `ingest.py` ne dépend que
de `os` et `tqdm`. C'est une **layered architecture** propre.

### 3.5 Données persistées

```
data/processed/
├── chunks.json         ⟵ liste de Chunk dataclass sérialisés
│                          [{file_path, first_character_index,
│                            last_character_index, text}, ...]
├── meta.json           ⟵ {"embedder_name": ..., "n_chunks": "..."}
├── bm25_index/         ⟵ format propre à `bm25s.BM25.save()`
│   ├── params.index.json
│   ├── data.csc.index.npy
│   ├── indices.csc.index.npy
│   ├── indptr.csc.index.npy
│   └── vocab.index.json
└── dense_index/        ⟵ uniquement si --use_embeddings True
    └── embeddings.npy  ⟵ array numpy (N_chunks × 384) float32
```

---

## 4. Parcours fichier par fichier

### 4.1 `pyproject.toml`

**Rôle.** Fichier central de configuration du package Python (PEP 621). Il
définit le nom, la version, les dépendances, et configure les outils
(`mypy`, `flake8`).

```toml
[project]
name = "student"                         # nom du package importable
version = "0.1.0"                        # SemVer
description = "RAG against the machine - 42 project"
requires-python = ">=3.10,<3.11"         # Python 3.10 exactement
dependencies = [
    "pydantic>=2.6",                     # modèles validés
    "fire>=0.6",                         # CLI auto depuis classe
    "tqdm>=4.66",                        # barres de progression
    "bm25s>=0.2.0",                      # BM25 rapide
    "transformers>=4.44",                # HuggingFace (LLM)
    "torch>=2.2",                        # backend tenseurs
    "accelerate>=0.30",                  # device_map="auto"
    "numpy>=1.26",                       # arrays
    "sentence-transformers>=2.7",        # embeddings denses (bonus)
    "chromadb>=0.5",                     # importable, non utilisé (recommandé par sujet)
    "PyStemmer>=2.2.0",                  # stemming (optionnel BM25)
]

[project.optional-dependencies]          # `uv sync --group dev`
dev = ["flake8>=7.0", "mypy>=1.10", "pytest>=8.0"]

[build-system]
requires = ["hatchling"]                 # backend de build PEP 517
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/student"]               # layout src/

[tool.mypy]                              # paramètres mypy
python_version = "3.10"
ignore_missing_imports = true            # ne pas exiger les stubs des libs externes
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true             # toutes les fonctions doivent être typées
check_untyped_defs = true

[tool.flake8]                            # IGNORÉ par flake8 (qui ne lit pas pyproject.toml)
max-line-length = 100                    # → voir aussi le .flake8 séparé
extend-ignore = ["E203", "W503"]
```

**Points d'attention** :

- `chromadb` est dans les deps parce que recommandé par le sujet, mais
  le projet ne l'utilise pas dans le code. Le code utilise `bm25s` (autorisé
  car « TF-IDF ou BM25 »).
- `requires-python = ">=3.10,<3.11"` est strict — empêche d'installer en 3.11+
  pour éviter les surprises avec les libs ML.
- Layout `src/` (recommandé) — empêche d'importer accidentellement le package
  sans installation.

### 4.2 `Makefile`

**Rôle.** Automatiser les tâches courantes (imposé par le sujet).

```make
.PHONY: install run debug clean lint lint-strict index search evaluate test

PYTHON := uv run python                  # raccourci variable
MODULE := student

install:                                 # crée venv + installe deps
	uv venv
	uv sync

run:                                     # affiche l'aide CLI
	$(PYTHON) -m $(MODULE) --help

debug:                                   # debugger pdb interactif
	$(PYTHON) -m pdb -m $(MODULE)

clean:                                   # supprime artefacts Python
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:                                    # flake8 + mypy (flags imposés)
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:                             # mypy --strict (optionnel)
	uv run flake8 .
	uv run mypy . --strict

index:                                   # alias indexation
	$(PYTHON) -m $(MODULE) index --max_chunk_size 2000

test:                                    # pytest, ne bloque pas si pas de tests
	uv run pytest -q || true
```

**Pièges** :

- Le sujet impose **les flags mypy exacts** : `--warn-return-any
  --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs
  --check-untyped-defs`. Tout flag manquant = note retirée.
- L'indentation Makefile : **tabulations uniquement**. Un espace en début de
  ligne = `*** missing separator`.
- `.PHONY` empêche `make install` de ne rien faire s'il existe un fichier
  nommé `install`.

### 4.3 `.flake8`

```ini
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude = .venv, build, dist, data
```

**Pourquoi un fichier à part** : flake8 ne lit **pas** `pyproject.toml` par
défaut. Sans `.flake8` (ou `setup.cfg`), il revient à PEP8 strict
(`max-line-length=79`) et toutes les lignes de plus de 79 caractères
échouent. Le projet a beaucoup de telles lignes ; on relâche à 100.

**Codes ignorés** :
- `E203` (`whitespace before ':'`) — incompatible avec `black` et le slicing
  numpy.
- `W503` (`line break before binary operator`) — PEP8 a changé d'avis,
  cette règle est obsolète.

### 4.4 `.gitignore`

```
__pycache__/
*.py[cod]
*.egg-info/
.mypy_cache/
.pytest_cache/
.venv/
venv/
.env
.envrc

# Project artifacts (ne pas commit !)
data/raw/                # vLLM dézippé (~70 Mo)
data/processed/          # index BM25 généré
data/output/             # outputs des commandes
data/datasets/           # datasets publics
*.log

# Models cache
.cache/
models/
```

Conforme à la consigne du sujet (chap. IX) : « Do not include large data
files, model weights, or generated outputs in your repository ».

### 4.5 `README.md`

**Rôle.** Documentation publique. Le sujet (chap. VII) impose 9 sections :

1. Italique première ligne `*This project has been created as part of the 42
   curriculum by <login>.*`
2. Description
3. Instructions (install / run)
4. Resources (refs externes + AI usage)
5. System architecture
6. Chunking strategy
7. Retrieval method
8. Performance analysis
9. Design decisions
10. Challenges faced
11. Example usage

Toutes les sections sont présentes dans le `README.md` du projet.

### 4.6 `PREREQUIS.md` et `CODE_EXPLAINED.md`

Documents d'apprentissage non requis par le sujet, ajoutés pour
l'auto-formation :

- **`PREREQUIS.md`** : liste tout ce qu'il faut savoir avant de lire le
  code (Python, RAG, BM25, embeddings, LLM, outils système).
- **`CODE_EXPLAINED.md`** : lecture pas-à-pas du code, ligne par ligne, avec
  commentaires pédagogiques.

### 4.7 `src/student/__init__.py`

```python
"""RAG against the machine — student package."""

__version__ = "0.1.0"
```

**Rôle.** Marqueur de package + exposition de la version.

**Concept** : sans `__init__.py`, Python 3.3+ reconnaît quand même un
*namespace package* (PEP 420), mais **avec un build backend comme
`hatchling` ce n'est pas suffisant** : `hatch` peut refuser d'inclure
le dossier ou détecter le package incorrectement. Le `__init__.py`
explicite est donc obligatoire ici. Il permet aussi d'exposer la version
(`student.__version__`) et de contrôler ce qui est ré-exporté.

### 4.8 `src/student/__main__.py`

```python
"""Module entry point: ``python -m student``."""

from .cli import main

if __name__ == "__main__":
    main()
```

**Rôle.** Permet d'exécuter le package avec `python -m student`. Python
cherche un `__main__.py` à la racine du package quand on lui passe `-m`.

**Concept** : `if __name__ == "__main__":` garde-fou — ne s'exécute que
quand le fichier est lancé directement, pas s'il est importé.

### 4.9 `src/student/models.py`

**Rôle.** Définit tous les schémas Pydantic v2 utilisés comme contrats de
données (entrée datasets, sortie résultats).

```python
"""Pydantic data models required by the RAG pipeline specification."""

from __future__ import annotations

import uuid
from typing import List, Union

from pydantic import BaseModel, Field


class MinimalSource(BaseModel):
    """A minimal source: a slice of a file by character offsets."""

    file_path: str
    first_character_index: int
    last_character_index: int


class UnansweredQuestion(BaseModel):
    """A question that has not been answered yet."""

    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """A question with a ground-truth answer and its source slices."""

    sources: List[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """A dataset of RAG questions (answered or unanswered)."""

    rag_questions: List[Union[AnsweredQuestion, UnansweredQuestion]]


class MinimalSearchResults(BaseModel):
    """Search results for a single question."""

    question_id: str
    question_str: str                   # ⚠️ NOM IMPORTANT
    retrieved_sources: List[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    """Search results enriched with a generated answer."""

    answer: str


class StudentSearchResults(BaseModel):
    """Full batch of search results emitted by the student system."""

    search_results: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(StudentSearchResults):
    """Batch of search results plus generated answers."""

    search_results: List[MinimalAnswer]  # type: ignore[assignment]
```

**Détails ligne par ligne** :

- **L1–8** : doc + imports. `from __future__ import annotations` permet la
  syntaxe d'annotation moderne (`list[str]`, `X | None`) même quand on
  importe depuis un module plus ancien.
- **L11–15 `MinimalSource`** : la brique de base. Un *passage* dans un
  fichier, identifié par 3 champs (path, début, fin). C'est ce qui permet
  au Recall@k de comparer.
- **L18–22 `UnansweredQuestion`** : `question_id` est généré automatiquement
  si non fourni (`default_factory=lambda: str(uuid.uuid4())`). Comportement
  utile pour générer des datasets à la volée.
- **L25–29 `AnsweredQuestion`** : hérite d'`UnansweredQuestion` et ajoute
  `sources` (vérité terrain) + `answer` (réponse modèle, jamais utilisé e
  par le student mais présente dans les datasets).
- **L32–35 `RagDataset`** : un container `{rag_questions: [...]}` qui peut
  contenir un mix d'AnsweredQuestion / UnansweredQuestion grâce à `Union`.
  ⚠️ **Pydantic v2 essaie les types dans l'ordre déclaré** du `Union`
  (`AnsweredQuestion` d'abord, puis `UnansweredQuestion` en fallback).
  L'ordre **n'est pas** déterminé par la spécificité de la classe : il
  faut mettre le type le plus spécifique en premier soi-même, sinon
  Pydantic accepterait une question avec `sources` comme `UnansweredQuestion`
  et perdrait silencieusement les champs supplémentaires. Le mode
  `smart` (par défaut en v2) peut aussi entrer en jeu sur certains
  types — voir <https://docs.pydantic.dev/latest/concepts/unions/>.
- **L38–42 `MinimalSearchResults`** : ⚠️ le champ est **`question_str`**
  (pas `question`). Le sujet PDF V.7 montre `question: str` dans son
  exemple de code, mais le binaire moulinette officiel (`moulinette-ubuntu`,
  v2 livrée mai 2026) **rejette** l'output avec une erreur Pydantic
  `Field required: question_str` si on utilise `question`. Vérifié
  empiriquement en lançant la moulinette avant et après le rename — voir
  la section 11.3 "FAQ". **Toujours retester** avec la version exacte de
  la moulinette qui sera utilisée à la défense.
- **L45–47 `MinimalAnswer`** : extension de `MinimalSearchResults` avec un
  champ `answer`.
- **L50–53 `StudentSearchResults`** : conteneur des résultats de recherche
  + `k` utilisé.
- **L56–58 `StudentSearchResultsAndAnswer`** : même chose mais avec des
  `MinimalAnswer` au lieu de `MinimalSearchResults`. Le `# type: ignore` est
  là parce que mypy n'aime pas les redéfinitions de champ avec un type plus
  étroit. C'est cohérent avec Pydantic.

**Concepts illustrés** :

- **Pydantic `BaseModel`** : validation automatique, (de)sérialisation
  JSON via `model_validate_json(s)` (lecture) et `model_dump_json()`
  (écriture).
- **`Field(default_factory=...)`** : valeur par défaut calculée à
  l'instanciation (sinon partagée entre instances → bug classique).
- **`Union[A, B]`** : un champ qui accepte plusieurs types ; Pydantic
  essaie chacun dans l'ordre.
- **Héritage de classe Pydantic** : `AnsweredQuestion(UnansweredQuestion)`
  hérite des champs.

> 💡 **Analogie trading** — Pydantic joue le rôle d'un validateur de payload côté EA : avant d'exécuter un signal reçu via webhook Telegram ou une réponse d'API broker, on vérifie que les champs (`symbol`, `lot`, `sl`, `tp`) sont bien typés et présents. Un champ manquant ou mal typé est rejeté avant qu'il ne provoque un trade incohérent, exactement comme Pydantic rejette un dataset mal formé avant qu'il ne casse le pipeline.

### 4.10 `src/student/ingest.py`

**Rôle.** Parcourir le dépôt vLLM, filtrer les fichiers utiles, et les lire
en mémoire.

```python
"""Filesystem ingestion: walk the repository and collect files to index."""

from __future__ import annotations

import os
from typing import Iterator, List, Tuple

from tqdm import tqdm

ALLOWED_EXTENSIONS = (".py", ".md", ".markdown", ".rst", ".txt")
SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    ".venv",
    "venv",
    "build",
    "dist",
    ".tox",
}


def iter_files(root: str) -> Iterator[str]:
    """Yield absolute paths of indexable files under ``root``."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]   # in-place
        for name in filenames:
            if name.lower().endswith(ALLOWED_EXTENSIONS):
                yield os.path.join(dirpath, name)


def read_file_safely(path: str) -> str:
    """Read a file as UTF-8, ignoring decoding errors."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            return fh.read()
    except OSError:
        return ""


def collect_files(root: str, relative_to: str | None = None) -> List[Tuple[str, str]]:
    """Return a list of (relative_path, content) for every indexable file."""
    base = relative_to or root
    files: List[Tuple[str, str]] = []
    paths = list(iter_files(root))
    for abs_path in tqdm(paths, desc="Reading files", unit="file"):
        text = read_file_safely(abs_path)
        if not text.strip():
            continue
        rel = os.path.relpath(abs_path, base)
        files.append((rel, text))
    return files
```

**Concepts essentiels** :

- **`os.walk(root)`** : générateur récursif qui yield `(dirpath, dirnames,
  filenames)`. **Astuce** : on modifie `dirnames[:]` *in-place* pour empêcher
  `os.walk` de descendre dans les dossiers exclus. Si on faisait
  `dirnames = [...]` (rebind), `os.walk` continuerait avec l'ancienne liste.
- **Générateur (`yield`)** : `iter_files` ne stocke pas tout en mémoire ;
  chaque path est produit à la demande.
- **`errors="ignore"`** : robustesse aux fichiers avec des octets non-UTF8
  (fréquent dans un dépôt aussi gros que vLLM).
- **`relative_to`** : ⚠️ **crucial** — détermine la racine pour les paths
  stockés dans les chunks. Le `cli.py` appelle avec `relative_to="."`,
  ce qui donne des paths du genre `data/raw/vllm-0.10.1/docs/x.md`. C'est
  ce qui doit matcher le `file_path` dans les datasets ground-truth.
- **`os.path.relpath(abs, base)`** : transforme un path absolu en path
  relatif à `base`.
- **Tuple typing** : `List[Tuple[str, str]]` = liste de paires
  `(path, contenu)`.

**Pièges** :

- Le filtre `.lower().endswith(ALLOWED_EXTENSIONS)` reconnaît `.PY`, `.Md`,
  etc., insensible à la casse.
- `read_file_safely` retourne `""` en cas d'erreur OS plutôt que de lever
  → `collect_files` filtre les vides avec `if not text.strip(): continue`.

### 4.11 `src/student/tokenizer.py`

**Rôle.** Découper un texte en tokens normalisés. Ce tokenizer est conçu
pour matcher correctement **identifiants de code + langage naturel**.

```python
"""Simple tokenizer tuned for code + prose."""

from __future__ import annotations

import re
from typing import List

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "else", "of", "in",
    "on", "to", "for", "with", "by", "as", "is", "it", "this", "that",
    "these", "those", "be", "are", "was", "were", "from", "at", "into",
    "your", "you", "we", "our", "i", "me", "my", "do", "does", "did",
    "have", "has", "had", "can", "will", "would", "should",
}

_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_SPLIT_RE = re.compile(r"[^A-Za-z0-9]+")


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase identifier-friendly tokens."""
    if not text:
        return []
    parts = _SPLIT_RE.split(text)
    tokens: List[str] = []
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


def tokenize_batch(texts: List[str]) -> List[List[str]]:
    """Tokenize a list of texts."""
    return [tokenize(t) for t in texts]
```

**Décomposition des regex** :

- **`_SPLIT_RE = r"[^A-Za-z0-9]+"`** : splitte sur tout ce qui n'est pas
  alphanumérique. Donc `get_user.name(arg)` → `["get", "user", "name",
  "arg"]`.
- **`_CAMEL_RE = r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])"`** :
  deux *look-around* (lookbehind + lookahead) pour découper le camelCase
  *sans consommer de caractères* :
  - Premier alternant : `(?<=[a-z0-9])(?=[A-Z])` — entre une minuscule/chiffre
    et une majuscule. Ex: `userName` → `["user", "Name"]`.
  - Deuxième alternant : `(?<=[A-Z])(?=[A-Z][a-z])` — entre deux majuscules
    quand la suivante est suivie d'une minuscule. Ex: `HTTPServer` →
    `["HTTP", "Server"]` (ne casse pas `URL` en lettres isolées).

**Exemples concrets** (utile pour comprendre l'effet) :

| Input | Tokens |
|---|---|
| `OpenAIServer` | `["open", "ai", "server"]` |
| `get_chat_completions` | `["get", "chat", "completions"]` |
| `vLLMConfig` | `["llm", "config"]` (`v` < 2 chars → filtré) |
| `the OpenAI API server` | `["open", "ai", "api", "server"]` (`the` stopword) |

**Filtres post-split** :

- `len < 2` éliminés (mots d'une lettre = bruit).
- Stopwords éliminés.
- Tout lowercase pour matcher quoi qu'il arrive.

**Pourquoi c'est crucial pour le code** : sans ce splitting, une question
contenant le mot « server » ne matcherait jamais un fichier qui s'appelle
`OpenAIServer.py` ou contient `OpenAIServer.run()`.

### 4.12 `src/student/chunking.py`

**Rôle.** Découper chaque fichier en chunks avec leurs **offsets de
caractère** dans le fichier d'origine.

```python
"""Chunking strategies for Python and Markdown/text files."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import List


@dataclass
class Chunk:
    """A piece of a file together with its character offsets."""

    file_path: str
    first_character_index: int
    last_character_index: int
    text: str

    def char_len(self) -> int:
        return self.last_character_index - self.first_character_index
```

**`@dataclass`** : génère automatiquement `__init__`, `__repr__`, `__eq__`.
Plus léger qu'une `BaseModel` Pydantic (pas de validation) ; utilisé en
interne — Pydantic n'est utilisé qu'aux frontières I/O.

#### Sous-fonction `_split_oversized`

```python
def _split_oversized(
    file_path: str,
    text: str,
    start: int,
    end: int,
    max_chunk_size: int,
) -> List[Chunk]:
    """Split a chunk that is too large into ~equal sub-chunks with overlap."""
    chunks: List[Chunk] = []
    size = end - start
    if size <= max_chunk_size:
        return [Chunk(file_path, start, end, text[start:end])]

    overlap = max_chunk_size // 10               # 10% overlap
    step = max_chunk_size - overlap              # avance de 90%
    pos = start
    while pos < end:
        sub_end = min(pos + max_chunk_size, end)
        chunks.append(Chunk(file_path, pos, sub_end, text[pos:sub_end]))
        if sub_end >= end:
            break
        pos += step
    return chunks
```

**Idée** : fenêtre glissante avec chevauchement de 10%. Si `max_chunk_size`
= 2000, l'overlap = 200 caractères. Garantit qu'une phrase coupée au milieu
sera *aussi* présente dans le chunk suivant.

#### `chunk_python` (AST-based)

```python
def chunk_python(file_path: str, text: str, max_chunk_size: int = 2000) -> List[Chunk]:
    """Chunk a Python file using its AST."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return chunk_text(file_path, text, max_chunk_size)   # fallback

    chunks: List[Chunk] = []
    lines = text.split("\n")
    line_offsets = [0]
    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line) + 1)   # +1 pour le \n

    def lc_to_offset(lineno: int, col: int) -> int:
        idx = max(0, min(lineno - 1, len(line_offsets) - 1))
        return min(line_offsets[idx] + col, len(text))

    top_level = [
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]

    cursor = 0
    for node in top_level:
        start = lc_to_offset(node.lineno, node.col_offset)
        end_lineno = getattr(node, "end_lineno", node.lineno) or node.lineno
        end_col = getattr(node, "end_col_offset", 0) or 0
        end = lc_to_offset(end_lineno, end_col)

        if start > cursor:
            pre = text[cursor:start].strip()
            if pre:
                chunks.extend(_split_oversized(file_path, text, cursor, start, max_chunk_size))
        chunks.extend(_split_oversized(file_path, text, start, end, max_chunk_size))
        cursor = end

    if cursor < len(text):
        tail = text[cursor:].strip()
        if tail:
            chunks.extend(_split_oversized(file_path, text, cursor, len(text), max_chunk_size))

    if not chunks:
        chunks = _split_oversized(file_path, text, 0, len(text), max_chunk_size)

    return [c for c in chunks if c.text.strip()]
```

**Idée centrale** : utiliser l'**AST** (Abstract Syntax Tree) de Python pour
ne *pas* couper au milieu d'une fonction. Chaque `FunctionDef`,
`AsyncFunctionDef`, `ClassDef` au top-level devient un chunk indépendant.

**Mécanique fine** :

1. `ast.parse(text)` lève `SyntaxError` si le fichier n'est pas du Python
   valide → fallback `chunk_text`.
2. **Table `line_offsets`** : préfixe cumulé des longueurs de lignes. Permet
   de convertir `(lineno, col)` en offset de caractère en O(1).
3. `node.lineno` est 1-indexé, le `line_offsets[idx]` est 0-indexé d'où
   `lineno - 1`.
4. **`end_lineno` / `end_col_offset`** : disponibles à partir de Python 3.8.
   Le `getattr(..., default) or default` est paranoïaque (gère le cas où
   l'attribut serait None).
5. **Préamble** : tout le code entre `cursor` (fin de la fonction
   précédente) et `start` (début de la suivante) est conservé comme chunk
   intermédiaire (imports, constantes, code module-level).
6. **Tail** : après la dernière fonction.
7. **Filtre `if c.text.strip()`** : on garde seulement les chunks non vides.

**Edge cases gérés** :

- Fichier vide ou sans fonctions/classes → fallback `_split_oversized` sur
  tout le fichier.
- Fichier non parsable (SyntaxError) → fallback `chunk_text`.

#### `chunk_markdown` (headers-based)

```python
def chunk_markdown(file_path: str, text: str, max_chunk_size: int = 2000) -> List[Chunk]:
    """Chunk a Markdown file by ATX headers (#, ##, ...)."""
    if not text:
        return []

    lines = text.split("\n")
    line_offsets = [0]
    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line) + 1)

    section_starts: List[int] = []
    for i, line in enumerate(lines):
        if line.lstrip().startswith("#"):
            section_starts.append(line_offsets[i])
    if not section_starts or section_starts[0] != 0:
        section_starts.insert(0, 0)

    boundaries = section_starts + [len(text)]
    chunks: List[Chunk] = []
    for i in range(len(boundaries) - 1):
        start, end = boundaries[i], boundaries[i + 1]
        if text[start:end].strip():
            chunks.extend(_split_oversized(file_path, text, start, end, max_chunk_size))
    return chunks
```

**Idée** : un chunk = une section (entre deux titres `#` ATX).
- `line.lstrip().startswith("#")` capte aussi `   ## Foo` indenté.
- On insère un boundary à 0 pour capturer le préambule (texte avant le 1er
  titre).

**Limites** : capte aussi les `#` dans des blocs de code (ex. `# comment` en
Python dans un bloc ```python ... ```). Acceptable car le bruit reste local.

#### `chunk_text` et `chunk_file`

```python
def chunk_text(file_path: str, text: str, max_chunk_size: int = 2000) -> List[Chunk]:
    """Generic fallback: sliding window."""
    if not text:
        return []
    return _split_oversized(file_path, text, 0, len(text), max_chunk_size)


def chunk_file(file_path: str, text: str, max_chunk_size: int = 2000) -> List[Chunk]:
    """Dispatch to the right chunker based on file extension."""
    lower = file_path.lower()
    if lower.endswith(".py"):
        return chunk_python(file_path, text, max_chunk_size)
    if lower.endswith((".md", ".markdown", ".rst")):
        return chunk_markdown(file_path, text, max_chunk_size)
    return chunk_text(file_path, text, max_chunk_size)
```

**Dispatch par extension** — c'est ici qu'on choisit la stratégie. Si on
voulait ajouter un chunker spécial pour `.rst`, il faudrait l'écrire et
modifier ce switch.

### 4.13 `src/student/index.py`

**Rôle.** Construire, persister et interroger l'index BM25 (+ embeddings
optionnels). C'est le **cœur du système de retrieval**.

#### Header et imports

```python
"""BM25 + optional dense (sentence-transformers) indexing and retrieval."""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

import numpy as np
from tqdm import tqdm

from .chunking import Chunk, chunk_file
from .ingest import collect_files
from .tokenizer import tokenize, tokenize_batch

try:
    import bm25s
except ImportError as exc:                # pragma: no cover
    raise RuntimeError(
        "bm25s is required. Install it via `uv sync`."
    ) from exc
```

**Concepts** :

- **`TYPE_CHECKING`** : `True` à la vérification mypy, `False` au runtime.
  Permet d'importer `SentenceTransformer` pour les annotations sans le
  forcer au runtime (lazy loading).
- **`try: import bm25s except ImportError`** : message d'erreur clair si la
  dépendance manque.
- **`raise X from exc`** : préserve la chaîne d'exception pour le debug
  (PEP 3134).

#### Constantes & classe

```python
CHUNKS_FILENAME = "chunks.json"
BM25_DIRNAME = "bm25_index"
DENSE_DIRNAME = "dense_index"
META_FILENAME = "meta.json"


class KnowledgeBase:
    """Indexed knowledge base with BM25 and optional dense embeddings."""

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

`_embedder` (avec underscore) est privé — chargé seulement au premier
`search_dense()`.

#### `build` (classmethod constructeur)

```python
@classmethod
def build(
    cls,
    repo_root: str,
    max_chunk_size: int = 2000,
    use_embeddings: bool = False,
    embedder_name: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> "KnowledgeBase":
    """Walk ``repo_root``, chunk every file, build BM25 (and dense)."""
    print(f"[index] scanning {repo_root}")
    files = collect_files(repo_root, relative_to=".")            # ← relatif au cwd
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

**Étapes** :

1. `collect_files(repo_root, relative_to=".")` lit tous les fichiers du
   dépôt vLLM. ⚠️ `relative_to="."` est **crucial** : produit des paths
   comme `data/raw/vllm-0.10.1/docs/x.md` qui matchent les datasets.
2. `chunk_file` pour chaque fichier → liste cumulée de chunks.
3. `tokenize_batch` produit `List[List[str]]` (un sac de tokens par chunk).
4. `bm25s.BM25().index(tokens)` construit l'index.
5. Si `use_embeddings=True`, on ajoute la couche dense.

#### `save` et `load`

```python
def save(self, directory: str) -> None:
    """Persist the index to disk."""
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, CHUNKS_FILENAME), "w", encoding="utf-8") as fh:
        json.dump([asdict(c) for c in self.chunks], fh)            # liste de dicts

    bm25_dir = os.path.join(directory, BM25_DIRNAME)
    os.makedirs(bm25_dir, exist_ok=True)
    self.bm25.save(bm25_dir)                                       # format bm25s

    meta: Dict[str, Optional[str]] = {
        "embedder_name": self.embedder_name,
        "n_chunks": str(len(self.chunks)),
    }
    with open(os.path.join(directory, META_FILENAME), "w", encoding="utf-8") as fh:
        json.dump(meta, fh)

    if self.dense_embeddings is not None:
        os.makedirs(os.path.join(directory, DENSE_DIRNAME), exist_ok=True)
        np.save(
            os.path.join(directory, DENSE_DIRNAME, "embeddings.npy"),
            self.dense_embeddings,
        )


@classmethod
def load(cls, directory: str) -> "KnowledgeBase":
    """Load an index previously saved with ``save``."""
    with open(os.path.join(directory, CHUNKS_FILENAME), "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    chunks = [Chunk(**c) for c in raw]                              # ** dict-unpack

    bm25_dir = os.path.join(directory, BM25_DIRNAME)
    bm25 = bm25s.BM25.load(bm25_dir, load_corpus=False)

    meta_path = os.path.join(directory, META_FILENAME)
    embedder_name: Optional[str] = None
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as fh:
            meta = json.load(fh)
            embedder_name = meta.get("embedder_name")

    dense: Optional[np.ndarray] = None
    dense_path = os.path.join(directory, DENSE_DIRNAME, "embeddings.npy")
    if os.path.exists(dense_path):
        dense = np.load(dense_path)

    return cls(chunks, bm25, dense, embedder_name)
```

**Concepts** :

- **`asdict(c)`** : convertit une dataclass en dict pour la sérialisation
  JSON.
- **`Chunk(**c)`** : décompacte le dict en kwargs pour reconstruire la
  dataclass. Pattern simple sans Pydantic.
- **`bm25s.BM25.load(dir, load_corpus=False)`** : on n'a pas besoin de
  recharger le corpus (les chunks sont déjà dans `chunks.json`).
- **`np.save` / `np.load`** : format binaire `.npy` optimisé pour numpy.

#### Retrieval BM25

```python
def search_bm25(self, query: str, k: int = 10) -> List[Tuple[int, float]]:
    """Return (chunk_index, score) pairs from BM25 only."""
    if not query.strip():
        return []
    tokens = tokenize(query)
    if not tokens:
        return []
    docs, scores = self.bm25.retrieve(
        [tokens],                                # batch de 1 query
        k=min(k, len(self.chunks)),
        show_progress=False,
    )
    out: List[Tuple[int, float]] = []
    for idx, score in zip(docs[0], scores[0]):
        out.append((int(idx), float(score)))
    return out
```

- `bm25s.retrieve(queries, k)` retourne **deux** arrays : indices et
  scores, de shape `(n_queries, k)`. On prend `[0]` pour la query unique.
- `min(k, len(self.chunks))` évite l'erreur si k > nb chunks.
- Conversion explicite en `int` / `float` Python (sinon ce sont des
  `np.int64`, source de bugs JSON ultérieurs).

#### Retrieval dense

```python
def _get_embedder(self) -> "SentenceTransformer":
    if self._embedder is None:
        from sentence_transformers import SentenceTransformer
        assert self.embedder_name is not None
        self._embedder = SentenceTransformer(self.embedder_name)
    return self._embedder


def search_dense(self, query: str, k: int = 10) -> List[Tuple[int, float]]:
    """Return (chunk_index, score) pairs using dense cosine similarity."""
    if self.dense_embeddings is None or self.embedder_name is None:
        return []
    embedder = self._get_embedder()
    q_vec = embedder.encode([query], normalize_embeddings=True)
    sims = self.dense_embeddings @ q_vec[0]                # cosinus = dot car normalisés
    top_n = min(k, len(self.chunks))
    idxs = np.argpartition(-sims, top_n - 1)[:top_n]
    idxs = idxs[np.argsort(-sims[idxs])]
    return [(int(i), float(sims[i])) for i in idxs]
```

**Subtilités numpy** :

- **`embeddings @ q_vec[0]`** : produit matriciel
  `(N, 384) @ (384,) = (N,)` — un score par chunk.
- **Cosinus = dot product** parce que `normalize_embeddings=True` (les
  vecteurs sont sur la sphère unité).
- **`np.argpartition(-sims, n-1)[:n]`** : top-n indices sans tri complet
  (O(N) au lieu de O(N log N)). Utile quand N >> k.
- **Ensuite `np.argsort` sur ces n-là** : tri local.

#### Hybrid (RRF)

```python
def search_hybrid(self, query: str, k: int = 10, rrf_k: int = 60) -> List[Tuple[int, float]]:
    """Reciprocal Rank Fusion of BM25 and dense retrieval."""
    pool = max(k * 4, 20)                                          # élargir le bassin
    bm25_hits = self.search_bm25(query, k=pool)
    dense_hits = self.search_dense(query, k=pool) if self.dense_embeddings is not None else []

    scores: Dict[int, float] = {}
    for rank, (idx, _) in enumerate(bm25_hits):
        scores[idx] = scores.get(idx, 0.0) + 1.0 / (rrf_k + rank + 1)
    for rank, (idx, _) in enumerate(dense_hits):
        scores[idx] = scores.get(idx, 0.0) + 1.0 / (rrf_k + rank + 1)

    if not scores:
        return []
    ranked = sorted(scores.items(), key=lambda x: -x[1])[:k]
    return ranked
```

**RRF (Reciprocal Rank Fusion)** : formule de fusion *sans hyperparamètre* à
régler, robuste aux échelles différentes des scores BM25 vs cosinus.

```
score(doc) = Σ_methods  1 / (rrf_k + rank_method(doc))
```

Le paramètre `rrf_k=60` est la constante canonique de Cormack et al. (2009).

**Pool élargi** : on récupère 4×k résultats de chaque méthode pour donner
plus de chances à la fusion (un doc peu classé BM25 mais top en dense
peut remonter).

#### Search high-level

```python
def search(self, query: str, k: int = 10, mode: str = "auto") -> List[Chunk]:
    """High-level retrieval returning chunks. mode ∈ {auto, bm25, dense, hybrid}."""
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

**`mode="auto"`** : par défaut, hybride si dispo, sinon BM25. Pratique.

#### Helper d'encodage

```python
def _encode_corpus(chunks: List[Chunk], model_name: str) -> np.ndarray:
    """Encode chunks into normalized dense vectors."""
    from sentence_transformers import SentenceTransformer
    print(f"[index] loading embedder {model_name}")
    model = SentenceTransformer(model_name)
    texts = [c.text for c in chunks]
    print(f"[index] encoding {len(texts)} chunks (this is the slow step)")
    vectors = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return np.asarray(vectors, dtype=np.float32)
```

`batch_size=64` est un compromis vitesse/mémoire CPU. `dtype=np.float32` est
le format standard des embeddings (suffisant pour la similarité).

### 4.14 `src/student/generator.py`

**Rôle.** Charger Qwen3-0.6B et produire une réponse ancrée dans les chunks
récupérés.

#### Constantes

```python
DEFAULT_MODEL = "Qwen/Qwen3-0.6B"

SYSTEM_PROMPT = (
    "You are a precise technical assistant. Answer the user's question using "
    "ONLY the provided context snippets. Be concise, source-grounded, and "
    "self-contained. If the answer is not present in the context, say so."
)
```

Le **system prompt** est crucial : il *cadre* le LLM pour qu'il colle au
contexte fourni au lieu d'inventer. Trois consignes :
1. Précis et technique.
2. **Seulement** le contexte fourni (anti-hallucination).
3. Concis + self-contained (pour que la réponse seule soit lisible).
4. Reconnaître l'absence d'info.

#### Classe `AnswerGenerator`

```python
class AnswerGenerator:
    """Lightweight wrapper around Qwen3-0.6B for grounded answer generation."""

    def __init__(self, model_name=DEFAULT_MODEL, max_new_tokens=256, max_context_length=2000):
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.max_context_length = max_context_length
        self._tokenizer = None
        self._model = None
```

Modèle et tokenizer sont chargés *à la demande* (`_load()`), pas à
l'instanciation : import lazy de `torch` et `transformers`.

#### `_load`

```python
def _load(self) -> None:
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
        assert self._model is not None
        self._model.to("cpu")
```

- **`AutoTokenizer` / `AutoModelForCausalLM`** : factories HuggingFace qui
  choisissent la classe concrète selon le modèle.
- **float16 sur GPU, float32 sur CPU** : sur CPU float16 est lent ; sur GPU
  c'est l'opposé.
- **`device_map="auto"`** (avec `accelerate`) : place les couches sur les
  devices dispos automatiquement.
- **`assert ... is not None`** : aide mypy à comprendre que `_model` n'est
  plus None après l'assignement.

#### `_format_context`

```python
def _format_context(self, chunks: List[Chunk]) -> str:
    parts: List[str] = []
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

Format clair pour le LLM : chaque source numérotée, citée avec son chemin
et ses offsets. Encourage le modèle à *référencer* les sources.

#### `generate`

```python
def generate(self, question: str, chunks: List[Chunk]) -> str:
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
        messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
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

**Détails critiques** :

- **`apply_chat_template(..., enable_thinking=False)`** : Qwen3 a un mode
  « thinking » qui produit du texte de réflexion avant la réponse. On le
  désactive pour avoir une sortie déterministe et économiser des tokens.
- **`return_tensors="pt"`** : retourne des tenseurs PyTorch.
- **`.to(self._model.device)`** : déplace les inputs sur le bon device
  (CPU ou cuda:0).
- **`torch.no_grad()`** : désactive le gradient (économie de mémoire en
  inférence).
- **`do_sample=False, temperature=0.0`** : **génération déterministe**
  (greedy decoding). Même prompt → toujours même sortie. Indispensable
  pour les tests reproductibles.
- **`pad_token_id=eos_token_id`** : Qwen n'a pas de pad_token par défaut ;
  on réutilise EOS pour éviter un warning.
- **Slicing `output[0][inputs["input_ids"].shape[-1]:]`** : `generate`
  retourne le prompt **+** la réponse ; on coupe le prompt.
- **`skip_special_tokens=True`** : enlève `<|im_start|>`, `<|im_end|>` etc.

#### Singleton

```python
_singleton: Optional[AnswerGenerator] = None


def get_generator(model_name: str = DEFAULT_MODEL, max_context_length: int = 2000):
    """Return a process-wide singleton generator (avoids reloading the model)."""
    global _singleton
    if _singleton is None or _singleton.model_name != model_name:
        _singleton = AnswerGenerator(model_name=model_name, max_context_length=max_context_length)
    return _singleton
```

Pattern Singleton lazy : la 1re question coûte le chargement complet de
Qwen (~5 s en CPU), les suivantes sont quasi-gratuites côté model load.

> 💡 **Analogie trading** — C'est l'équivalent de garder une seule connexion MT5 initialisée pour tout le bot au lieu d'appeler `MT5.initialize()` à chaque tick : l'authentification au terminal coûte cher, donc on l'amortit en réutilisant l'instance pendant toute la session.

### 4.15 `src/student/evaluate.py`

**Rôle.** Implémente Recall@k localement (la moulinette officielle a la sienne).

```python
"""Recall@k evaluation against ground-truth source spans."""

OVERLAP_THRESHOLD = 0.05


@dataclass
class EvalReport:
    n_questions: int
    recall_at: Dict[int, float]

    def pretty(self) -> str:
        lines = [
            "Evaluation Results",
            "=" * 40,
            f"Questions evaluated: {self.n_questions}",
        ]
        for k in sorted(self.recall_at):
            lines.append(f"Recall@{k:>2}: {self.recall_at[k]:.3f}")
        return "\n".join(lines)


def overlap_ratio(retrieved: MinimalSource, truth: MinimalSource) -> float:
    """Return |retrieved ∩ truth| / |truth| if same file, else 0."""
    if retrieved.file_path != truth.file_path:
        return 0.0
    truth_len = max(1, truth.last_character_index - truth.first_character_index)
    lo = max(retrieved.first_character_index, truth.first_character_index)
    hi = min(retrieved.last_character_index, truth.last_character_index)
    inter = max(0, hi - lo)
    return inter / truth_len


def question_recall(retrieved, truth, k) -> float:
    """Recall@k for a single question."""
    if not truth:
        return 0.0
    top = retrieved[:k]
    found = 0
    for t in truth:
        for r in top:
            if overlap_ratio(r, t) >= OVERLAP_THRESHOLD:
                found += 1
                break                        # une seule preuve suffit
    return found / len(truth)


def evaluate(student_results_path, dataset_path, ks=(1, 3, 5, 10)) -> EvalReport:
    """Compute recall@k for the student's search results."""
    with open(student_results_path) as fh:
        student = StudentSearchResults.model_validate_json(fh.read())
    with open(dataset_path) as fh:
        dataset = RagDataset.model_validate_json(fh.read())

    truth_by_id: Dict[str, List[MinimalSource]] = {}
    for q in dataset.rag_questions:
        if isinstance(q, AnsweredQuestion):
            truth_by_id[q.question_id] = q.sources

    sums: Dict[int, float] = {k: 0.0 for k in ks}
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

**Définition Recall@k officielle (cf. sujet VI.1.1)** :

```
overlap_ratio(retrieved, truth) = |intersection_caractères| / |truth|
                                 si même file_path, sinon 0

retrieved est "found" pour truth ssi overlap_ratio >= 0.05

Recall@k(question) = nb_truth_found / nb_truth_total
```

**Asymétrie importante** : la formule du student est `|inter| / |truth|`,
pas IoU (`|inter| / |union|`). Donc retrouver un chunk *plus grand* que le
ground-truth ne pénalise pas (tant qu'il en couvre 5%).

**Source du seuil 5%** : sujet PDF chapitre VI.1.1 : « A source is considered
'found' if there is at least 5% overlap between the retrieved source and any
correct source ». La formule exacte (overlap vs IoU vs IoU-min) **n'est pas
détaillée** dans le PDF.

**⚠️ Différence éventuelle avec la moulinette** : le `README.md` de la
moulinette officielle parle explicitement d'**IoU** (« IoU > 5% »). Le
binaire `moulinette-ubuntu` étant un PyInstaller, son code n'est pas
directement lisible. Les Recall@k que le student calcule (`inter/truth`)
et ceux de la moulinette (peut-être IoU) **peuvent légèrement diverger**.
En pratique mesurée sur le dataset public (15 mai 2026) :

| Dataset | Recall@5 (student local) | Recall@5 (moulinette) |
|---|---:|---:|
| docs | 0.84 | 0.83 |
| code | 0.66 | 0.66 |

Les deux passent les seuils. La sortie **moulinette** est ce qui compte
pour la note finale — toujours valider avec elle avant la défense.

### 4.16 `src/student/cli.py`

**Rôle.** Le point d'entrée utilisateur. Une classe `CLI` exposée à Fire ;
chaque méthode = une sous-commande.

#### Header

```python
"""Command-line interface (Python Fire).

Commands:
    index            Build the knowledge-base index from a raw repository.
    search           Search a single query.
    search_dataset   Run a dataset of questions and save StudentSearchResults.
    answer           Answer a single question with retrieved context.
    answer_dataset   Generate answers for a saved search_results file.
    evaluate         Compute recall@k against ground truth.
"""

from __future__ import annotations
import json
import os
from tqdm import tqdm
from .evaluate import evaluate as _evaluate
from .generator import get_generator
from .index import KnowledgeBase
from .models import (
    MinimalAnswer, MinimalSearchResults, MinimalSource, RagDataset,
    StudentSearchResults, StudentSearchResultsAndAnswer,
)

DEFAULT_RAW_DIR = "data/raw/vllm-0.10.1"
DEFAULT_INDEX_DIR = "data/processed"
DEFAULT_OUTPUT_DIR = "data/output"
```

#### Helper `_resolve_repo`

```python
def _resolve_repo(raw_dir: str) -> str:
    """If raw_dir exists as-is use it; else try its only subdirectory."""
    if os.path.isdir(raw_dir):
        entries = [e for e in os.listdir(raw_dir) if not e.startswith(".")]
        subdirs = [...]
        if len(subdirs) == 1 and not any(...):
            return subdirs[0]
    return raw_dir
```

Heuristique : si on pointe sur `data/raw/` mais qu'il contient un seul
sous-dossier `vllm-0.10.1/`, on descend automatiquement. Pratique si
l'utilisateur tape `data/raw` sans le `vllm-0.10.1`.

#### `index`

```python
def index(self, repo_path=DEFAULT_RAW_DIR, save_directory=DEFAULT_INDEX_DIR,
          max_chunk_size=2000, use_embeddings=False,
          embedder_name="sentence-transformers/all-MiniLM-L6-v2") -> str:
    """Build and save the index."""
    repo = _resolve_repo(repo_path)
    if not os.path.isdir(repo):
        raise FileNotFoundError(f"repo not found: {repo}")
    kb = KnowledgeBase.build(repo_root=repo, max_chunk_size=max_chunk_size,
                              use_embeddings=use_embeddings, embedder_name=embedder_name)
    kb.save(save_directory)
    msg = f"Ingestion complete! Indices saved under {save_directory}/"
    print(msg)
    return msg
```

#### `search`

```python
def search(self, query: str, index_directory=DEFAULT_INDEX_DIR, k=10, mode="auto") -> str:
    kb = KnowledgeBase.load(index_directory)
    chunks = kb.search(query, k=k, mode=mode)
    sources = [
        MinimalSource(file_path=c.file_path,
                       first_character_index=c.first_character_index,
                       last_character_index=c.last_character_index)
        for c in chunks
    ]
    out = json.dumps([s.model_dump() for s in sources], indent=2)
    print(out)
    return out
```

Renvoie un JSON formaté. Fire affiche aussi la valeur de retour, d'où le
**double print** dans la sortie (effet attendu).

#### `search_dataset`

```python
def search_dataset(self, dataset_path: str, index_directory=DEFAULT_INDEX_DIR,
                    save_directory=f"{DEFAULT_OUTPUT_DIR}/search_results",
                    k=10, mode="auto") -> str:
    with open(dataset_path) as fh:
        dataset = RagDataset.model_validate_json(fh.read())
    kb = KnowledgeBase.load(index_directory)

    results: list[MinimalSearchResults] = []
    for q in tqdm(dataset.rag_questions, desc="Searching", unit="q"):
        chunks = kb.search(q.question, k=k, mode=mode)
        retrieved = [MinimalSource(file_path=c.file_path,
                                    first_character_index=c.first_character_index,
                                    last_character_index=c.last_character_index)
                     for c in chunks]
        results.append(MinimalSearchResults(question_id=q.question_id,
                                             question_str=q.question,    # ← STR
                                             retrieved_sources=retrieved))

    payload = StudentSearchResults(search_results=results, k=k)
    os.makedirs(save_directory, exist_ok=True)
    out_path = os.path.join(save_directory, os.path.basename(dataset_path))
    with open(out_path, "w") as fh:
        fh.write(payload.model_dump_json(indent=2))
    msg = f"Saved student_search_results to {out_path}"
    print(msg)
    return msg
```

⚠️ **Le piège clé** : `question_str=q.question` — on convertit le champ
`question` (dataset) en `question_str` (output attendu par la moulinette).

#### `answer` et `answer_dataset`

```python
def answer(self, question: str, index_directory=DEFAULT_INDEX_DIR, k=10,
           mode="auto", max_context_length=2000) -> str:
    kb = KnowledgeBase.load(index_directory)
    chunks = kb.search(question, k=k, mode=mode)
    gen = get_generator(max_context_length=max_context_length)
    text = gen.generate(question, chunks)
    print(text)
    return text


def answer_dataset(self, student_search_results_path: str,
                    save_directory=f"{DEFAULT_OUTPUT_DIR}/search_results_and_answer",
                    index_directory=DEFAULT_INDEX_DIR, max_context_length=2000) -> str:
    with open(student_search_results_path) as fh:
        search = StudentSearchResults.model_validate_json(fh.read())
    kb = KnowledgeBase.load(index_directory)
    gen = get_generator(max_context_length=max_context_length)

    chunks_by_offset = {(c.file_path, c.first_character_index, c.last_character_index): c
                        for c in kb.chunks}
    answers: list[MinimalAnswer] = []
    for sr in tqdm(search.search_results, desc="Answering", unit="q"):
        ctx = []
        for s in sr.retrieved_sources:
            key = (s.file_path, s.first_character_index, s.last_character_index)
            chunk = chunks_by_offset.get(key)
            if chunk is not None:
                ctx.append(chunk)
        text = gen.generate(sr.question_str, ctx)
        answers.append(MinimalAnswer(question_id=sr.question_id,
                                      question_str=sr.question_str,
                                      retrieved_sources=sr.retrieved_sources,
                                      answer=text))
    out_payload = StudentSearchResultsAndAnswer(search_results=answers, k=search.k)
    ...
```

**Astuce `chunks_by_offset`** : on reconstruit un dict d'index pour
retrouver le `Chunk` original à partir des trois clés (file_path, début,
fin). Permet de récupérer le `text` qui n'est pas dans le fichier de
résultats de recherche.

#### `evaluate` et `main`

```python
def evaluate(self, student_results_path, dataset_path, k=10, max_context_length=2000) -> str:
    _ = (k, max_context_length)                  # gardés pour compat (ignorés)
    report = _evaluate(student_results_path, dataset_path)
    text = report.pretty()
    print(text)
    return text


def main() -> None:
    """Entry point for python -m student."""
    import fire
    fire.Fire(CLI)
```

`fire.Fire(CLI)` introspect la classe ; toute méthode publique devient une
sous-commande, tout paramètre devient un flag CLI (`--k`, `--mode`).

---

## 5. Concepts techniques exhaustifs

### 5.1 Concepts Python

#### 5.1.1 `from __future__ import annotations`

**Définition** : depuis Python 3.7, on peut activer le « lazy evaluation »
des annotations. Toutes les annotations sont stockées comme chaînes ;
elles ne sont évaluées que par les outils de typing (mypy, IDE) ou via
`typing.get_type_hints()`.

**Pourquoi c'est utile** :
- Permet la syntaxe moderne `list[str]` en Python 3.10 dans certains
  contextes où elle ne marcherait pas runtime.
- Permet les annotations forward-reference sans guillemets : on peut
  écrire `def foo() -> Bar:` même si `Bar` est défini après dans le
  fichier.
- Évite l'évaluation circulaire d'annotations à l'import.

**Où dans le projet** : en tête de quasiment tous les modules.

#### 5.1.2 Annotations de type

| Annotation | Sens |
|---|---|
| `int`, `str`, `float`, `bool` | Types primitifs |
| `List[X]` ou `list[X]` (3.9+) | Liste homogène |
| `Dict[K, V]` ou `dict[K, V]` | Dictionnaire |
| `Tuple[X, Y, Z]` | Tuple à 3 éléments typés |
| `Optional[X]` = `X \| None` | Peut être `None` |
| `Union[A, B]` = `A \| B` (3.10+) | A ou B |
| `Iterator[X]` | Générateur produisant des X |
| `Callable[[Args], Ret]` | Fonction |
| `Any` | N'importe quoi (désactive le check) |

**Où dans le projet** : partout. Imposé par `disallow_untyped_defs`.

#### 5.1.3 `@dataclass`

```python
from dataclasses import dataclass

@dataclass
class Chunk:
    file_path: str
    first_character_index: int
    last_character_index: int
    text: str
```

Génère automatiquement `__init__`, `__repr__`, `__eq__`. Plus léger qu'une
Pydantic BaseModel (pas de validation, mais plus rapide).

**Helpers** :
- `asdict(c)` → dict de tous les fields.
- `dataclasses.fields(c)` → métadonnées sur les fields.

#### 5.1.4 Pydantic v2

Différences majeures avec Pydantic v1 :

| v1 | v2 |
|---|---|
| `BaseModel.parse_obj(d)` | `Model.model_validate(d)` |
| `BaseModel.parse_raw(s)` | `Model.model_validate_json(s)` |
| `instance.json()` | `instance.model_dump_json()` |
| `instance.dict()` | `instance.model_dump()` |

**Où dans le projet** : `models.py` et tout I/O JSON dans `cli.py` et
`evaluate.py`.

#### 5.1.5 Context managers (`with`)

```python
with open(path, "r", encoding="utf-8") as fh:
    text = fh.read()
# fh est fermé automatiquement même si exception
```

Imposé par le sujet pour la gestion des ressources. Utilisé partout pour
les fichiers.

#### 5.1.6 Générateurs et `yield`

```python
def iter_files(root: str) -> Iterator[str]:
    for dirpath, dirnames, filenames in os.walk(root):
        for name in filenames:
            yield os.path.join(dirpath, name)
```

`yield` transforme la fonction en générateur. Économie de mémoire :
on ne construit pas la liste complète.

#### 5.1.7 Compréhensions

```python
[asdict(c) for c in self.chunks]                              # liste
{(c.file_path, c.first, c.last): c for c in kb.chunks}        # dict
[s for s in sims if s > 0]                                    # avec filtre
```

#### 5.1.8 Unpacking `*args` / `**kwargs`

```python
Chunk(**c)                          # dict-unpack en kwargs
self._model.generate(**inputs, ...) # unpacking d'un dict d'inputs
```

#### 5.1.9 `try / except` et chaining `from`

```python
try:
    import bm25s
except ImportError as exc:
    raise RuntimeError("bm25s is required") from exc
```

`from exc` préserve la chaîne pour le debug (PEP 3134).

#### 5.1.10 Lazy imports

```python
def _load(self) -> None:
    if self._model is not None:
        return
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    ...
```

Importer **dans la fonction** au lieu du module : économise le temps de
démarrage si la fonction n'est jamais appelée (path BM25-only n'importe
jamais `torch`).

> 💡 **Analogie trading** — Comme un EA multi-stratégies qui ne charge le module "news filter" qu'à l'approche d'un événement macro : inutile de monter la lib de scraping en mémoire si la session courante tourne en pur scalping technique.

#### 5.1.11 `TYPE_CHECKING`

```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

def _get_embedder(self) -> "SentenceTransformer":
    ...
```

`TYPE_CHECKING` est `False` au runtime, `True` quand mypy analyse. Permet
d'utiliser un type dans les annotations sans importer la lib au runtime.
Les annotations forward sont entre guillemets pour éviter `NameError`.

#### 5.1.12 Singleton via variable globale

```python
_singleton: Optional[AnswerGenerator] = None

def get_generator(...):
    global _singleton
    if _singleton is None:
        _singleton = AnswerGenerator(...)
    return _singleton
```

Pattern simple, pas thread-safe (acceptable ici, mono-thread).

#### 5.1.13 Slicing et offsets

```python
text[start:end]               # substring entre offsets
output[0][inputs.shape[-1]:]  # slice à partir de l'index de fin du prompt
```

Idiomatique en Python ; les offsets négatifs comptent depuis la fin
(`text[-3:]`).

#### 5.1.14 Regex avec look-around

```python
re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
```

- `(?<= ...)` lookbehind (sans consommer).
- `(?= ...)` lookahead.
- Tous les deux : "splitter à ce point" sans mettre de caractères dans
  les groupes capturés.

### 5.2 Concepts NLP / IR

#### 5.2.1 Tokenisation

Découpage d'un texte en unités plus petites (tokens) pour le traitement.
Stratégies :
- **Whitespace tokenization** : split sur les espaces (naïf).
- **Identifier-aware** (ce projet) : split sur les non-alphanumériques,
  puis sur les transitions camelCase.
- **Subword** (BPE, WordPiece) : utilisé par les LLM modernes.

#### 5.2.2 BM25

**Formule canonique** :
```
score(D, Q) = Σ_{t in Q} IDF(t) * (TF(t,D) * (k1+1)) /
                          (TF(t,D) + k1 * (1 - b + b * |D|/avgdl))
```

- `TF(t, D)` : fréquence du terme `t` dans le document `D`.
- `IDF(t) = log((N - df + 0.5) / (df + 0.5))` : rareté du terme.
- `k1 ≈ 1.2`, `b ≈ 0.75` : hyperparamètres de saturation et normalisation
  de longueur.

`bm25s` implémente cette formule en sparse, très efficacement.

> 💡 **Analogie trading** — BM25 ressemble à un EA qui score la qualité d'un setup à partir de plusieurs critères pondérés (RSI, distance à la VWAP, volume). La saturation TF est l'équivalent de la conviction qui plafonne : voir le même signal se répéter dix fois n'augmente plus le score au-delà d'un seuil, exactement comme empiler dix touches d'un même support n'ajoute pas linéairement à la qualité du niveau.

#### 5.2.3 TF-IDF vs BM25

- TF-IDF : produit `TF × IDF`, sans saturation ni normalisation.
- BM25 : ajoute saturation TF (à partir d'un certain seuil, plus de TF
  n'aide plus) et pondère par la longueur du doc.

#### 5.2.4 Embeddings denses

Un vecteur de 384 ou 768 floats qui capture le sens d'un texte. Produits
par un *bi-encoder* (Sentence-Transformers).

**Similarité cosinus** :
```
cos(u, v) = (u · v) / (||u|| * ||v||)
```

Si on normalise (`||v|| = 1`), c'est simplement le produit scalaire.

> 💡 **Analogie trading** — Les embeddings denses permettent de matcher par le sens plutôt que par mot-clé exact. Un signal "breakout sur le plus haut de la session de Londres" et "cassure du high asiatique étendu sur l'ouverture EU" sont lexicalement très différents mais sémantiquement proches : c'est ce type de proximité que la similarité cosinus capte, là où BM25 raterait le rapprochement.

#### 5.2.5 Reciprocal Rank Fusion (RRF)

Fusion de plusieurs classements en un seul score, **sans hyperparamètre**
significatif :

```
score_RRF(d) = Σ_method  1 / (k + rank_method(d))
```

Avec `k = 60` par convention (Cormack et al., SIGIR 2009).

> 💡 **Analogie trading** — RRF fonctionne comme une confluence de signaux multi-stratégies : Gold scalping, London breakout et M5 momentum "votent" sur les mêmes paires, et un setup classé haut par plusieurs stratégies remonte au top de la liste finale. Comme RRF, cette fusion ne demande pas de calibrer des poids relatifs entre stratégies — seul le rang compte.

#### 5.2.6 Chunking strategies

| Stratégie | Avantages | Inconvénients |
|---|---|---|
| Fixed-size | Simple | Coupe au milieu des phrases/fonctions |
| Sliding window | Évite les coupures abruptes (overlap) | Redondance |
| Recursive splitting | Hiérarchique (paragraphe → phrase) | Complexe |
| **AST-based** (Python) | Frontières syntaxiques | Spécifique au langage |
| **Header-based** (Markdown) | Frontières sémantiques | Sections inégales |

> 💡 **Analogie trading** — Chunker sans casser une unité cohérente, c'est comme découper un historique de bougies sans couper une structure de prix au milieu : on préfère segmenter à la fin d'une session ou d'un swing plutôt qu'au hasard, sous peine de perdre le contexte qui rendait la donnée exploitable.

#### 5.2.7 Recall@k

```
Recall@k = nb_passages_pertinents_dans_top_k / nb_passages_pertinents_total
```

Comparé à *Precision@k* (parmi les top-k, combien sont pertinents).

> 💡 **Analogie trading** — Recall@k joue le rôle d'un backtest sur historique : on confronte le système à un jeu de questions de vérité terrain pour mesurer combien de "bons trades" (passages pertinents) il aurait su capter dans son top-k, indépendamment de l'opinion qu'on a de sa logique interne.

#### 5.2.8 IoU vs Overlap

- **IoU** : `|A ∩ B| / |A ∪ B|`.
- **Overlap (ce projet)** : `|A ∩ B| / |truth|`.

Asymétrique : retrieved peut être plus grand que truth sans pénalité.

### 5.3 Concepts LLM / Génération

#### 5.3.1 Anatomie d'un LLM

- **Tokenizer** : encode texte → tokens (ids).
- **Embedding layer** : id → vecteur.
- **Transformer layers** : self-attention + FFN, empilés.
- **LM head** : projette en logits sur le vocabulaire.

#### 5.3.2 Chat template

Les LLM modernes (Qwen, Llama, etc.) sont fine-tunés avec un format
spécifique d'instruction. Exemple Qwen3 :

```
<|im_start|>system
{prompt système}
<|im_end|>
<|im_start|>user
{question}
<|im_end|>
<|im_start|>assistant
{réponse}
```

`tokenizer.apply_chat_template(messages, ...)` formate automatiquement.

#### 5.3.3 Generation parameters

- `max_new_tokens` : limite de tokens générés.
- `do_sample=True` : sampling stochastique. `False` = greedy (déterministe).
- `temperature` : douceur du softmax avant sampling. 0 = déterministe.
- `top_k`, `top_p` : tronquent la distribution avant sampling.
- `repetition_penalty` : pénalise les tokens déjà vus.

#### 5.3.4 Greedy vs sampling

- **Greedy** (`do_sample=False`) : prend toujours le token le plus probable.
  Déterministe, reproductible, parfois répétitif.
- **Sampling** : tire un token selon la distribution. Plus créatif, moins
  reproductible.

Ce projet utilise greedy pour la reproductibilité.

> 💡 **Analogie trading** — Le greedy decoding correspond à un backtest reproductible : mêmes données d'entrée, mêmes paramètres → exactement la même séquence de trades à chaque rejeu. Le sampling stochastique serait l'équivalent d'un EA avec une part d'aléa dans l'exécution, utile pour explorer mais impossible à débugger pas à pas.

#### 5.3.5 KV cache

Optimisation transformer : à chaque token généré, on cache les `K` et
`V` des couches précédentes pour ne pas refaire le calcul. transformers
le fait automatiquement dans `model.generate()`.

#### 5.3.6 Quantization (non utilisée ici)

Conversion fp16 → int8/int4 pour économiser de la VRAM. Aurait permis de
faire tourner Qwen3 sur 1.5 GB de VRAM au lieu de 3 GB.

### 5.4 Concepts d'architecture

#### 5.4.1 Layered architecture

Modules organisés en couches superposées, dépendances unidirectionnelles
(haut → bas). Permet d'isoler les changements.

#### 5.4.2 Singleton pattern

Une seule instance d'une classe pour tout le processus. Utilisé pour les
ressources lourdes (modèle ML).

> 💡 **Analogie trading** — Même logique qu'un EA de risk management (type RiskGuard) qu'on instancie une seule fois et qui surveille tous les ordres : dupliquer l'instance dupliquerait les vérifications et risquerait de désynchroniser l'état (compteur de pertes journalières, exposition cumulée). Une seule autorité, partagée par tous les appelants.

#### 5.4.3 Strategy pattern

Plusieurs algos interchangeables derrière une même interface. `kb.search(mode="...")`
choisit BM25 / dense / hybrid.

#### 5.4.4 Builder pattern via classmethod

```python
class KnowledgeBase:
    @classmethod
    def build(cls, ...) -> "KnowledgeBase": ...
    @classmethod
    def load(cls, ...) -> "KnowledgeBase": ...
```

Deux constructeurs alternatifs. Plus lisible que des paramètres optionnels.

#### 5.4.5 Lazy initialization

Charger seulement quand nécessaire. Économie de temps et de mémoire.
Utilisé pour le modèle, le tokenizer, l'embedder.

#### 5.4.6 DTO (Data Transfer Object)

Objets dédiés à transporter des données entre couches, sans logique.
Les modèles Pydantic du projet sont des DTOs.

### 5.5 Concepts transversaux

#### 5.5.1 Gestion des exceptions

Le sujet impose try/except gracieux. Exemples dans le projet :
- `read_file_safely` (ingest.py) capture `OSError`.
- `chunk_python` capture `SyntaxError` et fallback en text chunking.
- `import bm25s` capture `ImportError` avec message clair.

> 💡 **Analogie trading** — C'est l'approche d'un EA qui ne crash pas quand le broker renvoie une erreur (`OrderSend` qui échoue, requote, slippage) : on attrape l'erreur, on log, et on applique une règle de repli (skip le signal, retenter une fois, ou désactiver la stratégie) plutôt que de stopper le bot entier au milieu d'une session.

#### 5.5.2 Logging vs print

Le projet utilise `print()` partout (simple, suffit pour ce projet). En
production on remplacerait par `logging` avec niveaux (INFO, DEBUG, ERROR).

#### 5.5.3 Reproductibilité

- `do_sample=False, temperature=0` → génération déterministe.
- `uv.lock` → versions exactes des deps.
- `bm25` est déterministe par construction.
- `np.random.seed(...)` non utilisé (pas de randomisation côté retrieval).

#### 5.5.4 Performance

- **bm25s** vectorisé en C/numpy : retrieval < 5 ms par query.
- **Dense** : `embeddings @ q_vec` (matmul) pour scorer tout le corpus
  en une opération.
- **Lazy loading** : aucun coût quand non utilisé.
- **Batch encoding** : `model.encode(texts, batch_size=64)` plutôt que un
  par un.

#### 5.5.5 Sécurité

- Pas d'eval/exec sur user input.
- `errors="ignore"` à la lecture (pas de crash sur binaire).
- Pas de réseau au runtime (modèle déjà téléchargé).

---

## 6. Dépendances externes

### 6.1 pydantic (≥ 2.6)

**À quoi ça sert** : validation et (de)sérialisation de données
structurées. Garantit que les JSON entrants et sortants respectent les
schémas attendus.

**Usage dans le projet** :
- `BaseModel` pour tous les modèles (`MinimalSource`, `RagDataset`, etc.).
- `Field(default_factory=...)` pour les valeurs par défaut calculées.
- `model_validate_json(s)` pour parser un JSON externe.
- `model_dump_json(indent=2)` pour écrire un JSON.

**Concepts clés** :
- v1 vs v2 (méthodes renommées).
- Validators custom (`@validator`, non utilisé ici).
- `model_config = ConfigDict(...)` pour configurer (strict mode, etc.).

**Alternatives** : `attrs`, `dataclasses` (sans validation),
`marshmallow`.

### 6.2 fire (≥ 0.6)

**À quoi ça sert** : transformer automatiquement une fonction/classe en
CLI. Pas de parsing manuel d'argparse.

**Usage** : `fire.Fire(CLI)` dans `cli.py:main()`. Chaque méthode de
`CLI` devient une sous-commande, chaque paramètre un flag.

**Concept clé** : Fire introspect via `inspect` et type-aware (mais
moins strict qu'argparse).

**Alternatives** : `argparse` (stdlib, verbeux), `click`, `typer`.

### 6.3 tqdm (≥ 4.66)

**À quoi ça sert** : barres de progression.

**Usage** : `for x in tqdm(iter, desc="...", unit="...")`. Imposé par
le sujet pour les opérations longues.

**Alternatives** : `rich.progress`, `alive_progress`.

### 6.4 bm25s (≥ 0.2.0)

**À quoi ça sert** : implémentation BM25 ultra-rapide en numpy/scipy sparse.

**Usage** :
```python
import bm25s
bm = bm25s.BM25()
bm.index(corpus_tokens)              # list[list[str]]
docs, scores = bm.retrieve([tokens], k=10)
bm.save(directory)
bm.load(directory)
```

**Concepts clés** :
- Sparse matrix interne (chaque doc = vecteur creux sur le vocabulaire).
- Pas de stemming par défaut (utilise PyStemmer si besoin).
- Pas de tokenization built-in : on lui passe déjà les tokens.

**Alternatives** :
- `rank_bm25` (pure Python, lent).
- `Whoosh` (full-text search).
- `Elasticsearch`/`OpenSearch` (overkill).

### 6.5 transformers (≥ 4.44)

**À quoi ça sert** : interface unifiée pour charger et utiliser les
modèles HuggingFace.

**Usage** :
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.6B")
output = model.generate(**inputs, max_new_tokens=256)
```

**Concepts clés** :
- `AutoXxx` : factory qui choisit la classe selon le modèle.
- `from_pretrained` : télécharge depuis HuggingFace Hub et cache local.
- `apply_chat_template(messages, ...)` : format spécifique au modèle.
- `pipeline("text-generation", model=...)` : wrapper plus haut niveau
  (non utilisé ici car moins flexible).

### 6.6 torch (≥ 2.2)

**À quoi ça sert** : backend tenseurs/autograd pour transformers.

**Usage** :
```python
import torch
torch.cuda.is_available()           # détection GPU
torch.no_grad()                     # context manager (pas de gradient)
torch.float16, torch.float32        # dtypes
```

**Concepts clés** :
- Tensors (analogues à numpy arrays, mais avec autograd et GPU).
- Devices (`cpu`, `cuda:0`).
- Autograd (non utilisé en inférence).
- `with torch.no_grad():` ↔ économie de mémoire.

### 6.7 accelerate (≥ 0.30)

**À quoi ça sert** : utilitaires HuggingFace pour le multi-device / DDP.
Utilisé ici uniquement pour `device_map="auto"`.

### 6.8 numpy (≥ 1.26)

**À quoi ça sert** : arrays N-D, algèbre linéaire.

**Usage** :
- Embeddings stockés en `np.ndarray` float32.
- Similarité : produit matriciel `@`.
- Top-k : `np.argpartition`, `np.argsort`.
- I/O : `np.save`, `np.load`.

### 6.9 sentence-transformers (≥ 2.7)

**À quoi ça sert** : encodage de texte en vecteurs denses sémantiques.

**Usage** :
```python
from sentence_transformers import SentenceTransformer
m = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
vecs = m.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
```

**Concepts clés** :
- Bi-encoder (par opposition au cross-encoder, plus précis mais plus
  lent).
- Modèles populaires : MiniLM (rapide), MPNet (équilibré), BGE (top
  qualité 2024).

### 6.10 chromadb (≥ 0.5)

Présent dans `pyproject.toml` (recommandé par le sujet) mais **non utilisé**
dans le code. Aurait servi si on stockait les embeddings dans une vector
DB persistante avec query API.

### 6.11 PyStemmer (≥ 2.2.0)

Stemmer (réduction des mots à leur racine : `running` → `run`). Présent
en dépendance optionnelle pour bm25s mais non activé dans le code (le
tokenizer custom suffit).

---

## 7. Flux de données

### 7.1 Schéma global

```
                       ┌──────────────────┐
                       │  data/raw/       │
                       │  vllm-0.10.1/    │
                       │  (~1900 fichiers)│
                       └────────┬─────────┘
                                │
                                ▼ student index
                       ┌──────────────────┐
                       │  ingest          │
                       │  collect_files() │
                       │  → List[(path,   │
                       │     text)]       │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  chunking        │
                       │  chunk_file()    │
                       │  → List[Chunk]   │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  tokenizer       │
                       │  tokenize_batch()│
                       │  → List[List[str]]
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  bm25s.BM25.index│
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  data/processed/ │ ⟵ persistance
                       │  - chunks.json   │
                       │  - bm25_index/   │
                       │  - meta.json     │
                       │  - dense_index/  │
                       └──────────────────┘

                       ┌──────────────────┐
                       │  user query      │
                       └────────┬─────────┘
                                │
                                ▼ student search
                       ┌──────────────────┐
                       │  KB.load()       │
                       │  + tokenize(q)   │
                       │  + bm25.retrieve │
                       │  (+ dense + RRF) │
                       └────────┬─────────┘
                                │ List[Chunk]
                                ▼
                       ┌──────────────────┐
                       │  format JSON     │
                       │  (MinimalSource) │
                       └────────┬─────────┘
                                ▼
                       JSON stdout / file

                       ┌──────────────────┐
                       │  user query      │
                       └────────┬─────────┘
                                ▼ student answer
                       (idem search) + ────┐
                                ▼          │
                       ┌──────────────────┐│
                       │  AnswerGenerator ││
                       │  - _load model   ││
                       │  - _format_ctx   ││
                       │  - apply_chat... ││
                       │  - generate()    ││
                       │  - decode        ││
                       └────────┬─────────┘│
                                ▼          ▼
                          text                JSON (avec answer)
```

### 7.2 Structures de données principales

#### `Chunk` (dataclass interne)
```python
@dataclass
class Chunk:
    file_path: str
    first_character_index: int
    last_character_index: int
    text: str
```
Représente un morceau de fichier avec ses offsets exacts.

#### `chunks.json` (sortie disque)
```json
[
    {
        "file_path": "data/raw/vllm-0.10.1/docs/x.md",
        "first_character_index": 0,
        "last_character_index": 1800,
        "text": "# Heading\n..."
    },
    ...
]
```

#### `StudentSearchResults` (sortie `search_dataset`)
```json
{
    "search_results": [
        {
            "question_id": "uuid",
            "question_str": "What is X?",
            "retrieved_sources": [
                {
                    "file_path": "data/raw/vllm-0.10.1/...",
                    "first_character_index": 0,
                    "last_character_index": 1800
                },
                ...
            ]
        },
        ...
    ],
    "k": 10
}
```

#### `StudentSearchResultsAndAnswer` (sortie `answer_dataset`)
Idem mais chaque entrée a en plus `"answer": "..."`.

#### `RagDataset` (input des datasets)
```json
{
    "rag_questions": [
        {
            "question_id": "uuid",
            "question": "What is X?",
            "answer": "X is ...",
            "sources": [
                {"file_path": "...", "first_character_index": 0, "last_character_index": 100}
            ],
            "difficulty": "synthetic",
            "is_valid": true
        }
    ]
}
```
Note : les champs `difficulty` et `is_valid` ne sont pas dans le modèle
Pydantic du student → ignorés silencieusement (Pydantic v2 par défaut).

### 7.3 Interface "publique" (CLI)

| Commande | Input | Output |
|---|---|---|
| `index` | `data/raw/vllm-0.10.1/` | `data/processed/` |
| `search QUERY` | string + `data/processed/` | JSON sources stdout |
| `search_dataset --dataset_path X` | JSON dataset + `data/processed/` | JSON results file |
| `answer QUERY` | string + `data/processed/` | string stdout |
| `answer_dataset --student_search_results_path X` | JSON results + `data/processed/` | JSON results+answers file |
| `evaluate --student_results_path X --dataset_path Y` | 2 JSONs | text report stdout |

---

## 8. Tests

### 8.1 État actuel

Le projet n'inclut **aucun** test unitaire formel. La cible `make test`
lance `pytest -q || true` (n'échoue jamais).

### 8.2 Stratégie réelle (validation manuelle)

Les tests réels du projet sont :

1. **`make lint`** : flake8 + mypy doivent passer (vérifié, OK).
2. **Run end-to-end** : `index` → `search_dataset` → `evaluate` doit
   donner Recall@5 ≥ 80% (docs) et ≥ 50% (code).
3. **Moulinette officielle** : binaire `moulinette-ubuntu`/`moulinette-fedora`
   fourni par 42, qui valide le format JSON et calcule le recall.

### 8.3 Ce qu'on aurait pu tester

```python
# test_tokenizer.py
def test_camelcase_split():
    assert tokenize("OpenAIServer") == ["open", "ai", "server"]

def test_stopwords_removed():
    assert "the" not in tokenize("the server")

# test_chunking.py
def test_python_ast_chunking():
    code = "def foo():\n    pass\n\ndef bar():\n    pass\n"
    chunks = chunk_python("test.py", code, max_chunk_size=2000)
    assert len(chunks) == 2  # foo et bar séparés

def test_offsets_preserved():
    text = "ABCDEFGH"
    chunks = chunk_text("test.txt", text, max_chunk_size=3)
    for c in chunks:
        assert c.text == text[c.first_character_index:c.last_character_index]

# test_evaluate.py
def test_overlap_ratio_same_file():
    r = MinimalSource(file_path="a.py", first_character_index=0, last_character_index=100)
    t = MinimalSource(file_path="a.py", first_character_index=50, last_character_index=150)
    assert overlap_ratio(r, t) == 50/100  # 50 chars in common / 100 truth_len

def test_overlap_different_files():
    r = MinimalSource(file_path="a.py", first_character_index=0, last_character_index=100)
    t = MinimalSource(file_path="b.py", first_character_index=0, last_character_index=100)
    assert overlap_ratio(r, t) == 0.0
```

### 8.4 Couverture (estimée)

| Module | Testé manuellement | Testé via end-to-end |
|---|---|---|
| `tokenizer.py` | non | implicitement (via indexation) |
| `chunking.py` | non | implicitement |
| `ingest.py` | non | implicitement |
| `index.py` | non | implicitement |
| `evaluate.py` | non | oui (via moulinette) |
| `generator.py` | non | oui (commande `answer`) |
| `cli.py` | oui (commandes lancées à la main) | oui |
| `models.py` | non | oui (parse JSON) |

### 8.5 Ce qui manque (suggéré pour aller plus loin)

- **Tests unitaires** : tokenizer, chunking (offsets), evaluate (overlap).
- **Tests d'intégration** : un mini-corpus de 5 fichiers, indexer + search,
  vérifier que le bon chunk est top-1.
- **Property-based tests** (`hypothesis`) : pour chaque chunk produit,
  `text == file_text[first:last]`.
- **Regression tests** : snapshot des Recall@k sur un dataset fixe.
- **GitHub Actions** : exécuter lint + tests à chaque push.

---

## 9. Critique du code

### 9.1 Forces

1. **Architecture propre** : couches bien définies, pas de cycle d'import,
   chaque module a une responsabilité unique.
2. **Type hints complets** : tout le code est typé, mypy passe.
3. **Lazy loading partout** : on ne paie pas le coût de transformers/torch
   si on fait juste de la recherche BM25.
4. **Persistance correcte** : le format `chunks.json + bm25_index/` est
   simple et reproductible.
5. **Robustesse** : `try/except` aux endroits critiques, fallback chunking
   en cas de SyntaxError, `errors="ignore"` à la lecture.
6. **Performance** : tient largement le budget (7 s indexation vs 5 min
   max, retrieval < 5 ms).
7. **Bonus bien intégrés** : embeddings + RRF avec un design qui ne casse
   pas le path BM25-only.
8. **Documentation** : 3 README cohérents (public + apprentissage + code
   commenté).
9. **Reproductibilité** : génération greedy, `uv.lock` figé.
10. **Singleton du modèle** : évite de recharger 1 Go à chaque question.

### 9.2 Faiblesses / dette technique

1. **Aucun test unitaire** — la cible `make test` est cosmétique.
2. **Pas de logger** : `print()` partout. Difficile de filtrer le bruit
   en production.
3. **Singleton non thread-safe** : `get_generator` a une race condition si
   appelé en concurrent (acceptable ici car CLI mono-thread).
4. **`chunks_by_offset`** reconstruit en mémoire à chaque `answer_dataset`
   (O(N_chunks)). Pourrait être pickle-cached.
5. **Pas de gestion VRAM** : sur GPU 4 Go, charger Qwen3 + le contexte
   complet peut OOM (vu en local). Aucun fallback automatique.
6. **`max_context_length`** est par-source, pas global. Sur 10 sources de
   2000 chars chacune, le contexte total est 20k chars (~5k tokens) → risque
   de dépasser le context window de Qwen3 (32k).
7. **Tokenizer naïf** : pas de stemming, pas de gestion des accents/Unicode.
   Suffisant pour le corpus vLLM (anglais code/docs) mais limité.
8. **Heuristique `_resolve_repo`** trop magique : si l'utilisateur a deux
   dossiers dans `data/raw/`, comportement non déterministe.
9. **Pas de validation que `relative_to="."`** correspond bien au cwd
   appelant : si on lance depuis ailleurs, les paths sont cassés.
10. **`question` vs `question_str`** : incohérence entre le sujet PDF (V.7
    montre `question: str`) et la moulinette (qui attend `question_str`).
    Le student a choisi la moulinette, c'est le bon choix mais c'est fragile.
11. **`chromadb` et `PyStemmer` dans les deps** : non utilisés, font
    grossir le `.venv` inutilement (~50 Mo).
12. **`evaluate(--k --max_context_length ...)`** : ces paramètres sont
    acceptés mais ignorés (`_ = (k, max_context_length)`). Compat moulinette,
    mais c'est trompeur côté API.

### 9.3 Bugs potentiels / edge cases

1. **`np.argpartition(-sims, n-1)`** : si `n == 0`, erreur ; protégé par
   `top_n = min(k, len(self.chunks))` mais pas si `len(chunks) == 0`.
2. **`chunk_python`** : si toutes les top-level sont commentées au
   `node.col_offset` peut être 0 sur la ligne 1 → OK, mais limite à
   garder en tête.
3. **`chunk_markdown`** : un `#` dans un bloc de code (```python # foo```) est
   pris pour un header.
4. **`read_file_safely`** : retourne `""` sur erreur → un fichier illisible
   est silencieusement ignoré sans warning à l'utilisateur.
5. **`apply_chat_template(enable_thinking=False)`** : si Qwen change son
   API dans une version future, ce flag pourrait disparaître silencieusement
   (transformers v5 changera des choses).
6. **`device_map="auto"` + CPU** : on passe `None`, mais on appelle quand
   même `.to("cpu")` ensuite — pourrait être simplifié.

### 9.4 Améliorations suggérées (par ordre d'impact)

1. **Ajouter pytest + couvrir tokenizer/chunking/evaluate** : 1 h de
   travail, augmente massivement la confiance.
2. **Remplacer `print` par `logging`** avec niveaux configurables.
3. **CI GitHub Actions** : lint + tests + dry-run de l'indexation sur
   un mini-corpus.
4. **Caching disque pour `chunks_by_offset`** dans `answer_dataset`.
5. **Tronquer le contexte total** dans `_format_context` (par token-count
   plutôt qu'en chars).
6. **Query expansion bonus** : ré-écrire la query avec un LLM ou ajouter
   des synonymes.
7. **Re-ranking croisé** (cross-encoder) sur les top-K : gain de précision.
8. **Supprimer chromadb et PyStemmer** des deps si non utilisés.

---

## 10. Glossaire

| Terme | Définition |
|---|---|
| **RAG** | Retrieval-Augmented Generation — pattern qui combine recherche d'info et génération LLM. |
| **Chunk** | Morceau d'un document, unité atomique de l'index. |
| **Chunking** | Action de découper un document en chunks. |
| **Token** | Unité atomique de texte après tokenisation (mot, sous-mot, etc.). |
| **Tokenizer** | Algorithme/objet qui convertit texte ↔ tokens. |
| **BM25** | Best Matching 25, fonction de scoring lexicale dérivée de TF-IDF. |
| **TF-IDF** | Term Frequency × Inverse Document Frequency. |
| **Recall@k** | Proportion des passages pertinents retrouvés dans le top-k. |
| **Precision@k** | Proportion des top-k qui sont pertinents. |
| **IoU** | Intersection over Union, métrique d'overlap symétrique. |
| **Embedding** | Vecteur dense représentant le sens d'un texte. |
| **Bi-encoder** | Modèle qui encode séparément les deux textes à comparer. |
| **Cross-encoder** | Modèle qui prend les deux textes ensemble (plus précis, plus lent). |
| **RRF** | Reciprocal Rank Fusion, méthode de fusion de classements. |
| **AST** | Abstract Syntax Tree, représentation arborescente du code source. |
| **LLM** | Large Language Model. |
| **Qwen3-0.6B** | Modèle d'Alibaba, 600 M de paramètres, multilingue. |
| **fp16 / fp32** | Précisions float 16 et 32 bits. |
| **Greedy decoding** | Génération qui prend toujours le token le plus probable. |
| **Sampling** | Génération stochastique selon la distribution. |
| **Chat template** | Format de prompt spécifique à un LLM fine-tuné chat. |
| **VRAM** | Vidéo-RAM = mémoire GPU. |
| **OOM** | Out of Memory. |
| **Pydantic** | Lib Python de validation et sérialisation via modèles typés. |
| **DTO** | Data Transfer Object. |
| **Singleton** | Pattern qui garantit une seule instance par processus. |
| **PEP** | Python Enhancement Proposal. |
| **PEP 8** | Style guide officiel Python. |
| **PEP 257** | Convention docstrings. |
| **PEP 517/518** | Build system Python moderne (`pyproject.toml`). |
| **PEP 621** | Métadonnées projet dans `pyproject.toml`. |
| **PEP 3134** | Chaining d'exceptions (`raise X from Y`). |
| **flake8** | Linter de style PEP 8. |
| **mypy** | Type-checker statique. |
| **uv** | Package manager Rust pour Python (remplace pip+venv). |
| **CLI** | Command-Line Interface. |
| **fire** | Lib Google pour créer une CLI à partir d'une classe. |
| **HF Hub** | HuggingFace Hub, registry de modèles ML. |
| **vLLM** | Moteur d'inférence LLM open-source — la base de connaissances ici. |
| **Moulinette** | Programme d'évaluation automatique de 42. |
| **Defense** | Soutenance orale d'un projet 42 devant un évaluateur. |

---

## 11. Cheatsheet

### 11.1 Commandes utiles

```bash
# Setup
make install                                  # uv venv && uv sync
source .venv/bin/activate                     # activer le venv
mkdir -p data/raw && unzip vllm-0.10.1.zip -d data/raw
unzip datasets_public.zip -d data/

# Quotidien
make lint                                     # flake8 + mypy (flags imposés)
make clean                                    # supprime __pycache__ etc.

# Indexation
uv run python -m student index                          # défaut max_chunk_size=2000
uv run python -m student index --max_chunk_size 1500    # taille custom
uv run python -m student index --use_embeddings True    # bonus dense

# Recherche
uv run python -m student search "MA QUESTION" --k 10
uv run python -m student search "MA QUESTION" --mode bm25
uv run python -m student search "MA QUESTION" --mode hybrid

# Génération
uv run python -m student answer "MA QUESTION" --k 5

# Pipeline batch
uv run python -m student search_dataset \
    --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json \
    --save_directory data/output/search_results --k 10

uv run python -m student answer_dataset \
    --student_search_results_path data/output/search_results/dataset_docs_public.json \
    --save_directory data/output/search_results_and_answer

# Évaluation
uv run python -m student evaluate \
    --student_results_path data/output/search_results/dataset_docs_public.json \
    --dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json

# Moulinette officielle
./moulinette-ubuntu evaluate_student_search_results \
    data/output/search_results/dataset_docs_public.json \
    data/datasets/AnsweredQuestions/dataset_docs_public.json \
    --k 10 --threshold 0.80
```

### 11.2 Snippets fréquents

**Lire un JSON dans un modèle Pydantic** :
```python
with open(path, "r", encoding="utf-8") as fh:
    obj = MyModel.model_validate_json(fh.read())
```

**Écrire un modèle Pydantic en JSON** :
```python
with open(path, "w", encoding="utf-8") as fh:
    fh.write(obj.model_dump_json(indent=2))
```

**Charger l'index et faire une recherche** :
```python
from student.index import KnowledgeBase
kb = KnowledgeBase.load("data/processed")
chunks = kb.search("ma question", k=10, mode="auto")
for c in chunks:
    print(c.file_path, c.first_character_index, c.last_character_index)
```

**Générer une réponse** :
```python
from student.generator import get_generator
gen = get_generator()
print(gen.generate("ma question", chunks))
```

### 11.3 FAQ / Problèmes courants

**Q : `flake8` se plaint de lignes trop longues mais `pyproject.toml`
fixe 100.**
A : flake8 ne lit pas `pyproject.toml`. Vérifier qu'un `.flake8` ou
`setup.cfg` existe avec `max-line-length = 100`.

**Q : `make lint` mypy échoue avec "Unused `type: ignore`".**
A : `ignore_missing_imports = True` rend les `# type: ignore` redondants
sur les imports de libs externes. Les supprimer.

**Q : `Recall@5 = 0.0`.**
A : 99% du temps, mismatch de `file_path` entre l'output student et le
dataset. Vérifier que `collect_files(..., relative_to=".")` est utilisé
et que le cwd est la racine du projet.

**Q : `Field required: question_str` à la validation moulinette.**
A : Le modèle `MinimalSearchResults` doit utiliser `question_str`, pas
`question`. C'est le seul nom accepté par la moulinette.

**Q : `torch.OutOfMemoryError: CUDA out of memory`.**
A : Réduire `--k` ou `--max_context_length`. Sur 4 Go de VRAM, k=3
et context=600 fonctionnent.

**Q : « ImportError: bm25s ».**
A : `uv sync` n'a pas tourné, ou le venv n'est pas activé.

**Q : Comment relancer un index propre ?**
A : `rm -rf data/processed/ && uv run python -m student index`.

**Q : `python -m student --help` n'affiche pas grand chose.**
A : Comportement de Fire — il faut taper `python -m student` pour voir
la liste des commandes, puis `python -m student index --help` pour les
flags d'une commande.

**Q : Erreur "No module named 'student'".**
A : `pip install -e .` ou `uv sync` (qui installe le package en mode
editable).

**Q : La génération est lente sur CPU.**
A : Normal — Qwen3-0.6B en fp32 sur CPU c'est ~30 s par question.
Solutions :
- Avoir un GPU (même 4 Go).
- Réduire `max_new_tokens` (256 → 128).
- Quantization (bitsandbytes, non implémenté ici).

---

## 12. Pour aller plus loin

### 12.1 Sujets à explorer

#### Côté retrieval
- **Cross-encoder re-ranking** : prendre les top-50 BM25, ré-ordonner
  les top-10 avec un cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`).
  Gain de précision élevé.
- **HyDE** (Hypothetical Document Embeddings) : générer une réponse fake
  avec le LLM, l'encoder, et chercher avec ce vecteur.
- **ColBERT** (late interaction) : embeddings par token au lieu d'un
  vecteur global, retrieval plus précis.
- **Query expansion** : ajouter des synonymes, ou demander à un LLM de
  réécrire la query.
- **Filtres metadata** : filtrer les chunks par langage (`.py` vs `.md`)
  selon la nature de la question.

#### Côté chunking
- **Recursive chunking** (LangChain) : essayer plusieurs séparateurs
  par ordre de priorité (paragraphe → phrase → mot).
- **Semantic chunking** : couper là où les phrases changent de sujet
  (mesuré par les embeddings).
- **Code-aware chunking** spécifique à chaque langage (tree-sitter).

#### Côté génération
- **vLLM** local (le projet qu'on indexe !) au lieu de transformers
  → 5–10× plus rapide via PagedAttention.
- **Quantization** (bnb, gguf, exllamav2) pour faire tourner sur
  moins de VRAM.
- **Function calling / outputs structurés** : forcer le LLM à produire
  du JSON valide.
- **Streaming** : afficher la réponse au fur et à mesure (UX).

#### Côté évaluation
- **RAGAS** : framework d'évaluation RAG (faithfulness, answer relevancy,
  context precision/recall).
- **LLM-as-a-judge** : utiliser GPT-4 pour noter automatiquement les
  réponses.
- **Annotateurs humains** sur un échantillon.

### 12.2 Ressources externes

#### RAG
- *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*
  (Lewis et al., 2020) — le papier fondateur :
  <https://arxiv.org/abs/2005.11401>
- *Pinecone Learning Center* : <https://www.pinecone.io/learn/>
- *LangChain docs* : <https://python.langchain.com/docs/get_started>
- *LlamaIndex docs* : <https://docs.llamaindex.ai>

#### BM25 / IR
- Robertson & Zaragoza, *The Probabilistic Relevance Framework: BM25
  and Beyond* (2009).
- *Introduction to Information Retrieval* (Manning, Raghavan, Schütze,
  2008) — texte de référence : <https://nlp.stanford.edu/IR-book/>
- `bm25s` repo : <https://github.com/xhluca/bm25s>

#### Embeddings / Sentence-Transformers
- Site officiel : <https://www.sbert.net>
- Papier MiniLM : <https://arxiv.org/abs/2002.10957>
- MTEB leaderboard (benchmarks) : <https://huggingface.co/spaces/mteb/leaderboard>

#### LLM / transformers
- HuggingFace course : <https://huggingface.co/course>
- *The Illustrated Transformer* (Jay Alammar) :
  <https://jalammar.github.io/illustrated-transformer/>
- Qwen3 docs : <https://huggingface.co/Qwen/Qwen3-0.6B>

#### Python avancé
- *Fluent Python* (Luciano Ramalho, 2e édition) — best practices.
- *Effective Python* (Brett Slatkin).
- PEP index : <https://peps.python.org>.

#### Outils
- `uv` docs : <https://docs.astral.sh/uv/>
- `pytest` docs : <https://docs.pytest.org>
- Fire docs : <https://github.com/google/python-fire>

### 12.3 Exercices pour consolider

1. **Tests unitaires** : écrire pytest pour `tokenize`,
   `overlap_ratio`, `chunk_python`. Viser 100% coverage de `evaluate.py`
   et `tokenizer.py`.
2. **Métriques supplémentaires** : ajouter Precision@k, MRR (Mean
   Reciprocal Rank), NDCG.
3. **Re-ranking** : intégrer un cross-encoder après BM25, mesurer
   l'amélioration de Recall@5.
4. **Query expansion** : implémenter une ré-écriture de query naïve
   (LLM le génère, on cherche pour les 2 versions, on fusionne).
5. **CLI mode interactif** : `python -m student chat` qui boucle sur
   les questions de l'utilisateur en gardant un historique.
6. **Streaming output** : modifier `generate` pour streamer les tokens
   au fur et à mesure via `TextStreamer`.
7. **Profiling** : `python -m cProfile -o prof.out -m student index`
   puis analyser avec `snakeviz`.
8. **Comparaison embedders** : essayer `BAAI/bge-small-en-v1.5` à la
   place de MiniLM, comparer Recall@5.

### 12.4 Idées d'extensions

- **Web UI** : Streamlit ou Gradio pour interface graphique.
- **API REST** : exposer `search` et `answer` via FastAPI.
- **Indexation incrémentale** : ajouter de nouveaux fichiers sans
  reconstruire l'index.
- **Multi-index** : un index par langage (`.py`, `.md`, `.rst`) avec
  routage automatique selon la question.
- **Citation extraction** : forcer le LLM à citer `[Source 3]` dans sa
  réponse, parser ces citations en post-traitement.
- **Caching des réponses** : mémoïser `(question, k, mode) → answer`.
- **Tests d'évaluation continue** : un script qui re-évalue à chaque
  commit, graphique d'évolution Recall@5.
- **Support multi-langue** : extension à des dépôts non-anglophones.

### 12.5 Refactos possibles

- **Extraire un module `paths.py`** pour centraliser `DEFAULT_RAW_DIR`
  etc., et résoudre `relative_to` proprement (ne pas dépendre de cwd).
- **Logging** : remplacer `print` par un logger structuré.
- **Configuration YAML** : `config.yaml` pour les hyperparamètres
  (max_chunk_size, k, mode par défaut, etc.).
- **Plugin system pour chunking** : un registre `{ext: chunker_fn}`
  extensible.
- **Async generation** : avec `transformers` 4.40+ on peut paralléliser.
- **Type stubs** pour `bm25s` (pas de stubs officiels) pour activer
  `--strict` mypy.

---

## Annexe A — Sortie attendue

### Output `search`
```json
[
  {
    "file_path": "data/raw/vllm-0.10.1/docs/serving/openai_compatible_server.md",
    "first_character_index": 9867,
    "last_character_index": 10100
  },
  ...
]
```

### Output `search_dataset` (StudentSearchResults)
```json
{
  "search_results": [
    {
      "question_id": "17526382-...",
      "question_str": "What HTTP endpoint is used to dynamically load a LoRA adapter in vLLM?",
      "retrieved_sources": [
        {
          "file_path": "data/raw/vllm-0.10.1/docs/features/lora.md",
          "first_character_index": 4695,
          "last_character_index": 6100
        },
        ...
      ]
    },
    ...
  ],
  "k": 10
}
```

### Output `answer_dataset` (StudentSearchResultsAndAnswer)
```json
{
  "search_results": [
    {
      "question_id": "...",
      "question_str": "...",
      "retrieved_sources": [...],
      "answer": "The HTTP endpoint used to dynamically load a LoRA adapter in vLLM is `/v1/load_lora_adapter`."
    },
    ...
  ],
  "k": 10
}
```

### Output `evaluate` (stdout)
```
Evaluation Results
========================================
Questions evaluated: 100
Recall@ 1: 0.620
Recall@ 3: 0.790
Recall@ 5: 0.830
Recall@10: 0.850
```

---

## Annexe B — Performances mesurées

Sur machine de dev (CPU Intel, 16 Go RAM, GPU 3.6 Go VRAM) :

| Opération | Temps | Mémoire |
|---|---|---|
| `make install` (uv sync) | ~2 min (premier run, cache vide) | — |
| `student index` (BM25 only, 1969 fichiers, 21 530 chunks) | ~7 s | < 500 Mo |
| `student index --use_embeddings True` | ~3 min (CPU) ou ~30 s (GPU) | ~2 Go |
| `student search QUERY` (charge index + retrieve) | < 1 s | ~200 Mo |
| `student answer QUERY` (1er appel, charge Qwen3) | ~30 s | ~3 Go (fp16) |
| `student answer QUERY` (suivants, modèle en cache) | ~5 s GPU / ~30 s CPU | idem |
| `student search_dataset` (100 questions, k=10) | < 1 s | ~200 Mo |
| `student evaluate` | < 1 s | minimal |

Recall final (dataset public) :

| Dataset | Recall@1 | Recall@3 | Recall@5 | Recall@10 |
|---|---:|---:|---:|---:|
| docs | 0.62 | 0.79 | **0.83** ≥ 0.80 ✅ | 0.85 |
| code | 0.40 | 0.59 | **0.66** ≥ 0.50 ✅ | 0.72 |

---

## Annexe C — Liens internes au code

| Concept | Fichier:Ligne |
|---|---|
| Point d'entrée Fire | [src/student/cli.py:227](src/student/cli.py) |
| Dispatch chunker par extension | [src/student/chunking.py:168](src/student/chunking.py) |
| AST chunking Python | [src/student/chunking.py:54](src/student/chunking.py) |
| Header chunking Markdown | [src/student/chunking.py:121](src/student/chunking.py) |
| Tokenizer regex camelCase | [src/student/tokenizer.py:21](src/student/tokenizer.py) |
| Stopwords | [src/student/tokenizer.py:13](src/student/tokenizer.py) |
| BM25 index | [src/student/index.py:76](src/student/index.py) |
| Dense encoding | [src/student/index.py:217](src/student/index.py) |
| RRF fusion | [src/student/index.py:174](src/student/index.py) |
| `mode="auto"` switch | [src/student/index.py:204](src/student/index.py) |
| Système prompt LLM | [src/student/generator.py:11](src/student/generator.py) |
| Greedy generation | [src/student/generator.py:89](src/student/generator.py) |
| Recall@k formule | [src/student/evaluate.py:42](src/student/evaluate.py) |
| Modèle `MinimalSearchResults` | [src/student/models.py:39](src/student/models.py) |
| `relative_to="."` critique | [src/student/index.py:67](src/student/index.py) |
| Singleton generator | [src/student/generator.py:104](src/student/generator.py) |

---

---

## 13. Préparation à la défense 42

### 13.1 Le format de la défense

Une défense 42 dure typiquement **45 minutes – 1 heure**. Déroulé attendu :

1. **Démo (5–10 min)** : tu lances ton projet, fais tourner le pipeline
   complet (index → search → answer → evaluate), montres les Recall@5.
2. **Tour du code (15–20 min)** : l'évaluateur ouvre les fichiers et te
   demande d'expliquer ce qui se passe. Il peut pointer du doigt
   n'importe quelle fonction et dire « explique-moi ce que ça fait, et
   pourquoi tu l'as écrit comme ça ».
3. **Questions de fond (15–20 min)** : RAG, BM25, embeddings, LLM,
   architecture, choix techniques.
4. **Recode (5–10 min, optionnel mais possible cf. PDF IX.1)** : on te
   demande de modifier une partie du code en direct (renommer un champ,
   ajouter une option CLI, etc.). Si tu n'as pas écrit le code toi-même,
   c'est ici que ça se voit.

### 13.2 Tour du code à préparer (30 secondes par fichier)

Entraîne-toi à dérouler cette synthèse à voix haute, ouvert sur les
fichiers :

```
1. pyproject.toml      → "deps, build hatchling, mypy/flake8 configs"
2. Makefile            → "install/run/lint/clean/index, flags imposés"
3. .flake8             → "max-line-length=100, flake8 ignore pyproject"
4. README.md           → "format imposé par le sujet"
5. src/student/__init__.py / __main__.py
                       → "package + entry point python -m student"
6. models.py           → "modèles Pydantic, question_str important"
7. ingest.py           → "os.walk + filtres + relative_to crucial"
8. tokenizer.py        → "regex camelCase + stopwords"
9. chunking.py         → "dispatch par extension, AST pour Python"
10. index.py           → "BM25 + dense + RRF, save/load JSON+npy"
11. generator.py       → "singleton, lazy load Qwen3-0.6B, greedy"
12. evaluate.py        → "overlap_ratio, recall@k, 5% threshold"
13. cli.py             → "Fire, 6 commandes, helpers"
```

### 13.3 30 questions piège (avec réponses prêtes)

#### Sur le RAG en général

**Q1. Qu'est-ce que le RAG et pourquoi c'est utile ?**
> Retrieval-Augmented Generation. Au lieu de fine-tuner un LLM sur de
> nouvelles données (coûteux), on lui donne accès à une base de
> connaissances externe au moment de la question. Avantages : pas de
> re-training, knowledge cutoff dépassé, on peut citer les sources,
> hallucinations réduites.

**Q2. Quelle est la différence entre RAG et fine-tuning ?**
> Fine-tuning modifie les *poids* du modèle (coût élevé, données
> figées). RAG ne touche pas au modèle, ajoute juste du contexte à
> chaque inférence. RAG est mieux pour les connaissances qui changent
> souvent ou qui doivent être citées.

**Q3. Quelles sont les 4 étapes du RAG ?**
> Ingestion (lire les sources), Chunking (couper en morceaux), Indexation
> (construire une structure searchable), Retrieval+Generation (récupérer
> les bons morceaux + générer avec un LLM).

#### Sur BM25 et le retrieval

**Q4. C'est quoi BM25 en une phrase ?**
> Une fonction de scoring lexicale dérivée de TF-IDF, qui pondère chaque
> match terme/document par la fréquence (TF), la rareté du terme (IDF),
> avec saturation et normalisation de longueur.

**Q5. Quels paramètres a BM25 et que font-ils ?**
> `k1` (≈ 1.2) contrôle la **saturation de la TF** (à partir d'un
> certain seuil, plus d'occurrences n'aident plus). `b` (≈ 0.75) contrôle
> la **normalisation par la longueur du doc** (b=0 = pas de normalisation,
> b=1 = full normalisation).

**Q6. Pourquoi avoir choisi `bm25s` et pas `rank_bm25` ?**
> `bm25s` est 10–100× plus rapide grâce à son implémentation sparse en
> numpy/scipy. Sur le dépôt vLLM (~21k chunks), `rank_bm25` prendrait
> plusieurs minutes ; `bm25s` fait l'indexation en < 1 s.

**Q7. Quelle est la différence entre TF-IDF et BM25 ?**
> TF-IDF est un simple produit `TF * IDF`. BM25 ajoute la **saturation
> de TF** (la 50e occurrence d'un terme n'aide pas autant que la 2e) et
> la **normalisation par longueur du doc** (un doc court mais ciblé est
> favorisé sur un doc long et dilué).

**Q8. Pourquoi le tokenizer split camelCase ?**
> Le code regorge d'identifiants type `OpenAIServer`, `get_user_name`.
> Sans split, une question « comment configurer le server » ne matche
> pas `OpenAIServer.py`. En splittant, on transforme `OpenAIServer` en
> `["open", "ai", "server"]` qui matche la query.

**Q9. Que fait `relative_to="."` et pourquoi c'est critique ?**
> Détermine la racine pour les `file_path` stockés dans les chunks. Avec
> `"."` (cwd = racine du projet), on a des paths du genre
> `data/raw/vllm-0.10.1/docs/x.md`. Les datasets ground-truth utilisent
> ce même format. Si on mettait `relative_to=repo_root`, les paths
> seraient `docs/x.md` et **aucun** match avec les datasets → Recall = 0%.

#### Sur les embeddings et l'hybrid

**Q10. C'est quoi un embedding dense ?**
> Un vecteur de N floats (384 pour MiniLM, 768 pour MPNet) qui
> représente le sens d'un texte. Deux textes proches en sens →
> vecteurs proches (similarité cosinus élevée). Permet de matcher
> sémantiquement, sans nécessiter de mots-clés en commun.

**Q11. Comment se calcule la similarité cosinus en pratique ?**
> `cos(u, v) = (u · v) / (||u|| * ||v||)`. Si on **normalise** les
> vecteurs (`||v|| = 1`), c'est juste le produit scalaire. On
> `normalize_embeddings=True` à l'encodage, et après c'est un simple
> matmul `embeddings @ query_vector`.

**Q12. C'est quoi RRF, et pourquoi pas une moyenne pondérée ?**
> Reciprocal Rank Fusion : `score(doc) = Σ 1 / (k + rank_method(doc))`,
> avec k=60 par convention. Avantages vs moyenne pondérée :
> - **Pas d'hyperparamètre** à régler.
> - **Robuste aux échelles différentes** des scores (BM25 sort des
>   valeurs > 1, cosinus sort dans [-1, 1]).
> - **Pas besoin de normaliser** les scores au préalable.

**Q13. Pourquoi élargir le pool à 4×k dans `search_hybrid` ?**
> Pour donner plus de chances à des documents bien classés dans une
> méthode mais hors top-k de l'autre. Sans pool élargi, un doc 11e en
> BM25 mais 2e en dense serait perdu.

#### Sur le chunking

**Q14. Pourquoi pas juste un sliding window de taille fixe ?**
> Ça couperait au milieu des fonctions/sections, ce qui dilue
> l'information. AST chunking garde une fonction/classe entière par
> chunk → meilleur signal pour BM25 (tous les tokens liés ensemble) et
> meilleure réponse du LLM (contexte cohérent).

**Q15. Que se passe-t-il si un fichier Python n'est pas parsable ?**
> `ast.parse()` lève `SyntaxError` → on tombe dans le fallback
> `chunk_text` (sliding window). Cas réel : fichier avec syntaxe
> Python 2 ou des marqueurs de merge git non résolus.

**Q16. Comment vous gérez les fichiers Markdown ?**
> Découpage par titres ATX (`#`, `##`, …). Chaque section = un chunk.
> Si une section dépasse `max_chunk_size`, on sub-split en sliding
> window avec 10% d'overlap.

**Q17. Le `max_chunk_size` est de 2000 caractères. Pourquoi ?**
> Imposé par le sujet (note V.4). Compromis entre :
> - Trop petit : on perd le contexte autour d'un identifiant.
> - Trop grand : on dilue la pertinence, le top-k devient grossier.
> 2000 chars ≈ 500–700 tokens, soit la taille d'une fonction moyenne.

#### Sur le LLM et la génération

**Q18. Pourquoi Qwen3-0.6B et pas un modèle plus gros ?**
> Imposé par le sujet. 600M paramètres, ~1.2 Go en fp16, tient sur un
> GPU modeste (3 Go suffisent) et même sur CPU avec patience. Suffisant
> pour répondre à des questions techniques quand le contexte est bien
> fourni par le retrieval.

**Q19. Pourquoi `do_sample=False, temperature=0` ?**
> Génération **greedy** (toujours le token le plus probable). Avantage :
> reproductibilité — même prompt → même sortie, donc les tests sont
> déterministes et la défense ne montre pas une réponse différente à
> chaque run.

**Q20. Pourquoi `enable_thinking=False` ?**
> Qwen3 a un mode « thinking » qui produit du texte de réflexion
> `<think>...</think>` avant la réponse. C'est lourd (consomme du
> contexte) et la sortie devient moins prédictible. On désactive pour
> aller droit au but.

**Q21. Comment le LLM est-il « grounded » sur les sources ?**
> Trois mécanismes :
> 1. **System prompt** : « Answer using ONLY the provided context ».
> 2. **Format de contexte** : sources numérotées et préfixées par leur
>    file_path, ce qui encourage la citation.
> 3. **Greedy decoding** : moins de créativité, plus de fidélité.

**Q22. Et si la réponse n'est pas dans le contexte ?**
> Le system prompt dit « If the answer is not present, say so ». En
> pratique, les petits modèles comme Qwen3-0.6B ne respectent pas
> toujours parfaitement cette consigne — c'est une limite connue.

#### Sur l'archi et le code

**Q23. Pourquoi un singleton pour `AnswerGenerator` ?**
> Charger Qwen3 prend ~5 s (fp16) et 1.2 Go de RAM/VRAM. On veut
> mutualiser ce coût sur toutes les questions d'un batch (`answer_dataset`).
> Le singleton garde l'instance entre les appels. Limitation : pas
> thread-safe, mais le CLI est mono-thread donc OK.

**Q24. Pourquoi `_get_embedder` est lazy alors que les embeddings
sont déjà chargés ?**
> Les embeddings du corpus (`dense_embeddings`) sont sur disque,
> chargés par `load()`. Mais pour encoder la *query* on a besoin du
> modèle `SentenceTransformer` lui-même, qui pèse 90 Mo et prend 1–2 s
> à charger. On le diffère au premier `search_dense`.

**Q25. Pourquoi `Pydantic` pour les modèles et `dataclass` pour `Chunk` ?**
> Pydantic = validation à la frontière (entrée/sortie JSON). Coût
> non-négligeable. `Chunk` est purement interne, on le construit nous-mêmes
> à partir de code qu'on contrôle → pas besoin de validation, dataclass
> suffit et c'est plus rapide.

**Q26. Comment l'index est-il persisté ?**
> 4 artefacts dans `data/processed/` :
> - `chunks.json` : liste de dicts sérialisés (path + offsets + text).
> - `bm25_index/` : format propre à `bm25s` (sparse matrix + vocab).
> - `meta.json` : métadonnées (embedder_name, n_chunks).
> - `dense_index/embeddings.npy` : array numpy float32 (N × 384), si
>   bonus activé.

**Q27. Comment vous testez ?**
> ⚠️ **Honnêteté** : pas de tests unitaires formels. Validation par :
> (1) `make lint` (flake8 + mypy passent sans erreur), (2) pipeline
> end-to-end (Recall@5 ≥ 80% docs / ≥ 50% code), (3) moulinette officielle.
> Améliorations possibles : pytest sur tokenizer, chunking, evaluate.
> *Ne pas mentir là-dessus à l'évaluateur*.

#### Sur les choix d'architecture

**Q28. Et si on n'avait pas le budget de 5 min d'indexation, qu'est-ce
qui changerait ?**
> Il faudrait :
> - Indexation incrémentale (ne ré-indexer que les fichiers modifiés).
> - Plusieurs index parallèles par sous-dossier.
> - Stocker les embeddings dans une vector DB (chromadb, faiss).
> - Pré-tokeniser et persister les tokens (déjà le cas via `bm25s`).

**Q29. Comment scaler à un dépôt 100× plus grand (e.g. tout PyPI) ?**
> - Index distribué (sharded BM25, faiss ivf pour les denses).
> - Re-ranking en deux étapes : BM25 grossier sur le full corpus, puis
>   cross-encoder sur les top-100.
> - Caching agressif des queries fréquentes.
> - Approximate Nearest Neighbors (HNSW) au lieu du matmul brute pour
>   les denses.

**Q30. Si je vous demande d'ajouter un nouveau type de chunker (e.g.
`.json`), comment faites-vous ?**
> Trois étapes :
> 1. Ajouter une fonction `chunk_json(file_path, text, max_size)` dans
>    `chunking.py`.
> 2. Ajouter le dispatch dans `chunk_file` :
>    ```python
>    if lower.endswith(".json"):
>        return chunk_json(...)
>    ```
> 3. Ajouter `.json` à `ALLOWED_EXTENSIONS` dans `ingest.py`.
> Tester sur un fichier JSON exemple. Refaire `student index` pour
> reconstruire avec la nouvelle stratégie.

### 13.4 Questions de recode probables (PDF IX.1)

Le sujet prévient qu'on peut être demandé une modification mineure en
direct. Préparation possible :

**Recode A : « Ajoute un flag `--min_score` à `search` qui filtre les
résultats sous un seuil ».**
> Modifier `KnowledgeBase.search` pour retourner aussi les scores,
> propager le param dans `CLI.search`, filtrer.

**Recode B : « Change le tokenizer pour qu'il garde les mots d'une
seule lettre (pour matcher des variables comme `x` ou `i`) ».**
> Dans `tokenizer.py:36`, remplacer `if len(sub_lower) < 2` par `< 1`.
> Re-indexer.

**Recode C : « Modifie le format JSON de `search` pour qu'il inclue le
score BM25 de chaque chunk ».**
> Ajouter un champ `score: float` au DTO de sortie, propager
> depuis `search_bm25` qui retourne déjà les scores.

**Recode D : « Évite de réindexer si `data/processed/` existe déjà —
ajoute un flag `--force` pour ré-indexer quand même ».**
> Dans `CLI.index`, vérifier `os.path.exists(save_directory)` et `force`,
> retourner tôt si déjà là.

**Recode E : « Ajoute une commande `stats` qui affiche le nombre de
chunks, la taille moyenne, et la distribution par extension ».**
> Méthode `stats(self, index_directory)` dans `CLI`, charge la KB,
> agrège.

### 13.5 Les pièges classiques en défense 42

1. **Ne pas savoir expliquer une ligne de son code.** Si tu as utilisé
   AI : *tu dois comprendre chaque ligne*. Sinon, score zéro
   automatique (« can't justify → fail », cf. AI Instructions du PDF).

2. **Sur-vendre les bonus.** Si tu dis « j'ai fait le bonus X » et
   qu'on te demande une démo, ça doit marcher (cf. chap VIII : « not
   just described in the README »). Vérifie que tes flags
   `--use_embeddings True` fonctionnent.

3. **Ne pas connaître ses limites.** Un bon candidat reconnaît : « Pas
   de tests unitaires, on aurait dû en faire ». Mauvais candidat
   prétend que c'est testé partout.

4. **Hallucination dans la démo.** Ne montre que des questions dont
   tu sais qu'elles marchent bien. Évite « comment optimiser CUDA dans
   vLLM ? » si tes 5 dernières runs sur cette question donnaient des
   réponses bullshit.

5. **Oublier le `relative_to`.** Si on te demande pourquoi les paths
   sont comme ça, tu dois pouvoir expliquer (cf. Q9).

6. **Confondre BM25 et embeddings.** Sache dire en 30 s la différence :
   BM25 = lexical, basé sur des mots-clés exacts (tokenisés). Embeddings
   = sémantique, basé sur le sens. Hybrid combine les deux.

7. **Ne pas savoir où est définie une commande.** Tu dois pouvoir
   pointer `cli.py:80–100` pour `search`, etc. Ouvre les bons fichiers
   *avant* la défense.

### 13.6 Démo type (10 minutes)

```bash
# Préparation (avant l'évaluateur)
source .venv/bin/activate
rm -rf data/processed   # pour montrer la build complète

# Etape 1 : show structure
ls src/student/

# Etape 2 : lint OK
make lint

# Etape 3 : indexation
time uv run python -m student index --max_chunk_size 2000
# → "Ingestion complete! 21530 chunks created"

# Etape 4 : search single query (lexical)
uv run python -m student search "How to load a LoRA adapter?" --k 5
# → JSON avec des paths cohérents

# Etape 5 : answer single query
uv run python -m student answer "How to load a LoRA adapter?" --k 3
# → réponse en anglais, citant /v1/load_lora_adapter

# Etape 6 : pipeline batch + evaluate
uv run python -m student search_dataset \
    --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json \
    --k 10 --save_directory data/output/search_results

uv run python -m student evaluate \
    --student_results_path data/output/search_results/dataset_docs_public.json \
    --dataset_path data/datasets/AnsweredQuestions/dataset_docs_public.json
# → Recall@5: 0.84

# Etape 7 (bonus) : hybrid
uv run python -m student index --use_embeddings True
uv run python -m student search "..." --mode hybrid
```

### 13.7 Auto-quiz (à faire fermé)

Pose-toi ces questions à voix haute sans rouvrir le doc :

1. Pourquoi `question_str` et pas `question` ?
2. Que produit le tokenizer sur `getOpenAIServer` ?
3. C'est quoi RRF, formule + intuition ?
4. Que retourne `np.argpartition(-x, n)` ?
5. Quelle est la différence entre `@classmethod` et `@staticmethod` ?
6. Pourquoi `relative_to="."` ?
7. Que se passe-t-il si `ast.parse` échoue ?
8. Comment je sais qu'un chunk dépasse `max_chunk_size` ? Que fait-on ?
9. Quels formats les chunks sont persistés sur disque ?
10. Quel est le système prompt et pourquoi cette formulation ?

Si tu sèches sur plus de 3, relis le LEARN.md.

### 13.8 Plan de révision sur 2 jours

**J-2 (avant la défense)**
- 30 min : relire le README + sujet PDF.
- 2 h : lire LEARN.md sections 4 (par fichier) + 5 (concepts).
- 1 h : faire tourner la démo bout-en-bout, mesurer les temps.
- 30 min : lire les 30 questions de 13.3.

**J-1**
- 1 h : refaire la démo, deux fois, en chronométrant à 10 min.
- 1 h : se faire interroger par un pair sur les questions 13.3.
- 30 min : auto-quiz 13.7.
- 30 min : vérifier que la moulinette passe (binaire et threshold).

**Jour J**
- Activer le venv.
- Vérifier `make lint` passe encore.
- Préparer `data/processed/` (option : pré-indexer ou démontrer
  l'indexation, à voir avec l'évaluateur).
- Ouvrir les fichiers `cli.py`, `index.py`, `chunking.py` dans l'IDE.

---

*Fin du document. Bonne lecture, et bon courage pour la défense !*
