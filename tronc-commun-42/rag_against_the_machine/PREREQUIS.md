# 📚 Prérequis pour le projet "RAG against the machine"

Ce document liste **tout** ce que tu dois maîtriser (ou au moins connaître) avant
de te lancer dans le code. Si un point est flou, lis-le et fais une petite
expérience avant de continuer — ça t'évitera de perdre des heures.

---

## 1. Python (niveau intermédiaire+)

### 1.1 Bases solides
- **Variables, types, conditions, boucles, fonctions** — évident, mais tu vas
  écrire beaucoup de code, autant être à l'aise.
- **Compréhensions** (`[x for x in ...]`, `{k: v for ...}`) — utilisées partout
  dans `chunking.py`, `evaluate.py`, `cli.py`.
- **f-strings** : `f"Hello {name}"`.
- **`with` (context managers)** pour ouvrir des fichiers proprement :
  ```python
  with open(path, "r", encoding="utf-8") as fh:
      data = fh.read()
  ```
- **try / except** — obligatoire dans le sujet (gestion d'erreurs gracieuse).

### 1.2 Notions plus avancées
- **Classes & héritage**
  - `class Foo(Bar):` — `AnsweredQuestion` hérite de `UnansweredQuestion`.
- **`@dataclass`** — utilisé pour `Chunk` et `EvalReport` (génère
  automatiquement `__init__`, `__repr__`).
- **Typing** — annotations de type, *obligatoire* dans le sujet (mypy passe
  sans erreur) :
  ```python
  def foo(x: int, names: list[str]) -> dict[str, int]:
      ...
  ```
  - `List[X]`, `Dict[K, V]`, `Tuple[X, Y]`, `Optional[X]` (= `X | None`),
    `Union[A, B]` (= `A | B`).
  - `from __future__ import annotations` en haut de fichier autorise la
    syntaxe `X | None` même en Python 3.10.
- **Generators et `yield`** — `iter_files()` dans `ingest.py` `yield`
  chaque path au lieu de tout retourner en liste.
- **`pathlib` / `os.path`** : manipulation de chemins de fichiers.
- **JSON** : `json.load`, `json.dump`, `json.dumps` (pour I/O datasets).
- **Modules et packages** : pourquoi un dossier `student/` avec
  `__init__.py` est un *package*, et pourquoi `__main__.py` est le point
  d'entrée quand on fait `python -m student`.
- **Imports relatifs** : `from .chunking import Chunk`.

### 1.3 Outils Python
- **`uv`** : gestionnaire de paquets ultra-rapide (remplace pip+venv). Tu
  *dois* l'utiliser pour ce projet.
  - `uv venv` crée un environnement virtuel `.venv/`.
  - `uv sync` installe ce qui est dans `pyproject.toml`.
  - `uv add <package>` ajoute une dépendance.
  - `uv run python ...` lance Python dans le venv.
- **`flake8`** : linter de style PEP8. Le sujet impose qu'il passe.
- **`mypy`** : vérificateur de types statiques. Le sujet impose qu'il passe.
- **`pytest`** : framework de tests (non obligatoire mais recommandé).

---

## 2. Librairies tierces utilisées

| Lib | À quoi ça sert chez nous | À connaître |
|---|---|---|
| **`pydantic`** | Modèles de données validés (`BaseModel`) | `Field`, `model_validate_json`, `model_dump_json` |
| **`fire`** | Transforme une classe Python en CLI auto | Tu écris une méthode `def search(...)`, Fire la rend appelable depuis le shell |
| **`tqdm`** | Barres de progression | `for x in tqdm(iterable, desc="...")` |
| **`bm25s`** | Index BM25 ultra-rapide | `bm25s.BM25()`, `.index(tokens)`, `.retrieve(query, k=...)`, `.save()`, `.load()` |
| **`numpy`** | Arrays numériques, multiplications matricielles | `np.asarray`, `np.argpartition`, `np.argsort` |
| **`sentence-transformers`** | Embeddings denses (bonus) | `SentenceTransformer(name).encode(texts)` |
| **`transformers`** (HuggingFace) | Charger Qwen3-0.6B | `AutoTokenizer`, `AutoModelForCausalLM`, `.generate()` |
| **`torch`** | Backend tenseurs (utilisé par transformers) | `torch.no_grad()`, `torch.float16`, `torch.cuda.is_available()` |

---

## 3. Notions théoriques **RAG**

### 3.1 Vue d'ensemble
**RAG** = Retrieval Augmented Generation. Au lieu d'apprendre un modèle sur
de nouvelles données (long, cher), on lui donne accès à une **base de
connaissances externe** au moment de la question.

Pipeline en 4 étapes :
1. **Ingestion** : lire tous les fichiers de la base.
2. **Chunking** : couper les fichiers en morceaux de taille raisonnable.
3. **Indexation** : construire une structure qui permet de *retrouver*
   rapidement les bons morceaux.
4. **Retrieval + Generation** : à la question, trouver les chunks
   pertinents, puis demander à un LLM de répondre en s'appuyant *uniquement*
   sur ce contexte.

### 3.2 Chunking
- Un chunk = un bout de texte (ici max 2000 caractères).
- **Pourquoi chunker ?** Parce que :
  - Le LLM a une fenêtre de contexte limitée.
  - On veut retrouver des passages précis (pas un fichier entier).
- **Stratégies** :
  - **Naïve** : couper tous les N caractères.
  - **Sémantique** : couper aux frontières logiques (fonction Python,
    section Markdown, paragraphe).
  - **Avec overlap** : faire chevaucher les chunks pour ne pas couper
    une phrase au milieu.

### 3.3 BM25 (l'algo de retrieval qu'on utilise)
- BM25 = Best Matching 25, dérivé du TF-IDF.
- Pour chaque chunk il calcule un *score* face à la requête :
  - **TF** (term frequency) : à quelle fréquence les mots de la requête
    apparaissent dans le chunk.
  - **IDF** (inverse document frequency) : pénalise les mots trop
    communs (« the », « and »).
  - **Normalisation de longueur** : un chunk court mais ciblé est
    favorisé par rapport à un chunk long et dilué.
- C'est **lexical** : il faut que les *mots* matchent. D'où l'importance
  d'un bon tokenizer (séparer `getUserName` en `get user name`).

### 3.4 Embeddings denses (bonus)
- Un embedding = un vecteur de 384 ou 768 nombres flottants qui résume
  le sens d'un texte.
- Deux textes proches en sens → vecteurs proches (similarité cosinus).
- Permet de matcher *sémantiquement* : `« comment configurer le serveur »`
  matchera `« server setup instructions »` même sans mots communs.
- Modèle utilisé ici : `sentence-transformers/all-MiniLM-L6-v2` (petit, rapide).

### 3.5 Hybrid retrieval (bonus)
Combiner BM25 (lexical) + dense (sémantique) → meilleurs résultats. La
fusion se fait par **Reciprocal Rank Fusion (RRF)** :
```
score(doc) = Σ 1 / (k + rank_dans_chaque_méthode)
```
Simple, sans hyperparamètres à régler, et robuste.

### 3.6 Évaluation : Recall@k
- Pour chaque question on a une *vérité terrain* : la liste des sources
  correctes (avec leurs offsets).
- On retient les **k** chunks les mieux classés par notre retriever.
- Une source ground-truth est **trouvée** si au moins **5 %** de ses
  caractères sont couverts par un des k chunks (même `file_path` requis).
- `Recall@k = nb_sources_trouvées / nb_sources_totales`.
- Le sujet exige **Recall@5 ≥ 80%** sur docs, **≥ 50%** sur code.

---

## 4. LLM et génération (Qwen3-0.6B)

- **LLM** = Large Language Model. `Qwen3-0.6B` = modèle de 600 millions
  de paramètres, raisonnablement léger (~1.2 Go en float16).
- **Tokenizer** : convertit le texte en *tokens* (entiers) que le modèle
  consomme.
- **Chat template** : Qwen3 attend un format de messages
  `[{"role": "system", "content": ...}, {"role": "user", ...}]`. La
  méthode `apply_chat_template()` formate ça correctement pour le modèle.
- **Generation parameters** :
  - `max_new_tokens` : limite de longueur de la réponse.
  - `do_sample=False` + `temperature=0` : génération déterministe
    (toujours la même réponse à même prompt).
- **GPU vs CPU** : on détecte `torch.cuda.is_available()`. Sans GPU,
  la génération sera lente mais fonctionnelle (Qwen3-0.6B reste tenable).

---

## 5. Outils système

### 5.1 Shell de base
- `cd`, `ls`, `mkdir -p`, `mv`, `cp`, `rm`, `find`.
- Redirections `>`, `>>`, pipes `|`.
- Variables d'environnement (`export VAR=...`).

### 5.2 Git
- `git init`, `git add`, `git commit -m "..."`, `git push`.
- Tu dois soumettre ton repo Git avec `src/`, `pyproject.toml`,
  `uv.lock`, `README.md`, `Makefile` — **sans** les datasets ni les
  weights de modèle.

### 5.3 Makefile
- Cibles : `make install`, `make run`, `make lint`, `make clean`.
- Syntaxe : indentation par **tabulations** (pas des espaces).

---

## 6. Récapitulatif : ordre de lecture conseillé

Si tu pars de zéro :

1. ✅ Python orienté objet + typing
2. ✅ `uv`, `pyproject.toml`, venv
3. ✅ JSON I/O et pydantic (`BaseModel`)
4. ✅ Pourquoi du RAG ? Lis la section III.5 du sujet PDF.
5. ✅ Chunking : pourquoi, comment.
6. ✅ BM25 : ce que ça calcule, à quoi ça sert (lecture rapide
   d'un tuto suffit).
7. ✅ HuggingFace `transformers` : `AutoTokenizer`, `AutoModelForCausalLM`
   et `.generate()`.
8. ✅ Recall@k : la formule, pourquoi on évalue comme ça.
9. (Bonus) Embeddings + similarité cosinus + RRF.

Une fois ces points compris, le code du projet devient une simple **mise
en musique** — passe au fichier `CODE_EXPLAINED.md` pour la lecture pas à
pas.
